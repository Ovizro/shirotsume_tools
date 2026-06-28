#ifndef REPIPACK_H
#define REPIPACK_H

#include <stdint.h>
#include <stddef.h>

#define RP_NAME_MAX 64

typedef struct {
    char name[RP_NAME_MAX];
    uint32_t offset;
    uint32_t size;
    uint32_t comp_size;
    uint8_t crypt_type;
} rp_entry_t;

typedef enum {
    RP_OK = 0,
    RP_ERR_INVALID_SIGNATURE,
    RP_ERR_UNSUPPORTED_VERSION,
    RP_ERR_SHORT_READ,
    RP_ERR_DECOMPRESSION,
    RP_ERR_COMPRESSION,
    RP_ERR_ALLOC,
} rp_error_t;

rp_error_t rp_decode_header(const uint8_t *in, size_t in_len,
                            uint8_t **header, size_t *header_len,
                            rp_entry_t **entries, size_t *entry_count);

rp_error_t rp_encode_header(uint8_t **out, size_t *out_len,
                            const uint8_t *header, size_t header_len,
                            const rp_entry_t *entries, size_t entry_count);

/* Caller must allocate `buf` with at least `size` bytes. */
rp_error_t rp_decode_body(uint8_t *buf, size_t comp_size, uint32_t size, uint8_t crypt_type);

rp_error_t rp_encode_body(const uint8_t *in, size_t in_len,
                          uint8_t **out, size_t *out_len,
                          uint8_t *crypt_type, int compress);

void rp_free(void *p);

#endif
