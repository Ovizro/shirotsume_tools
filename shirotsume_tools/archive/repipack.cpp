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

static void file_encrypt_words(uint32_t *buf, size_t word_count) {
    const uint32_t XOR6 = 0x26262626U;
    const uint32_t MASK6 = 0x3F3F3F3FU;
    const uint32_t LOW2 = 0x03030303U;
    for (size_t i = 0; i < word_count; i++) {
        uint32_t v = buf[i];
        uint32_t hi = (v >> 6) & LOW2;
        uint32_t lo = ((v & MASK6) ^ XOR6) << 2;
        buf[i] = (hi | lo) & 0xFFFFFFFFU;
    }
}

static void build_encrypted_table(uint8_t *raw_table,
                                  const rp_entry_t *entries,
                                  size_t entry_count) {
    size_t table_size = entry_count * 80;
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
        crypt_words(reinterpret_cast<uint32_t*>(slot), 80 / 4, FILE_KEY);
    }
}

// --- Okumura LZSS binary search tree compressor ---
// The original RepiPack compressor uses Haruhiko Okumura's classic LZSS
// algorithm with a binary search tree for longest-match finding. Key
// properties that make output byte-identical to the original:
//   1. Binary tree naturally orders candidates by string content, so the
//      "first longest match in tree-traversal order" tie-break is automatic.
//   2. When a full F-byte match is found, the new node REPLACES the old
//      node in the tree (identical strings), which deterministically prunes
//      earlier duplicate positions and explains every observed tie-break.
//   3. RLE / overlapping matches work automatically because the lookahead is
//      pre-written into the cache, so comparisons against fresh writes read
//      the correct (soon-to-be-output) bytes.

namespace {

constexpr int LZSS_N = 4096;
constexpr int LZSS_F = 18;
constexpr int LZSS_THRESHOLD = 2;
constexpr int LZSS_NIL = -1;

}  // namespace

static rp_error_t compress(const uint8_t *in, size_t in_len,
                           uint8_t **out, size_t *out_len) {
    if (in_len == 0) {
        *out = nullptr;
        *out_len = 0;
        return RP_OK;
    }

    uint8_t cache[LZSS_N];
    std::memset(cache, 0, sizeof(cache));

    // Tree arrays: indices 0..N-1 are real nodes; N..N+255 are root sentinels
    // (one per byte value, only rson is used for roots).
    int lson[LZSS_N + 256];
    int rson[LZSS_N + 256];
    int dad[LZSS_N + 256];
    for (int i = 0; i < LZSS_N + 256; ++i) {
        lson[i] = LZSS_NIL;
        rson[i] = LZSS_NIL;
        dad[i] = LZSS_NIL;
    }

    int match_position = 0;
    int match_length = 0;

    // InsertNode: insert the F-byte string starting at position r into the
    // tree and find the longest match. On a full F-byte match, replace the
    // existing node (identical strings) so only the newest position survives.
    auto insert_node = [&](int r) {
        int cmp = 1;
        int p = LZSS_N + cache[r];  // root sentinel for this byte value
        lson[r] = LZSS_NIL;
        rson[r] = LZSS_NIL;
        match_length = 0;

        for (;;) {
            if (cmp >= 0) {
                if (rson[p] != LZSS_NIL) {
                    p = rson[p];
                } else {
                    rson[p] = r;
                    dad[r] = p;
                    return;
                }
            } else {
                if (lson[p] != LZSS_NIL) {
                    p = lson[p];
                } else {
                    lson[p] = r;
                    dad[r] = p;
                    return;
                }
            }

            // Compare strings at r and p, starting from byte 1 (byte 0 is
            // guaranteed equal because they share the same root).
            int i = 1;
            while (i < LZSS_F) {
                uint8_t cr = cache[(r + i) & (LZSS_N - 1)];
                uint8_t cp = cache[(p + i) & (LZSS_N - 1)];
                if (cr != cp) {
                    cmp = static_cast<int>(cr) - static_cast<int>(cp);
                    break;
                }
                ++i;
            }
            if (i >= LZSS_F) cmp = 0;

            if (i > match_length) {
                match_position = p;
                match_length = i;
                if (match_length >= LZSS_F) break;  // full match: replace
            }
        }

        // Replace p with r in the tree (identical F-byte strings).
        dad[r] = dad[p];
        lson[r] = lson[p];
        rson[r] = rson[p];
        if (lson[p] != LZSS_NIL) dad[lson[p]] = r;
        if (rson[p] != LZSS_NIL) dad[rson[p]] = r;
        if (dad[p] != LZSS_NIL) {
            if (rson[dad[p]] == p) rson[dad[p]] = r;
            else lson[dad[p]] = r;
        }
        dad[p] = LZSS_NIL;
    };

    // DeleteNode: remove node p from the tree (standard BST deletion using
    // the in-order predecessor as replacement).
    auto delete_node = [&](int p) {
        if (dad[p] == LZSS_NIL) return;  // not in tree

        int q;
        if (rson[p] == LZSS_NIL) {
            q = lson[p];
        } else if (lson[p] == LZSS_NIL) {
            q = rson[p];
        } else {
            q = lson[p];
            if (rson[q] != LZSS_NIL) {
                while (rson[q] != LZSS_NIL) q = rson[q];
                rson[dad[q]] = lson[q];
                if (lson[q] != LZSS_NIL) dad[lson[q]] = dad[q];
                lson[q] = lson[p];
                if (lson[p] != LZSS_NIL) dad[lson[p]] = q;
            }
            rson[q] = rson[p];
            if (rson[p] != LZSS_NIL) dad[rson[p]] = q;
        }

        if (q != LZSS_NIL) dad[q] = dad[p];
        if (dad[p] != LZSS_NIL) {
            if (rson[dad[p]] == p) rson[dad[p]] = q;
            else lson[dad[p]] = q;
        }
        dad[p] = LZSS_NIL;
    };

    std::vector<uint8_t> temp;
    temp.reserve(in_len + in_len / 8 + 16);

    int r = LZSS_N - LZSS_F;  // 0xFEE
    int s = 0;

    // Pre-load the first F bytes (lookahead) into the cache.
    int lookahead = static_cast<int>(std::min<size_t>(LZSS_F, in_len));
    for (int i = 0; i < lookahead; ++i) {
        cache[(r + i) & (LZSS_N - 1)] = in[i];
    }
    size_t data_pos = static_cast<size_t>(lookahead);

    insert_node(r);

    while (lookahead > 0) {
        size_t flag_pos = temp.size();
        temp.push_back(0);
        uint8_t flag = 0;

        for (int bit = 0; bit < 8 && lookahead > 0; ++bit) {
            if (match_length > lookahead) match_length = lookahead;

            if (match_length <= LZSS_THRESHOLD) {
                match_length = 1;
                flag |= static_cast<uint8_t>(1 << bit);
                temp.push_back(cache[r]);
            } else {
                int offset = match_position & 0xFFF;
                int length_code = (match_length - 3) & 0x0F;
                temp.push_back(static_cast<uint8_t>(offset & 0xFF));
                temp.push_back(static_cast<uint8_t>(((offset >> 4) & 0xF0) | length_code));
            }

            // Shift the window by match_length bytes: delete the oldest
            // position, write the next input byte (if available), advance
            // s/r, and insert the new position into the tree.
            // NOTE: save match_length before the loop — insert_node()
            // overwrites it with the next decision's match.
            const int consume = match_length;
            for (int k = 0; k < consume; ++k) {
                if (data_pos < in_len) {
                    uint8_t c = in[data_pos++];
                    delete_node(s);
                    cache[s] = c;
                    s = (s + 1) & (LZSS_N - 1);
                    r = (r + 1) & (LZSS_N - 1);
                    insert_node(r);
                } else {
                    delete_node(s);
                    s = (s + 1) & (LZSS_N - 1);
                    r = (r + 1) & (LZSS_N - 1);
                    --lookahead;
                    if (lookahead > 0) insert_node(r);
                }
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

    if (header_size == 0) {
        *header = nullptr;
        *header_len = 0;
    } else {
        *header = static_cast<uint8_t*>(std::malloc(header_size));
        if (!*header) return RP_ERR_ALLOC;
        std::memcpy(*header, in + 16, header_size);
        decrypt_words(reinterpret_cast<uint32_t*>(*header), header_size / 4, HEADER_KEY);
        *header_len = header_size;
    }

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

    for (size_t i = 0; i < count; i++) {
        uint8_t *p = raw_table + i * 80;
        decrypt_words(reinterpret_cast<uint32_t*>(p), 80 / 4, FILE_KEY);
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
                          uint8_t *crypt_type, int do_compress,
                          uint8_t crypt_type_in) {
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

    uint8_t ct = (crypt_type_in != 0) ? crypt_type_in : 1;
    if (buf_len > 0) {
        if (ct == 2) {
            file_encrypt_words(reinterpret_cast<uint32_t*>(buf), buf_len / 4);
        } else {
            crypt_words(reinterpret_cast<uint32_t*>(buf), buf_len / 4, FILE_KEY);
        }
    }
    *out = buf;
    *out_len = buf_len;
    *crypt_type = ct;
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

    if (table_size > 0) {
        uint8_t *raw_table = static_cast<uint8_t*>(std::malloc(table_size));
        if (!raw_table) {
            std::free(*out);
            return RP_ERR_ALLOC;
        }
        build_encrypted_table(raw_table, entries, entry_count);
        std::memcpy(p, raw_table, table_size);
        std::free(raw_table);
    }

    *out_len = total;
    return RP_OK;
}

rp_error_t rp_encode_table(uint8_t **out, size_t *out_len,
                           const rp_entry_t *entries, size_t entry_count) {
    if (entry_count > SIZE_MAX / 80) return RP_ERR_ALLOC;

    size_t table_size = entry_count * 80;
    if (table_size == 0) {
        *out = nullptr;
        *out_len = 0;
        return RP_OK;
    }

    uint8_t *raw_table = static_cast<uint8_t*>(std::malloc(table_size));
    if (!raw_table) return RP_ERR_ALLOC;

    build_encrypted_table(raw_table, entries, entry_count);
    *out = raw_table;
    *out_len = table_size;
    return RP_OK;
}
