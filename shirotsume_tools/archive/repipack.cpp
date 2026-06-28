#include "repipack.h"

#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <cstring>

static const uint8_t SIG[8] = {'R', 'e', 'p', 'i', 'P', 'a', 'c', 'k'};
static const uint32_t VERSION = 2;
static const uint32_t HEADER_KEY = 0x837FC07A;
static const uint32_t FILE_KEY = 0xF517AA26;

static void decrypt_words(uint32_t *buf, size_t word_count, uint32_t key) {
    for (size_t i = 0; i < word_count; i++) {
        uint32_t value = buf[i] ^ key;
        buf[i] = value;
        uint32_t rotated = (((value << 16) | (value >> 16)) & 0xFFFFFFFFU) ^ 0x98FCDBA2U;
        key = (key + rotated) & 0xFFFFFFFFU;
    }
}

static void file_decrypt_words(uint32_t *buf, size_t word_count) {
    for (size_t i = 0; i < word_count; i++) {
        uint32_t value = buf[i];
        value = (value << 6) ^ (((value << 6) ^ ((value ^ 0x9B9B9B9BU) >> 2)) & 0x3F3F3F3FU);
        buf[i] = value & 0xFFFFFFFFU;
    }
}

static rp_error_t decompress(const uint8_t *comp, size_t comp_size,
                             uint8_t *out, size_t size) {
    uint8_t cache[0x1000];
    std::memset(cache, 0, sizeof(cache));
    uint16_t cache_ptr = 0xFEE;
    size_t cursor = 0;
    uint8_t read_mask = 0;
    uint8_t mask = 0;
    size_t out_len = 0;

    while (out_len < size) {
        if (read_mask == 0) {
            if (cursor >= comp_size) return RP_ERR_DECOMPRESSION;
            read_mask = 0xFF;
            mask = comp[cursor++];
        }
        if (mask & 1) {
            if (cursor >= comp_size) return RP_ERR_DECOMPRESSION;
            uint8_t value = comp[cursor++];
            out[out_len++] = value;
            cache[cache_ptr] = value;
            cache_ptr = (cache_ptr + 1) & 0xFFF;
        } else {
            if (cursor + 1 >= comp_size) return RP_ERR_DECOMPRESSION;
            uint8_t byte_0 = comp[cursor++];
            uint8_t byte_1 = comp[cursor++];
            uint16_t offset = ((byte_1 & 0xF0) << 4) | byte_0;
            uint8_t length = (byte_1 & 0x0F) + 3;
            for (uint8_t i = 0; i < length; i++) {
                uint8_t value = cache[(offset + i) & 0xFFF];
                out[out_len++] = value;
                cache[cache_ptr] = value;
                cache_ptr = (cache_ptr + 1) & 0xFFF;
                if (out_len == size) break;
            }
        }
        read_mask >>= 1;
        mask >>= 1;
    }
    return RP_OK;
}

static rp_error_t decrypt_body_in_place(uint8_t *buf, size_t comp_size,
                                        uint32_t size, uint8_t crypt_type) {
    if (comp_size % 4 != 0) {
        // The original format encrypts in whole dwords; trailing bytes are plaintext.
    }
    size_t word_count = comp_size / 4;
    if (crypt_type == 1) {
        decrypt_words(reinterpret_cast<uint32_t*>(buf), word_count, FILE_KEY);
    } else if (crypt_type == 2) {
        file_decrypt_words(reinterpret_cast<uint32_t*>(buf), word_count);
    }
    if (comp_size != size) {
        uint8_t *decompressed = static_cast<uint8_t*>(std::malloc(size));
        if (!decompressed) return RP_ERR_ALLOC;
        rp_error_t err = decompress(buf, comp_size, decompressed, size);
        if (err != RP_OK) {
            std::free(decompressed);
            return err;
        }
        std::memcpy(buf, decompressed, size);
        std::free(decompressed);
    }
    return RP_OK;
}

rp_error_t rp_decode_body(uint8_t *buf, size_t comp_size, uint32_t size, uint8_t crypt_type) {
    return decrypt_body_in_place(buf, comp_size, size, crypt_type);
}

void rp_free(void *p) {
    std::free(p);
}

rp_error_t rp_decode_header(const uint8_t *in, size_t in_len,
                            uint8_t **header, size_t *header_len,
                            rp_entry_t **entries, size_t *entry_count) {
    if (in_len < 16) return RP_ERR_SHORT_READ;
    if (std::memcmp(in, SIG, 8) != 0) return RP_ERR_INVALID_SIGNATURE;

    uint32_t version = *reinterpret_cast<const uint32_t*>(in + 8);
    if (version != VERSION) return RP_ERR_UNSUPPORTED_VERSION;

    uint32_t header_size = *reinterpret_cast<const uint32_t*>(in + 12);
    size_t table_offset = 16 + header_size;
    if (in_len < table_offset + 4) return RP_ERR_SHORT_READ;

    *header = static_cast<uint8_t*>(std::malloc(header_size));
    if (!*header) return RP_ERR_ALLOC;
    std::memcpy(*header, in + 16, header_size);
    decrypt_words(reinterpret_cast<uint32_t*>(*header), header_size / 4, HEADER_KEY);
    *header_len = header_size;

    uint32_t count = *reinterpret_cast<const uint32_t*>(in + table_offset);
    *entry_count = count;
    *entries = static_cast<rp_entry_t*>(std::malloc(count * sizeof(rp_entry_t)));
    if (!*entries) {
        std::free(*header);
        return RP_ERR_ALLOC;
    }

    size_t table_size = count * 80;
    if (in_len < table_offset + 4 + table_size) {
        std::free(*header);
        std::free(*entries);
        return RP_ERR_SHORT_READ;
    }

    uint8_t *raw_table = static_cast<uint8_t*>(std::malloc(table_size));
    if (!raw_table) {
        std::free(*header);
        std::free(*entries);
        return RP_ERR_ALLOC;
    }
    std::memcpy(raw_table, in + table_offset + 4, table_size);
    decrypt_words(reinterpret_cast<uint32_t*>(raw_table), table_size / 4, FILE_KEY);

    for (size_t i = 0; i < count; i++) {
        uint8_t *p = raw_table + i * 80;
        rp_entry_t *e = &(*entries)[i];
        std::memcpy(e->name, p, 64);
        e->offset = *reinterpret_cast<uint32_t*>(p + 64);
        e->size = *reinterpret_cast<uint32_t*>(p + 68);
        e->comp_size = *reinterpret_cast<uint32_t*>(p + 72);
        e->crypt_type = p[76];
    }
    std::free(raw_table);
    return RP_OK;
}
