# distutils: language = c++
# cython: language_level = 3

from libc.stdint cimport uint8_t, uint32_t
from libc.stdlib cimport malloc, free
from libc.string cimport memcpy, memset

import struct


class RepiPackError(Exception):
    pass


class InvalidSignatureError(RepiPackError):
    pass


class UnsupportedVersionError(RepiPackError):
    pass


class ShortReadError(RepiPackError):
    pass


class DecompressionError(RepiPackError):
    pass


class CompressionError(RepiPackError):
    pass


cdef inline void _raise_on_error(rp_error_t err) except *:
    if err == RP_OK:
        return
    elif err == RP_ERR_INVALID_SIGNATURE:
        raise InvalidSignatureError("not a RepiPack file")
    elif err == RP_ERR_UNSUPPORTED_VERSION:
        raise UnsupportedVersionError("unsupported RepiPack version")
    elif err == RP_ERR_SHORT_READ:
        raise ShortReadError("unexpected end of file")
    elif err == RP_ERR_DECOMPRESSION:
        raise DecompressionError("decompression failed")
    elif err == RP_ERR_COMPRESSION:
        raise CompressionError("compression failed")
    elif err == RP_ERR_ALLOC:
        raise MemoryError()
    else:
        raise RepiPackError("unknown RepiPack error")


cdef class RawEntry:
    cdef _init_from_c(self, const rp_entry_t *entry):
        memcpy(&self._entry, entry, sizeof(rp_entry_t))

    cpdef str name(self):
        cdef bytes b = (<char*>&self._entry.name)[:64]
        return b.split(b"\x00", 1)[0].decode("cp932")

    cpdef uint32_t offset(self):
        return self._entry.offset

    cpdef uint32_t size(self):
        return self._entry.size

    cpdef uint32_t comp_size(self):
        return self._entry.comp_size

    cpdef uint8_t crypt_type(self):
        return self._entry.crypt_type

    def __repr__(self):
        return f"RawEntry(name={self.name()!r}, offset={self.offset()}, size={self.size()}, comp_size={self.comp_size()}, crypt_type={self.crypt_type()})"


cdef class PackEntry:
    def __init__(self, str name, bytes data):
        self.name = name
        self.data = data

    def __repr__(self):
        return f"PackEntry(name={self.name!r}, data_len={len(self.data)})"


cpdef tuple decode_table(const uint8_t[::1] data):
    cdef:
        uint8_t *header = NULL
        size_t header_len = 0
        rp_entry_t *entries = NULL
        size_t entry_count = 0
        rp_error_t err
        list result = []
        RawEntry entry
        size_t i

    err = rp_decode_header(&data[0], data.shape[0], &header, &header_len,
                           &entries, &entry_count)
    _raise_on_error(err)

    try:
        for i in range(entry_count):
            entry = RawEntry.__new__(RawEntry)
            entry._init_from_c(&entries[i])
            result.append(entry)
        if header_len == 0:
            return (b"", result)
        return (bytes((<uint8_t*>header)[:header_len]), result)
    finally:
        rp_free(header)
        rp_free(entries)


cpdef bytes encode_table(const uint8_t[::1] header, list entries):
    cdef:
        size_t count = len(entries)
        rp_entry_t *raw = <rp_entry_t*>malloc(count * sizeof(rp_entry_t))
        uint8_t *out = NULL
        size_t out_len = 0
        rp_error_t err
        RawEntry entry
        size_t i

    if raw is NULL:
        raise MemoryError()
    memset(raw, 0, count * sizeof(rp_entry_t))
    try:
        for i in range(count):
            entry = <RawEntry>entries[i]
            memcpy(&raw[i], &entry._entry, sizeof(rp_entry_t))
        err = rp_encode_header(&out, &out_len, &header[0], header.shape[0],
                               raw, count)
        _raise_on_error(err)
        return bytes((<uint8_t*>out)[:out_len])
    finally:
        free(raw)
        rp_free(out)


cpdef bytes decode_body(const uint8_t[::1] comp_data, uint32_t size, uint8_t crypt_type):
    cdef:
        size_t comp_size = comp_data.shape[0]
        size_t buf_size = comp_size if comp_size > size else size
        uint8_t *buf = <uint8_t*>malloc(buf_size)
        rp_error_t err

    if buf is NULL:
        raise MemoryError()
    try:
        if comp_size > 0:
            memcpy(buf, &comp_data[0], comp_size)
        err = rp_decode_body(buf, comp_size, size, crypt_type)
        _raise_on_error(err)
        return bytes((<uint8_t*>buf)[:size])
    finally:
        free(buf)


cpdef tuple encode_body(const uint8_t[::1] data, bint compress=True):
    cdef:
        uint8_t *out = NULL
        size_t out_len = 0
        uint8_t crypt_type = 0
        rp_error_t err

    err = rp_encode_body(&data[0], data.shape[0], &out, &out_len,
                         &crypt_type, 1 if compress else 0)
    _raise_on_error(err)
    try:
        return (bytes((<uint8_t*>out)[:out_len]), crypt_type)
    finally:
        rp_free(out)


cdef class Unpacker:
    cdef object _file
    cdef list _entries
    cdef size_t _index
    cdef bytes _header

    def __cinit__(self, object file=None):
        self._file = file
        self._entries = []
        self._index = 0
        self._header = b""

    @property
    def header(self):
        return self._header

    @property
    def entries(self):
        return self._entries

    def __iter__(self):
        return self

    def __next__(self):
        cdef:
            RawEntry raw
            size_t comp_size
            bytes comp_data
            bytes data

        if self._index >= <size_t>len(self._entries):
            raise StopIteration

        raw = <RawEntry>self._entries[self._index]
        self._index += 1
        self._file.seek(raw.offset())
        comp_data = self._file.read(raw.comp_size())
        if <size_t>len(comp_data) != raw.comp_size():
            raise ShortReadError("unexpected end of file")
        data = decode_body(comp_data, raw.size(), raw.crypt_type())
        return PackEntry(raw.name(), data)


cpdef Unpacker unpack(object file):
    cdef Unpacker u = Unpacker.__new__(Unpacker)
    u._file = file

    cdef bytes sig_version_header_size = file.read(16)
    if len(sig_version_header_size) != 16:
        raise ShortReadError("unexpected end of file")

    cdef uint32_t header_size = struct.unpack_from("<I", sig_version_header_size, 12)[0]
    cdef bytes header_data = file.read(header_size)
    if len(header_data) != header_size:
        raise ShortReadError("unexpected end of file")

    cdef bytes file_count_bytes = file.read(4)
    if len(file_count_bytes) != 4:
        raise ShortReadError("unexpected end of file")

    cdef uint32_t file_count = struct.unpack_from("<I", file_count_bytes, 0)[0]
    cdef size_t table_size = <size_t>file_count * 80
    cdef bytes table_data = file.read(table_size)
    if <size_t>len(table_data) != table_size:
        raise ShortReadError("unexpected end of file")

    cdef bytes full_header = sig_version_header_size + header_data + file_count_bytes + table_data
    cdef bytes decoded_header
    cdef list entries

    decoded_header, entries = decode_table(full_header)
    u._header = decoded_header
    u._entries = entries
    return u


cpdef void pack(object file, const uint8_t[::1] header, list entries, bint compress=True) except *:
    cdef:
        size_t count = len(entries)
        rp_entry_t *raw = <rp_entry_t*>malloc(count * sizeof(rp_entry_t))
        PackEntry entry
        size_t i
        size_t data_offset
        size_t offset
        uint8_t *encrypted_body = NULL
        size_t encrypted_len = 0
        uint8_t crypt_type = 0
        uint8_t *full_header = NULL
        size_t full_header_len = 0
        rp_error_t err
        bytes name_bytes
        bytes body_data

    if raw is NULL:
        raise MemoryError()
    memset(raw, 0, count * sizeof(rp_entry_t))

    try:
        for i in range(count):
            entry = <PackEntry>entries[i]
            name_bytes = entry.name.encode("cp932")
            if <size_t>len(name_bytes) >= 64:
                raise ValueError(f"packed name is too long: {entry.name}")
            memcpy(raw[i].name, <const char*>name_bytes, len(name_bytes))
            raw[i].size = len(entry.data)

        data_offset = 8 + 4 + 4 + header.shape[0] + 4 + count * 80
        offset = data_offset

        err = rp_encode_header(&full_header, &full_header_len,
                               &header[0], header.shape[0], raw, count)
        _raise_on_error(err)
        try:
            file.write(bytes((<uint8_t*>full_header)[:full_header_len]))
        finally:
            rp_free(full_header)
            full_header = NULL

        for i in range(count):
            entry = <PackEntry>entries[i]
            body_data = entry.data
            err = rp_encode_body(<const uint8_t*>body_data, len(body_data),
                                 &encrypted_body, &encrypted_len,
                                 &crypt_type, 1 if compress else 0)
            _raise_on_error(err)
            try:
                file.write(bytes((<uint8_t*>encrypted_body)[:encrypted_len]))
            finally:
                rp_free(encrypted_body)
                encrypted_body = NULL

            raw[i].offset = offset
            raw[i].comp_size = encrypted_len
            raw[i].crypt_type = crypt_type
            offset += encrypted_len

        file.seek(0)
        err = rp_encode_header(&full_header, &full_header_len,
                               &header[0], header.shape[0], raw, count)
        _raise_on_error(err)
        try:
            file.write(bytes((<uint8_t*>full_header)[:full_header_len]))
        finally:
            rp_free(full_header)
    finally:
        free(raw)


cpdef void replace(object in_file, object out_file, object replacements, bint compress=True) except *:
    cdef:
        Unpacker u = unpack(in_file)
        list entries = u.entries
        RawEntry raw
        size_t i
        size_t count = len(entries)
        rp_entry_t *raw_arr = <rp_entry_t*>malloc(count * sizeof(rp_entry_t))
        bytes comp_data
        bytes new_data
        bytes encrypted
        uint8_t crypt_type = 0
        size_t offset
        size_t data_offset
        uint8_t *full_header = NULL
        size_t full_header_len = 0
        rp_error_t err
        object enc_result

    if raw_arr is NULL:
        raise MemoryError()
    memset(raw_arr, 0, count * sizeof(rp_entry_t))

    try:
        for i in range(count):
            raw = <RawEntry>entries[i]
            memcpy(&raw_arr[i], &raw._entry, sizeof(rp_entry_t))

        data_offset = 8 + 4 + 4 + len(u.header) + 4 + count * 80
        offset = data_offset

        err = rp_encode_header(&full_header, &full_header_len,
                               <const uint8_t*>u.header, len(u.header),
                               raw_arr, count)
        _raise_on_error(err)
        try:
            out_file.write(bytes((<uint8_t*>full_header)[:full_header_len]))
        finally:
            rp_free(full_header)
            full_header = NULL

        for i in range(count):
            raw = <RawEntry>entries[i]
            if raw.name() in replacements:
                new_data = replacements[raw.name()]
                enc_result = encode_body(new_data, compress)
                encrypted = enc_result[0]
                crypt_type = enc_result[1]
                raw_arr[i].size = len(new_data)
                raw_arr[i].comp_size = len(encrypted)
                raw_arr[i].crypt_type = crypt_type
                out_file.write(encrypted)
            else:
                in_file.seek(raw.offset())
                comp_data = in_file.read(raw.comp_size())
                if <size_t>len(comp_data) != raw.comp_size():
                    raise ShortReadError("unexpected end of file")
                raw_arr[i].offset = offset
                out_file.write(comp_data)
                offset += raw.comp_size()
                continue

            raw_arr[i].offset = offset
            offset += raw_arr[i].comp_size

        out_file.seek(0)
        err = rp_encode_header(&full_header, &full_header_len,
                               <const uint8_t*>u.header, len(u.header),
                               raw_arr, count)
        _raise_on_error(err)
        try:
            out_file.write(bytes((<uint8_t*>full_header)[:full_header_len]))
        finally:
            rp_free(full_header)
    finally:
        free(raw_arr)
