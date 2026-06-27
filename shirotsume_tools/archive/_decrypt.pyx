from libc.stdlib cimport malloc, free
from libc.string cimport memcpy
from cpython.exc cimport PyErr_SetString, PyErr_Format

from io import IOBase
from os import path, makedirs, SEEK_SET, PathLike
from typing import BinaryIO


cdef bytes _read_exact(object dat_file, size_t n):
    """Read exactly *n* bytes from *dat_file*; raise DecryptError on short read."""
    cdef bytes data = dat_file.read(n)
    if <size_t>len(data) < n:
        raise DecryptError("unexpected end of file")
    return data


cdef class Decryptor:
    def __dealloc__(self):
        if self._file_header:
            free(self._file_header)
            self._file_header = NULL

    cpdef bint _read_sig(self, object dat_file) except -1:
        cdef bytes sig = _read_exact(dat_file, 8)
        return sig == b"RepiPack"

    cpdef void _read_version(self, object dat_file) except *:
        cdef bytes version = _read_exact(dat_file, 4)
        self.version = (<uint32_t*><char*>version)[0]
        if self.version != 2:
            PyErr_Format(DecryptError, "unsupported version %d", self.version)

    cpdef void _read_header(self, object dat_file) except *:
        cdef:
            bytes header_size_obj = _read_exact(dat_file, 4)
            uint32_t header_size = (<uint32_t*><char*>header_size_obj)[0]
            bytearray header = bytearray(_read_exact(dat_file, header_size))
        _decrypt(<uint8_t*>header, header_size, 0x837fc07a)
        self.header = bytes(header)

    cpdef void _read_file_list(self, object dat_file) except *:
        cdef:
            bytes file_count = _read_exact(dat_file, 4)
            uint32_t file_count_int = (<uint32_t*><char*>file_count)[0]
            size_t headers_size = <size_t>file_count_int * 80
            bytearray all_headers = bytearray(_read_exact(dat_file, headers_size))
            uint8_t* buf = <uint8_t*>all_headers
            file_header_t* file_header = <file_header_t*>malloc(file_count_int * sizeof(file_header_t))
            file_header_t* p
            char* header_ptr
            uint32_t i

        if file_header is NULL:
            raise MemoryError()

        for i in range(file_count_int):
            header_ptr = <char*>(buf + i * 80)
            _decrypt(<uint8_t*>header_ptr, 80, 0xf517aa26)
            p = &file_header[i]
            memcpy(p.name, header_ptr, 0x40)
            p.offset = (<uint32_t*>header_ptr)[16]
            p.size = (<uint32_t*>header_ptr)[17]
            p.comp_size = (<uint32_t*>header_ptr)[18]
            p.crypt_type = <uint8_t>header_ptr[76]

        self.file_count = file_count_int
        if self._file_header:
            free(self._file_header)
        self._file_header = file_header
        self._file_list_cache = None

    cdef void _dump_file(self, object dat_file, size_t file_index, object outdir, object encoding = None) except *:
        cdef:
            file_header_t* p
            str name
            str outpath
            bytearray buf
            bytearray out_buf
            uint8_t* buf_ptr
            uint8_t* out_buf_ptr
            bint binmode = False

        if file_index >= self.file_count:
            raise IndexError(f"file index {file_index} out of range (0-{self.file_count - 1})")

        p = &self._file_header[file_index]
        name = p.name.decode("MS932")
        outpath = path.join(outdir, name)

        if encoding is None or not outpath.endswith(".txt"):
            binmode = True
            f = open(outpath, "wb")
        else:
            f = open(outpath, "w", encoding=encoding)
        try:
            dat_file.seek(p.offset, SEEK_SET)
            buf = bytearray(_read_exact(dat_file, p.comp_size))
            buf_ptr = <uint8_t*>buf

            with nogil:
                if p.crypt_type == 1:
                    _decrypt(buf_ptr, p.comp_size, 0xf517aa26)
                elif p.crypt_type == 2:
                    file_decrypt(buf_ptr, p.comp_size)

            if p.comp_size != p.size:
                if p.comp_size == 0:
                    raise DecryptError("corrupted file header: comp_size is 0 but size is non-zero")
                out_buf = bytearray(p.size)
                out_buf_ptr = <uint8_t*>out_buf
                with nogil:
                    decomp(buf_ptr, out_buf_ptr, p.size)
                buf = out_buf

            if binmode:
                f.write(buf)
            else:
                f.write(buf.decode("MS932"))
        finally:
            f.close()

    cpdef void load(self, object dat_file) except *:
        if not self._read_sig(dat_file):
            PyErr_SetString(DecryptError, "not RepiPack file")
        self._read_version(dat_file)
        self._read_header(dat_file)
        self._read_file_list(dat_file)

    def dump_file(self, dat_file: BinaryIO, file: str | int, outdir: str | PathLike, *, encoding: str | None = None) -> None:
        cdef:
            size_t file_index
        if isinstance(file, int):
            file_index = file
        else:
            file_index = self.file_list.index(file)
        self._dump_file(dat_file, file_index, outdir, encoding)

    def dump(self, dat_file: BinaryIO, outdir: str | PathLike, *, encoding: str | None = None) -> None:
        cdef uint32_t i
        for i in range(self.file_count):
            self._dump_file(dat_file, i, outdir, encoding)

    @classmethod
    def decrypt(cls, dat_file: str | PathLike | BinaryIO, outdir: str | PathLike, *, encoding: str | None = None) -> None:
        cdef:
            Decryptor decryptor
            uint32_t i
        close_file = not isinstance(dat_file, (BinaryIO, IOBase))
        if close_file:
            f = open(dat_file, "rb")
        else:
            f = dat_file
        try:
            decryptor = cls()
            decryptor.load(f)

            makedirs(outdir, exist_ok=True)
            for i in range(decryptor.file_count):
                decryptor._dump_file(f, i, outdir, encoding)
        finally:
            if close_file:
                f.close()

    @property
    def file_list(self) -> list[str]:
        if self._file_list_cache is not None:
            return self._file_list_cache
        cdef:
            file_header_t* p
            list file_list
            uint32_t i
        file_list = []
        for i in range(self.file_count):
            p = &self._file_header[i]
            file_list.append(p.name.decode("MS932"))
        self._file_list_cache = file_list
        return file_list

    @property
    def headers(self) -> list[dict]:
        cdef:
            file_header_t* p
            list headers
            uint32_t i
        headers = []
        for i in range(self.file_count):
            p = &self._file_header[i]
            headers.append({
                "offset": p.offset,
                "size": p.size,
                "comp_size": p.comp_size,
                "crypt_type": p.crypt_type,
            })
        return headers


decrypt = Decryptor.decrypt


cdef class DecryptError(Exception):
    pass
