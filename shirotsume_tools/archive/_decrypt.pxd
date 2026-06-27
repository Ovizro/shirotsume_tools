from libc.stdint cimport uint8_t, uint32_t


cdef extern from "decrypt.h":
    ctypedef struct file_header_t:
        char name[0x40]
        uint32_t offset
        uint32_t size
        uint32_t comp_size
        uint8_t  crypt_type
        
    cdef void _decrypt "decrypt" (uint8_t* buf, size_t size, uint32_t key) noexcept nogil
    cdef void file_decrypt(uint8_t* buf, size_t size) noexcept nogil
    cdef void decomp(uint8_t* comp_buf, uint8_t* buf, size_t size) noexcept nogil


cdef class Decryptor:
    cdef:
        file_header_t* _file_header
        list _file_list_cache
    cdef readonly:
        uint32_t version
        bytes header
        uint32_t file_count

    cpdef bint _read_sig(self, object dat_file) except -1
    cpdef void _read_version(self, object dat_file) except *
    cpdef void _read_header(self, object dat_file) except *
    cpdef void _read_file_list(self, object dat_file) except *
    cdef void _dump_file(self, object dat_file, size_t file_index, object outdir, object encoding=?) except *
    cpdef void load(self, object dat_file) except *
