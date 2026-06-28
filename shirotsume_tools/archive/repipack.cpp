#include "repipack.h"

#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <vector>

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

static void crypt_words(uint32_t *buf, size_t word_count, uint32_t key) {
    for (size_t i = 0; i < word_count; i++) {
        uint32_t value = buf[i];
        buf[i] = value ^ key;
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

static rp_error_t compress(const uint8_t *in, size_t in_len,
                           uint8_t **out, size_t *out_len) {
    if (in_len == 0) {
        *out = nullptr;
        *out_len = 0;
        return RP_OK;
    }

    uint8_t cache[0x1000];
    std::memset(cache, 0, sizeof(cache));
    uint16_t cache_ptr = 0xFEE;

    std::vector<uint8_t> temp;
    temp.reserve(in_len + in_len / 8 + 16);

    size_t i = 0;
    while (i < in_len) {
        size_t flag_pos = temp.size();
        temp.push_back(0);
        uint8_t flag = 0;

        for (int bit = 0; bit < 8 && i < in_len; ++bit) {
            uint16_t best_offset = 0;
            uint8_t best_len = 0;
            const uint8_t max_len = 18;
            size_t remaining = in_len - i;

            for (uint16_t off = 0; off < 0x1000; ++off) {
                uint8_t len = 0;
                size_t limit = std::min<size_t>(max_len, remaining);
                while (len < limit && cache[(off + len) & 0xFFF] == in[i + len]) {
                    ++len;
                }
                if (len > best_len) {
                    best_len = len;
                    best_offset = off;
                }
            }

            if (best_len >= 3) {
                uint8_t byte_0 = best_offset & 0xFF;
                uint8_t byte_1 = ((best_offset >> 4) & 0xF0) | ((best_len - 3) & 0x0F);
                temp.push_back(byte_0);
                temp.push_back(byte_1);
                for (uint8_t k = 0; k < best_len; ++k) {
                    uint8_t v = cache[(best_offset + k) & 0xFFF];
                    cache[cache_ptr] = v;
                    cache_ptr = (cache_ptr + 1) & 0xFFF;
                }
                i += best_len;
            } else {
                uint8_t v = in[i];
                temp.push_back(v);
                cache[cache_ptr] = v;
                cache_ptr = (cache_ptr + 1) & 0xFFF;
                flag |= static_cast<uint8_t>(1 << bit);
                ++i;
            }
        }

        temp[flag_pos] = flag;
    }

    *out = static_cast<uint8_t*>(std::malloc(temp.size()));
    if (!*out) return RP_ERR_ALLOC;
    std::memcpy(*out, temp.data(), temp.size());
    *out_len = temp.size();
    return RP_OK;
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
    if (count == 0) {
        *entries = nullptr;
        return RP_OK;
    }
    if (count > SIZE_MAX / 80) return RP_ERR_SHORT_READ;
    if (count > SIZE_MAX / sizeof(rp_entry_t)) return RP_ERR_ALLOC;

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

rp_error_t rp_encode_body(const uint8_t *in, size_t in_len,
                          uint8_t **out, size_t *out_len,
                          uint8_t *crypt_type, int do_compress) {
    uint8_t *buf = nullptr;
    size_t buf_len = 0;

    if (do_compress && in_len > 0) {
        rp_error_t err = compress(in, in_len, &buf, &buf_len);
        if (err != RP_OK) return err;
    } else {
        buf = static_cast<uint8_t*>(std::malloc(in_len));
        if (in_len > 0 && !buf) return RP_ERR_ALLOC;
        if (in_len > 0) std::memcpy(buf, in, in_len);
        buf_len = in_len;
    }

    if (buf_len > 0) {
        crypt_words(reinterpret_cast<uint32_t*>(buf), buf_len / 4, FILE_KEY);
    }
    *out = buf;
    *out_len = buf_len;
    *crypt_type = 1;
    return RP_OK;
}

rp_error_t rp_encode_header(uint8_t **out, size_t *out_len,
                            const uint8_t *header, size_t header_len,
                            const rp_entry_t *entries, size_t entry_count) {
    if (entry_count > SIZE_MAX / 80) return RP_ERR_ALLOC;

    size_t table_size = entry_count * 80;
    size_t total = 8 + 4 + 4 + header_len + 4 + table_size;
    if (total < table_size) return RP_ERR_ALLOC;

    *out = static_cast<uint8_t*>(std::malloc(total));
    if (!*out) return RP_ERR_ALLOC;

    uint8_t *p = *out;
    std::memcpy(p, SIG, 8);
    p += 8;
    *reinterpret_cast<uint32_t*>(p) = VERSION;
    p += 4;
    *reinterpret_cast<uint32_t*>(p) = static_cast<uint32_t>(header_len);
    p += 4;

    if (header_len > 0) {
        uint8_t *encrypted_header = static_cast<uint8_t*>(std::malloc(header_len));
        if (!encrypted_header) {
            std::free(*out);
            return RP_ERR_ALLOC;
        }
        std::memcpy(encrypted_header, header, header_len);
        crypt_words(reinterpret_cast<uint32_t*>(encrypted_header), header_len / 4, HEADER_KEY);
        std::memcpy(p, encrypted_header, header_len);
        std::free(encrypted_header);
    }
    p += header_len;

    *reinterpret_cast<uint32_t*>(p) = static_cast<uint32_t>(entry_count);
    p += 4;

    uint8_t *raw_table = static_cast<uint8_t*>(std::malloc(table_size));
    if (!raw_table) {
        std::free(*out);
        return RP_ERR_ALLOC;
    }
    std::memset(raw_table, 0, table_size);
    for (size_t i = 0; i < entry_count; i++) {
        const rp_entry_t *e = &entries[i];
        uint8_t *slot = raw_table + i * 80;
        size_t name_len = std::strlen(e->name);
        size_t copy_len = std::min(name_len, size_t(RP_NAME_MAX - 1));
        std::memcpy(slot, e->name, copy_len);
        *reinterpret_cast<uint32_t*>(slot + 64) = e->offset;
        *reinterpret_cast<uint32_t*>(slot + 68) = e->size;
        *reinterpret_cast<uint32_t*>(slot + 72) = e->comp_size;
        slot[76] = e->crypt_type;
    }
    crypt_words(reinterpret_cast<uint32_t*>(raw_table), table_size / 4, FILE_KEY);
    std::memcpy(p, raw_table, table_size);
    std::free(raw_table);

    *out_len = total;
    return RP_OK;
}
