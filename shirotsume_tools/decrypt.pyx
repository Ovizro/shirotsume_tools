from libc.stdlib cimport malloc, free
from libc.string cimport strncpy
from cpython.bytes cimport PyBytes_FromStringAndSize
from cpython.exc cimport PyErr_SetString, PyErr_Format

from os import path, makedirs, SEEK_SET
from typing import BinaryIO, List


cdef class Decryptor:
    def __dealloc__(self):
        if self._file_header:
            free(self._file_header)
            self._file_header = NULL
    
    cpdef bint _read_sig(self, object dat_file) except -1:
        cdef bytes sig = dat_file.read(8)
        return sig == b"RepiPack"
    
    cpdef void _read_version(self, object dat_file) except *:
        cdef:
            bytes version = dat_file.read(4)
            const char* version_text = <const char*>version
            uint32_t version_int = (<uint32_t*>version_text)[0]
        self.version = version_int
        if version_int != 2:
            PyErr_Format(DecryptError, "unsupported version %d", version_int)
    
    cpdef void _read_header(self, object dat_file) except *:
        cdef:
            bytes header_size_obj = dat_file.read(4)
            const char* header_size_text = <const char*>header_size_obj
            uint32_t header_size = (<uint32_t*>header_size_text)[0]
            bytes header = dat_file.read(header_size)
            char* header_buf = <char*>header
        _decrypt(<uint8_t*>header_buf, header_size, 0x837fc07a)
        self.header = header
    
    cpdef void _read_file_list(self, object dat_file) except *:
        cdef:
            bytes file_count = dat_file.read(4)
            const char* file_count_text = <const char*>file_count
            uint32_t file_count_int = (<uint32_t*>file_count_text)[0]
            file_header_t* file_header = <file_header_t*>malloc(file_count_int * sizeof(file_header_t))

            bytes header
            const char* header_text
            file_header_t* p
            uint32_t i

        for i in range(file_count_int):
            p = &file_header[i]
            header = dat_file.read(80)
            header_text = <const char*>header

            _decrypt(<uint8_t*>header_text, len(header), 0xf517aa26)

            strncpy(p.name, header_text, 0x40)
            p.offset = (<uint32_t*>header_text)[16];
            p.size = (<uint32_t*>header_text)[17];
            p.comp_size = (<uint32_t*>header_text)[18];
            p.crypt_type = header_text[76];

        self.file_count = file_count_int
        if self._file_header:
            free(self._file_header)
        self._file_header = file_header
    
    cdef void _dump_file(self, object dat_file, size_t file_index, object outdir, object encoding = None) except *:
        cdef:
            file_header_t* p = &self._file_header[file_index]
            str name = p.name.decode("shift-jis")
            str outpath = path.join(outdir, name)
            bytes buf
            bytes comp_buf
            bint binmode = False
        
        if encoding is None or not outpath.endswith(".txt"):
            binmode = True
            f = open(outpath, "wb")
        else:
            f = open(outpath, "w", encoding=encoding)
        try:
            dat_file.seek(p.offset, SEEK_SET)
            buf = dat_file.read(p.comp_size)
            if p.crypt_type == 1:
                _decrypt(buf, len(buf), 0xf517aa26)
            elif p.crypt_type == 2:
                file_decrypt(buf, len(buf))
            
            if p.comp_size != p.size:
                comp_buf = buf
                buf = PyBytes_FromStringAndSize(NULL, p.size)
                decomp(comp_buf, buf, p.size)
            
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
    
    def dump_file(self, dat_file: BinaryIO, file: Union[str, int], outdir: Union[str, PathLike], *, encoding: str = None) -> None:
        cdef:
            size_t file_index
        if isinstance(file, int):
            file_index = file
        else:
            file_index = self.file_list.index(file)
        self._dump_file(dat_file, file_index, outdir, encoding)
    
    def dump(self, dat_file: BinaryIO, outdir: Union[str, PathLike], *, encoding: str = None) -> None:
        cdef uint32_t i
        for i in range(self.file_count):
            self._dump_file(dat_file, i, outdir, encoding)
    
    @classmethod
    def decrypt(cls, dat_file: Union[str, PathLike, BinaryIO], outdir: Union[str, PathLike], *, encoding: str = None) -> None:
        cdef Decryptor decryptor
        if isinstance(dat_file, BinaryIO):
            f = dat_file
        else:
            f = open(dat_file, "rb")
        decryptor = cls()
        decryptor.load(f)

        makedirs(outdir, exist_ok=True)
        cdef uint32_t i
        for i in range(decryptor.file_count):
            decryptor._dump_file(f, i, outdir, encoding)
        if isinstance(dat_file, str):
            f.close()
    
    @property
    def file_list(self) -> List[str]:
        cdef:
            file_header_t* p
            list file_list
        file_list = []
        for i in range(self.file_count):
            p = &self._file_header[i]
            file_list.append(p.name.decode("MS932"))
        return file_list


decrypt = Decryptor.decrypt
    

cdef class DecryptError(Exception):
    pass
