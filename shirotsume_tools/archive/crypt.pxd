from libc.stdint cimport uint8_t, uint32_t, uint16_t
from libc.stddef cimport size_t

cdef extern from "repipack.h":
    ctypedef struct rp_entry_t:
        char name[64]
        uint32_t offset
        uint32_t size
        uint32_t comp_size
        uint8_t crypt_type

    ctypedef enum rp_error_t:
        RP_OK
        RP_ERR_INVALID_SIGNATURE
        RP_ERR_UNSUPPORTED_VERSION
        RP_ERR_SHORT_READ
        RP_ERR_DECOMPRESSION
        RP_ERR_COMPRESSION
        RP_ERR_ALLOC

    rp_error_t rp_decode_header(const uint8_t *data, size_t data_len,
                                uint8_t **header, size_t *header_len,
                                rp_entry_t **entries, size_t *entry_count)
    rp_error_t rp_encode_header(uint8_t **out, size_t *out_len,
                                const uint8_t *header, size_t header_len,
                                const rp_entry_t *entries, size_t entry_count)
    rp_error_t rp_encode_table(uint8_t **out, size_t *out_len,
                               const rp_entry_t *entries, size_t entry_count)
    rp_error_t rp_decode_body(uint8_t *buf, size_t comp_size, uint32_t size, uint8_t crypt_type)
    rp_error_t rp_encode_body(const uint8_t *data, size_t data_len,
                              uint8_t **out, size_t *out_len,
                              uint8_t *crypt_type, int compress,
                              uint8_t crypt_type_in)
    void rp_free(void *p)

cdef class RawEntry:
    cdef rp_entry_t _entry
    cdef _init_from_c(self, const rp_entry_t *entry)
    cpdef str name(self)
    cpdef uint32_t offset(self)
    cpdef uint32_t size(self)
    cpdef uint32_t comp_size(self)
    cpdef uint8_t crypt_type(self)

cdef class PackEntry:
    cdef public str name
    cdef public bytes data
    cdef public uint8_t crypt_type
