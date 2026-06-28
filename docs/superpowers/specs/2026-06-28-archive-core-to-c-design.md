# Archive 核心编解码迁移至 C 设计文档

## 1. 目标

将 `shirotsume_tools/archive/writer.py` 中 RepiPack 的加解密、压缩解压、打包/解包/替换循环下沉到 C/C++，并通过单个 Cython 扩展 `crypt` 暴露。最终达成：

- 更高的解包/打包性能。
- 流式文件 I/O，降低大 `.dat` 文件的内存峰值。
- 回写时支持压缩，避免输出文件体积膨胀。
- 单一 Cython 模块，简化构建与维护。

## 2. 当前状态

- `shirotsume_tools/archive/_decrypt.pyx` + `decrypt.cpp/h`：提供 `Decryptor` 解密/解压能力。
- `shirotsume_tools/archive/writer.py`：纯 Python 实现 `read_pack` / `write_pack` / `replace_entries`，含加解密/解压逻辑，但写回时不压缩。
- `setup.py`：编译 `_decrypt` 扩展，源码为 `_decrypt.pyx` / `decrypt.cpp`。

## 3. 设计决策

| 决策 | 选择 | 原因 |
|------|------|------|
| C++ 核心文件 | 新建 `repipack.cpp/h` | 独立、完整地承载 RepiPack 编解码，避免旧 `decrypt.cpp` 职责继续扩张。 |
| Cython 入口 | 重命名为 `crypt.pyx/pxd` | 单一模块暴露完整加解密/打包能力，名称更准确。 |
| 文件 I/O | 放在 Cython 层，流式处理 | 避免 C 层处理路径编码；同时降低内存占用。 |
| 旧 `Decryptor` | 不兼容，直接删除 | 用户明确可重新设计 API 并更新上游引用。 |
| 压缩 | 一并实现 | `write_pack` / `replace_entries` 默认压缩，输出体积与原文件接近。 |

## 4. 模块结构

```
shirotsume_tools/archive/
├── repipack.cpp          # C++ 核心：表/体 编解码
├── repipack.h            # C 接口头
├── crypt.pyx             # Cython 扩展：流式 I/O + Python API
├── crypt.pxd
├── reader.py             # 重写：使用 crypt 的新 API
├── writer.py             # 重写：文件 I/O 薄封装
├── model.py              # FileEntry / PackEntry
├── errors.py             # ArchiveError 体系
└── _decrypt.* / decrypt.* # 删除
```

## 5. C++ 核心接口（`repipack.h`）

所有接口只操作内存缓冲区，不碰文件。

```c
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

/* 表头/文件表编解码 */
rp_error_t rp_decode_header(const uint8_t *in, size_t in_len,
                            uint8_t **header, size_t *header_len,
                            rp_entry_t **entries, size_t *entry_count);

rp_error_t rp_encode_header(uint8_t **out, size_t *out_len,
                            const uint8_t *header, size_t header_len,
                            const rp_entry_t *entries, size_t entry_count);

rp_error_t rp_encode_table(uint8_t **out, size_t *out_len,
                           const rp_entry_t *entries, size_t entry_count);

/* 单文件体处理 */
rp_error_t rp_decode_body(uint8_t *buf, size_t comp_size, uint32_t size, uint8_t crypt_type);
rp_error_t rp_encode_body(const uint8_t *in, size_t in_len,
                          uint8_t **out, size_t *out_len,
                          uint8_t *crypt_type, int compress);

/* 辅助：内存释放 */
void rp_free(void *p);

#endif
```

说明：
- `rp_decode_body` 在原地解密，如需解压则输出到新分配缓冲区（函数内部处理）。
- `rp_encode_body` 返回加密后的字节；`crypt_type` 固定为 `1`（类型 2 仅用于读取旧数据）。
- 所有 `rp_free` 释放的内存均由 C++ 层 `malloc`/`new` 分配。

## 6. Cython 扩展 `crypt` 接口

`crypt.pyx` 是**底层编解码扩展**，直接操作 `bytes` 缓冲区和 `BinaryIO`，不处理文件夹、路径字符串、文本编码等高层语义。高层操作保留在 `reader.py` / `writer.py`。

### 6.1 `crypt.pxd` 类型声明

```cython
from libc.stdint cimport uint8_t, uint32_t

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

    rp_error_t rp_decode_header(const uint8_t *in, size_t in_len,
                                uint8_t **header, size_t *header_len,
                                rp_entry_t **entries, size_t *entry_count)
    rp_error_t rp_encode_header(uint8_t **out, size_t *out_len,
                                const uint8_t *header, size_t header_len,
                                const rp_entry_t *entries, size_t entry_count)
    rp_error_t rp_decode_body(uint8_t *buf, size_t comp_size, uint32_t size, uint8_t crypt_type)
    rp_error_t rp_encode_body(const uint8_t *in, size_t in_len,
                              uint8_t **out, size_t *out_len,
                              uint8_t *crypt_type, int compress)
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
```

### 6.2 `crypt.pyx` 暴露的 Python API

```cython
# 异常
class RepiPackError(Exception): ...
class InvalidSignatureError(RepiPackError): ...
class UnsupportedVersionError(RepiPackError): ...
class ShortReadError(RepiPackError): ...

# 表头/文件表编解码（基于 bytes）
cpdef tuple decode_table(const uint8_t[::1] data)  # -> (header, list[RawEntry])
cpdef bytes encode_table(const uint8_t[::1] header, list entries)  # entries: list[RawEntry]

# 单文件体编解码（基于 bytes）
cpdef bytes decode_body(const uint8_t[::1] comp_data, uint32_t size, uint8_t crypt_type)
cpdef tuple encode_body(const uint8_t[::1] data, bint compress=*)  # -> (encrypted_bytes, crypt_type)

# 流式解包迭代器
cdef class Unpacker:
    cdef object _file
    cdef list _entries       # list[RawEntry]
    cdef size_t _index

    def __iter__(self):
        return self

    def __next__(self) -> PackEntry:
        # seek -> read(comp_size) -> rp_decode_body -> PackEntry
        ...

cpdef Unpacker unpack(object file)  # file: BinaryIO; 构造时读表，迭代时解压文件体

# 流式打包：entries 为任意 Iterable[PackEntry]
cpdef void pack(object file,
                const uint8_t[::1] header,
                object entries,   # Iterable[PackEntry]
                bint compress=True,
                object count=None) except *

# 流式替换
cpdef void replace(object in_file,
                   object out_file,
                   object replacements,  # Mapping[str, bytes] | Callable[[str], bytes | None]
                   bint compress=*) except *
```

说明：
- 所有函数均使用 `cpdef` 或 `cdef`，在 Cython 内部以 C 类型操作，减少 Python 开销。
- `const uint8_t[::1]` memoryview 直接绑定 `bytes`/`bytearray` 缓冲区，避免额外拷贝。
- `unpack` / `pack` / `replace` 只接受已打开的 `BinaryIO`；Cython 内部调用 `f.read()` / `f.write()` / `f.seek()`，但以 C 缓冲区方式传递数据。
- 异常由 Cython 层根据 `rp_error_t` 直接抛出，调用方无需检查错误码。

流式处理细节：
- `unpack`：构造时读取头/表到 `_entries`；迭代时按 entry 逐个 `seek` → `read(comp_size)` → C 解密/解压 → 构造 `PackEntry` 返回。任何时候内存中只保留一个文件体。
- `pack`：单遍流式打包。若 `count` 为 `None`，则从 `len(entries)` 取条目数（要求 `entries` 为 `Sized`）；若显式传入 `count`，则允许 `entries` 为一次性 generator。先根据 `count` 分配 `rp_entry_t[count]` 元数据数组，再写占位头（表区域为加密后的 0），然后逐条遍历 `entries`：`encode_body` 后直接通过 memoryview 写入文件体并回填该条元数据；最后 `seek` 到表偏移，只回填加密表。
- `replace`：单遍读取输入、写入输出。对每个 entry 查 `replacements`，命中则 `encode_body` 写入新数据，否则直接复制原 `comp_data`。无需缓存整个 `.dat`。

## 7. Python 层

### 7.1 `reader.py`

`reader.py` 负责路径、文件夹、文件名索引、文本编码等高层语义。

```python
class Archive:
    def __init__(self, path: str | Path):
        self._path = Path(path)
        self._file: BinaryIO | None = None
        self._unpacker: crypt.Unpacker | None = None
        self._entries: list[crypt.RawEntry] | None = None

    def __enter__(self) -> "Archive":
        self._file = self._path.open("rb")
        self._unpacker = crypt.unpack(self._file)
        self._entries = self._unpacker.entries  # RawEntry 元数据列表
        return self

    def __exit__(self, *args) -> None:
        if self._file is not None:
            self._file.close()

    @property
    def file_list(self) -> list[str]: ...
    @property
    def file_count(self) -> int: ...

    def extract(self, file: str | int, outdir, *, encoding=None):
        # 按 name/index 定位 entry，使用 decode_body 解压写出
        ...

    def extract_all(self, outdir, *, encoding=None):
        # 直接遍历 self._unpacker，逐个解压写出
        ...

    def iter_entries(self) -> Iterator[FileEntry]: ...

def decrypt(dat_file, outdir, *, encoding=None) -> None:
    with Archive(dat_file) as arc:
        arc.extract_all(outdir, encoding=encoding)
```

### 7.2 `writer.py`

`writer.py` 保留同名函数作为文件路径薄封装：

```python
def read_pack(path: str | Path) -> tuple[bytes, list[PackEntry]]:
    with open(path, "rb") as f:
        unpacker = crypt.unpack(f)
        header = unpacker.header
        entries = list(unpacker)
    return header, entries

def write_pack(path, header, entries, *, compress=True, count=None) -> None:
    with open(path, "wb") as f:
        crypt.pack(f, header, entries, compress, count)

def replace_entries(dat_path, out_path, replacements, *, compress=True) -> None:
    with open(dat_path, "rb") as fin, open(out_path, "wb") as fout:
        crypt.replace(fin, fout, replacements, compress)
```

## 8. 构建配置

更新 `setup.py`：

```python
import os
from setuptools import Extension, setup

USE_CYTHON = "USE_CYTHON" in os.environ
FILE_SUFFIX = ".pyx" if USE_CYTHON else ".c"

extensions = [
    Extension(
        "shirotsume_tools.archive.crypt",
        [
            "shirotsume_tools/archive/crypt" + FILE_SUFFIX,
            "shirotsume_tools/archive/repipack.cpp",
        ],
        include_dirs=["shirotsume_tools/archive"],
    ),
]

if USE_CYTHON:
    from Cython.Build import cythonize
    extensions = cythonize(
        extensions,
        annotate=True,
        compiler_directives={"language_level": "3"},
    )

setup(ext_modules=extensions)
```

同时更新 `pyproject.toml` 的 `package-data`（如需要包含 `.pyi` 等）。

## 9. 测试策略

- **单元测试**：对 `repipack.cpp` 的加解密/压缩解压做 round-trip 测试（可用 Cython 封装后测）。
- **集成测试**：
  - 用现有 `.dat` 文件解包，与原 `_decrypt.Decryptor` 输出逐字节比对。
  - 用 `replace_entries` 替换若干文件后，再解包验证内容正确。
  - `write_pack` 生成的 `.dat` 能被原游戏或原解密器正确读取。
- **内存测试**：对大 `.dat` 使用流式 API，监控峰值内存不随文件大小线性增长。

## 10. 迁移影响

- `shirotsume_tools.archive.__init__` 导出更新：移除 `Decryptor`、`DecryptError`；新增 `crypt` 相关 API。
- `reader.py` 内部实现变更，对外 API 不变。
- `writer.py` 函数签名不变，内部改由 `crypt` 实现。
- CLI 与 `translation.patch` 调用 `replace_entries` 的地方无需修改。

## 11. 待实施步骤概要

1. 实现 `repipack.cpp/h`（加解密、压缩解压、表编解码）。
2. 实现 `crypt.pyx/pxd`（流式 I/O、Python API）。
3. 重写 `reader.py` / `writer.py`。
4. 更新 `setup.py` / `__init__.py`。
5. 删除 `_decrypt.*` / `decrypt.*`。
6. 补充/更新测试。
7. 验证 round-trip 与原 `.dat` 兼容性。
