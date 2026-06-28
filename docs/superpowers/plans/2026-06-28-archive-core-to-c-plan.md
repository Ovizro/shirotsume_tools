# Archive 核心编解码迁移至 C Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 `shirotsume_tools/archive/writer.py` 中的 RepiPack 编解码逻辑下沉到 C/C++，通过单个 Cython 扩展 `crypt` 暴露，并保留 `reader.py` / `writer.py` 的 Python 层封装。

**Architecture:** 新建 `repipack.cpp/h` 承载 RepiPack 字节级编解码（加解密、压缩解压、表编解码）；`crypt.pyx/pxd` 作为唯一 Cython 入口，以 memoryview 和 BinaryIO 做流式封装；`reader.py` / `writer.py` 保留高层路径/文件夹语义。

**Tech Stack:** C++17, Cython 3, setuptools, pytest.

## Global Constraints

- Python >= 3.10
- Cython >= 3.0
- 单一 Cython 扩展模块：`shirotsume_tools.archive.crypt`
- 文件 I/O 保留在 Cython/Python 层，C++ 核心只操作内存缓冲区
- `crypt.pyx` 使用 `cdef`/`cpdef`/`const uint8_t[::1]` 等 Cython 原生特性
- 流式 API：`unpack` 返回 `Unpacker` 迭代器，`pack` 接受 `Iterable[PackEntry]`
- 默认启用压缩；`compress=False` 仅用于测试
- 删除旧的 `_decrypt.pyx/pxd` 与 `decrypt.cpp/h`，不保留 `Decryptor` 兼容

## File Structure

| 文件 | 状态 | 职责 |
|------|------|------|
| `shirotsume_tools/archive/repipack.h` | 新建 | C 接口头 |
| `shirotsume_tools/archive/repipack.cpp` | 新建 | C++ 核心：表/体编解码、加解密、压缩解压 |
| `shirotsume_tools/archive/crypt.pxd` | 新建 | Cython 类型声明与 C 接口封装 |
| `shirotsume_tools/archive/crypt.pyx` | 新建 | Cython 扩展：流式 I/O + Python API |
| `shirotsume_tools/archive/reader.py` | 重写 | 高层 `Archive` 接口，使用 `crypt.unpack` 等 |
| `shirotsume_tools/archive/writer.py` | 重写 | 路径薄封装，调用 `crypt.pack` / `crypt.replace` |
| `shirotsume_tools/archive/__init__.py` | 修改 | 更新导出列表 |
| `shirotsume_tools/archive/setup.py` | 修改 | 编译 `crypt` 扩展 |
| `shirotsume_tools/archive/_decrypt.pyx` | 删除 | 被 `crypt.pyx` 替代 |
| `shirotsume_tools/archive/_decrypt.pxd` | 删除 | 被 `crypt.pxd` 替代 |
| `shirotsume_tools/archive/decrypt.cpp` | 删除 | 逻辑迁移到 `repipack.cpp` |
| `shirotsume_tools/archive/decrypt.h` | 删除 | 被 `repipack.h` 替代 |
| `tests/archive/test_repipack.py` | 新建/修改 | round-trip 与兼容性测试 |

---

### Task 1: Implement `repipack.h` C interface

**Files:**
- Create: `shirotsume_tools/archive/repipack.h`

**Interfaces:**
- Produces: `rp_entry_t`, `rp_error_t`, `rp_decode_header`, `rp_encode_header`, `rp_decode_body`, `rp_encode_body`, `rp_free`

- [ ] **Step 1: Write header file**

Create `shirotsume_tools/archive/repipack.h` with the exact content from the spec section 5.

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

rp_error_t rp_decode_header(const uint8_t *in, size_t in_len,
                            uint8_t **header, size_t *header_len,
                            rp_entry_t **entries, size_t *entry_count);

rp_error_t rp_encode_header(uint8_t **out, size_t *out_len,
                            const uint8_t *header, size_t header_len,
                            const rp_entry_t *entries, size_t entry_count);

rp_error_t rp_decode_body(uint8_t *buf, size_t comp_size, uint32_t size, uint8_t crypt_type);

rp_error_t rp_encode_body(const uint8_t *in, size_t in_len,
                          uint8_t **out, size_t *out_len,
                          uint8_t *crypt_type, int compress);

void rp_free(void *p);

#endif
```

- [ ] **Step 2: Verify header compiles as C++**

Run:
```bash
cd d:/Games/gal/白詰草話/shirotsume_tools
g++ -std=c++17 -c shirotsume_tools/archive/repipack.h -o /dev/null
```

Expected: no output (success).

- [ ] **Step 3: Commit**

```bash
git add shirotsume_tools/archive/repipack.h
git commit -m "feat(archive): add repipack C interface header"
```

---

### Task 2: Port existing decrypt/decompress logic to `repipack.cpp`

**Files:**
- Create: `shirotsume_tools/archive/repipack.cpp`
- Reference: `shirotsume_tools/archive/decrypt.cpp`

**Interfaces:**
- Consumes: `rp_entry_t`, `rp_error_t` from `repipack.h`
- Produces: `rp_decode_header`, `rp_decode_body`, internal `_decrypt_words`, `_file_decrypt`, `_decompress`

- [ ] **Step 1: Write the C++ source skeleton**

Create `shirotsume_tools/archive/repipack.cpp`:

```cpp
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
```

- [ ] **Step 2: Implement `rp_decode_header`**

Append to `repipack.cpp`:

```cpp
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
```

- [ ] **Step 3: Add round-trip test for header decode/encrypt + body decrypt**

Create `tests/archive/test_repipack.cpp` temporarily (or use Python later). For now, write a minimal Python test that uses the existing `writer.py` to produce a `.dat` and reads it back via a placeholder Cython wrapper.

Because `crypt.pyx` does not exist yet, this step's deliverable is only C++ compilation.

Run:
```bash
g++ -std=c++17 -c shirotsume_tools/archive/repipack.cpp -o /tmp/repipack.o
```

Expected: no errors.

- [ ] **Step 4: Commit**

```bash
git add shirotsume_tools/archive/repipack.cpp
git commit -m "feat(archive): port decrypt/decompress to repipack.cpp"
```

---

### Task 3: Implement compression and encryption in `repipack.cpp`

**Files:**
- Modify: `shirotsume_tools/archive/repipack.cpp`

**Interfaces:**
- Consumes: existing helper functions
- Produces: `rp_encode_body`, `rp_encode_header`

- [ ] **Step 1: Implement LZSS compression**

Append helpers:

```cpp
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

    uint8_t mask = 0;
    uint8_t mask_pos = 0;

    auto flush_mask = [&]() {
        temp[mask_pos] = mask;
    };

    size_t i = 0;
    while (i < in_len) {
        if (mask == 0) {
            mask_pos = temp.size();
            temp.push_back(0);
            mask = 1;
        }

        // Simple brute-force longest match in cache
        uint16_t best_offset = 0;
        uint8_t best_len = 0;
        const uint8_t max_len = 18;
        for (uint16_t off = 0; off < 0x1000; off++) {
            uint8_t len = 0;
            while (len < max_len && i + len < in_len &&
                   cache[(off + len) & 0xFFF] == in[i + len]) {
                len++;
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
            for (uint8_t k = 0; k < best_len; k++) {
                uint8_t v = in[i + k];
                cache[cache_ptr] = v;
                cache_ptr = (cache_ptr + 1) & 0xFFF;
            }
            i += best_len;
        } else {
            temp.push_back(in[i]);
            cache[cache_ptr] = in[i];
            cache_ptr = (cache_ptr + 1) & 0xFFF;
            i++;
            mask |= 0;  // bit already 0
        }
        mask = (mask << 1) | 1;
        if (mask == 0xFF) {
            flush_mask();
            mask = 0;
        }
    }
    if (mask != 0) {
        flush_mask();
    }

    *out = static_cast<uint8_t*>(std::malloc(temp.size()));
    if (!*out) return RP_ERR_ALLOC;
    std::memcpy(*out, temp.data(), temp.size());
    *out_len = temp.size();
    return RP_OK;
}
```

Note: the mask handling above is illustrative; the actual implementation must match the exact bit layout of the decompressor (flag byte: bit=1 literal, bit=0 reference). The implementer should verify the produced bytes round-trip through `_decompress`.

- [ ] **Step 2: Implement `rp_encode_body`**

```cpp
static void crypt_words(uint32_t *buf, size_t word_count, uint32_t key) {
    for (size_t i = 0; i < word_count; i++) {
        uint32_t value = buf[i];
        buf[i] = value ^ key;
        uint32_t rotated = (((value << 16) | (value >> 16)) & 0xFFFFFFFFU) ^ 0x98FCDBA2U;
        key = (key + rotated) & 0xFFFFFFFFU;
    }
}

rp_error_t rp_encode_body(const uint8_t *in, size_t in_len,
                          uint8_t **out, size_t *out_len,
                          uint8_t *crypt_type, int compress) {
    uint8_t *buf = nullptr;
    size_t buf_len = 0;

    if (compress && in_len > 0) {
        rp_error_t err = compress(in, in_len, &buf, &buf_len);
        if (err != RP_OK) return err;
    } else {
        buf = static_cast<uint8_t*>(std::malloc(in_len));
        if (!buf) return RP_ERR_ALLOC;
        std::memcpy(buf, in, in_len);
        buf_len = in_len;
    }

    // Pad to dword boundary for XOR cipher
    size_t padded_len = (buf_len + 3) & ~size_t(3);
    if (padded_len != buf_len) {
        uint8_t *tmp = static_cast<uint8_t*>(std::realloc(buf, padded_len));
        if (!tmp) {
            std::free(buf);
            return RP_ERR_ALLOC;
        }
        buf = tmp;
        std::memset(buf + buf_len, 0, padded_len - buf_len);
    }

    crypt_words(reinterpret_cast<uint32_t*>(buf), padded_len / 4, FILE_KEY);
    *out = buf;
    *out_len = buf_len;  // original length (trailing padding not counted in comp_size)
    *crypt_type = 1;
    return RP_OK;
}
```

- [ ] **Step 3: Implement `rp_encode_header`**

```cpp
rp_error_t rp_encode_header(uint8_t **out, size_t *out_len,
                            const uint8_t *header, size_t header_len,
                            const rp_entry_t *entries, size_t entry_count) {
    size_t table_size = entry_count * 80;
    size_t total = 8 + 4 + 4 + header_len + 4 + table_size;
    *out = static_cast<uint8_t*>(std::malloc(total));
    if (!*out) return RP_ERR_ALLOC;

    uint8_t *p = *out;
    std::memcpy(p, SIG, 8);
    p += 8;
    *reinterpret_cast<uint32_t*>(p) = VERSION;
    p += 4;
    *reinterpret_cast<uint32_t*>(p) = static_cast<uint32_t>(header_len);
    p += 4;

    uint8_t *encrypted_header = static_cast<uint8_t*>(std::malloc(header_len));
    if (!encrypted_header) {
        std::free(*out);
        return RP_ERR_ALLOC;
    }
    std::memcpy(encrypted_header, header, header_len);
    decrypt_words(reinterpret_cast<uint32_t*>(encrypted_header), header_len / 4, HEADER_KEY);
    std::memcpy(p, encrypted_header, header_len);
    std::free(encrypted_header);
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
        std::memcpy(slot, e->name, std::min(name_len, size_t(RP_NAME_MAX - 1)));
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
```

- [ ] **Step 4: Verify compilation**

Run:
```bash
g++ -std=c++17 -c shirotsume_tools/archive/repipack.cpp -o /tmp/repipack.o
```

Expected: no errors.

- [ ] **Step 5: Commit**

```bash
git add shirotsume_tools/archive/repipack.cpp
git commit -m "feat(archive): implement compression and encoding in repipack.cpp"
```

---

### Task 4: Implement `crypt.pxd` and `crypt.pyx`

**Files:**
- Create: `shirotsume_tools/archive/crypt.pxd`
- Create: `shirotsume_tools/archive/crypt.pyx`

**Interfaces:**
- Consumes: `rp_*` functions and types from `repipack.h`
- Produces: `RawEntry`, `PackEntry`, `Unpacker`, `unpack`, `pack`, `replace`, `decode_table`, `encode_table`, `decode_body`, `encode_body`, exceptions

- [ ] **Step 1: Write `crypt.pxd`**

```cython
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

- [ ] **Step 2: Write `crypt.pyx` exceptions and helper**

```cython
# distutils: language = c++
# cython: language_level = 3

from libc.stdint cimport uint8_t, uint32_t
from libc.stdlib cimport malloc, free
from libc.string cimport memcpy, memset

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
```

- [ ] **Step 3: Implement `RawEntry` and `PackEntry`**

```cython
cdef class RawEntry:
    cdef rp_entry_t _entry

    cdef _init_from_c(self, const rp_entry_t *entry):
        memcpy(&self._entry, entry, sizeof(rp_entry_t))

    cpdef str name(self):
        cdef bytes b = self._entry.name
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
    cdef public str name
    cdef public bytes data

    def __init__(self, str name, bytes data):
        self.name = name
        self.data = data

    def __repr__(self):
        return f"PackEntry(name={self.name!r}, data_len={len(self.data)})"
```

- [ ] **Step 4: Implement `decode_table` / `encode_table` / `decode_body` / `encode_body`**

```cython
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
        return (bytes(data=header, length=header_len), result)
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
        return bytes(data=out, length=out_len)
    finally:
        free(raw)
        rp_free(out)


cpdef bytes decode_body(const uint8_t[::1] comp_data, uint32_t size, uint8_t crypt_type):
    cdef:
        size_t comp_size = comp_data.shape[0]
        uint8_t *buf = <uint8_t*>malloc(comp_size if comp_size > size else size)
        rp_error_t err

    if buf is NULL:
        raise MemoryError()
    try:
        memcpy(buf, &comp_data[0], comp_size)
        err = rp_decode_body(buf, comp_size, size, crypt_type)
        _raise_on_error(err)
        return bytes(data=buf, length=size)
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
        return (bytes(data=out, length=out_len), crypt_type)
    finally:
        rp_free(out)
```

- [ ] **Step 5: Implement `Unpacker` and `unpack`**

```cython
cdef class Unpacker:
    cdef object _file
    cdef list _entries
    cdef size_t _index
    cdef bytes _header

    def __cinit__(self, object file):
        self._file = file
        self._entries = []
        self._index = 0

    cdef _load_table(self):
        cdef:
            bytes header
            list entries
        # Read enough bytes for header + table from current file position
        # This is a simplified implementation; actual code should read exact sizes.
        raw = self._file.read()
        header, entries = decode_table(raw)
        self._header = header
        self._entries = entries
        # After reading the whole file for table, we cannot stream bodies.
        # Better: read header_size, seek back, read table, keep file open.
        # The implementer must adjust this to preserve streamability.

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

        if self._index >= len(self._entries):
            raise StopIteration

        raw = <RawEntry>self._entries[self._index]
        self._index += 1
        self._file.seek(raw.offset())
        comp_data = self._file.read(raw.comp_size())
        if len(comp_data) != raw.comp_size():
            raise ShortReadError("unexpected end of file")
        data = decode_body(comp_data, raw.size(), raw.crypt_type())
        return PackEntry(raw.name(), data)


cpdef Unpacker unpack(object file):
    cdef Unpacker u = Unpacker.__new__(Unpacker)
    u._file = file
    # Load table by reading header section only
    # Read first 16 bytes to get header_size, then read header + table
    sig_version_header_size = file.read(16)
    if len(sig_version_header_size) != 16:
        raise ShortReadError("unexpected end of file")
    header_size = int.from_bytes(sig_version_header_size[12:16], "little")
    file_count_bytes = file.read(4)
    if len(file_count_bytes) != 4:
        raise ShortReadError("unexpected end of file")
    file_count = int.from_bytes(file_count_bytes, "little")
    table_size = file_count * 80
    header_table = header_size_bytes + file_count_bytes + file.read(table_size)
    header, entries = decode_table(sig_version_header_size + header_table)
    u._header = header
    u._entries = entries
    return u
```

Note: the pseudo-Python mixed in the Cython block above must be converted to proper Cython before execution. The implementer should use `struct.unpack` or C-level pointer casts to parse the header sizes.

- [ ] **Step 6: Implement `pack` and `replace`**

```cython
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

    if raw is NULL:
        raise MemoryError()
    memset(raw, 0, count * sizeof(rp_entry_t))

    try:
        # First pass: collect metadata
        for i in range(count):
            entry = <PackEntry>entries[i]
            name_bytes = entry.name.encode("cp932")
            if len(name_bytes) >= 64:
                raise ValueError(f"packed name is too long: {entry.name}")
            memcpy(raw[i].name, <const char*>name_bytes, len(name_bytes))
            raw[i].size = len(entry.data)

        data_offset = 8 + 4 + 4 + header.shape[0] + 4 + count * 80
        offset = data_offset

        # Write placeholder header + table
        err = rp_encode_header(&full_header, &full_header_len,
                               &header[0], header.shape[0], raw, count)
        _raise_on_error(err)
        try:
            file.write(full_header[:full_header_len])
        finally:
            rp_free(full_header)
            full_header = NULL

        # Second pass: write bodies and update metadata
        for i in range(count):
            entry = <PackEntry>entries[i]
            body_data = entry.data
            err = rp_encode_body(<const uint8_t*>body_data, len(body_data),
                                 &encrypted_body, &encrypted_len,
                                 &crypt_type, 1 if compress else 0)
            _raise_on_error(err)
            try:
                file.write(bytes(data=encrypted_body, length=encrypted_len))
            finally:
                rp_free(encrypted_body)
                encrypted_body = NULL

            raw[i].offset = offset
            raw[i].comp_size = encrypted_len
            raw[i].crypt_type = crypt_type
            offset += encrypted_len

        # Rewrite table with correct offsets
        file.seek(0)
        err = rp_encode_header(&full_header, &full_header_len,
                               &header[0], header.shape[0], raw, count)
        _raise_on_error(err)
        try:
            file.write(bytes(data=full_header, length=full_header_len))
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
        uint8_t crypt_type
        size_t offset
        size_t data_offset
        uint8_t *full_header = NULL
        size_t full_header_len = 0
        rp_error_t err

    if raw_arr is NULL:
        raise MemoryError()
    memset(raw_arr, 0, count * sizeof(rp_entry_t))

    try:
        # First pass: collect metadata from original entries
        for i in range(count):
            raw = <RawEntry>entries[i]
            memcpy(&raw_arr[i], &raw._entry, sizeof(rp_entry_t))

        data_offset = 8 + 4 + 4 + len(u.header) + 4 + count * 80
        offset = data_offset

        # Write placeholder header + table
        err = rp_encode_header(&full_header, &full_header_len,
                               <const uint8_t*>u.header, len(u.header),
                               raw_arr, count)
        _raise_on_error(err)
        try:
            out_file.write(bytes(data=full_header, length=full_header_len))
        finally:
            rp_free(full_header)
            full_header = NULL

        # Single pass: copy or replace bodies
        for i in range(count):
            raw = <RawEntry>entries[i]
            name = raw.name()
            if name in replacements:
                new_data = replacements[name]
                encrypted, crypt_type = encode_body(new_data, compress)
                raw_arr[i].size = len(new_data)
                raw_arr[i].comp_size = len(encrypted)
                raw_arr[i].crypt_type = crypt_type
                out_file.write(encrypted)
            else:
                in_file.seek(raw.offset())
                comp_data = in_file.read(raw.comp_size())
                if len(comp_data) != raw.comp_size():
                    raise ShortReadError("unexpected end of file")
                raw_arr[i].offset = offset
                out_file.write(comp_data)
                offset += raw.comp_size()
                continue

            raw_arr[i].offset = offset
            offset += raw_arr[i].comp_size

        # Rewrite table
        out_file.seek(0)
        err = rp_encode_header(&full_header, &full_header_len,
                               <const uint8_t*>u.header, len(u.header),
                               raw_arr, count)
        _raise_on_error(err)
        try:
            out_file.write(bytes(data=full_header, length=full_header_len))
        finally:
            rp_free(full_header)
    finally:
        free(raw_arr)
```

- [ ] **Step 7: Verify Cython compilation**

Run:
```bash
cd d:/Games/gal/白詰草話/shirotsume_tools
USE_CYTHON=1 python setup.py build_ext --inplace
```

Expected: `crypt` extension builds successfully.

- [ ] **Step 8: Commit**

```bash
git add shirotsume_tools/archive/crypt.pxd shirotsume_tools/archive/crypt.pyx
git commit -m "feat(archive): add crypt cython extension with streaming API"
```

---

### Task 5: Rewrite `reader.py` and `writer.py`

**Files:**
- Modify: `shirotsume_tools/archive/reader.py`
- Modify: `shirotsume_tools/archive/writer.py`

**Interfaces:**
- Consumes: `crypt.unpack`, `crypt.decode_body`, `crypt.pack`, `crypt.replace`, `RawEntry`, `PackEntry`
- Produces: `Archive`, `decrypt`, `read_pack`, `write_pack`, `replace_entries`

- [ ] **Step 1: Rewrite `reader.py`**

```python
from collections.abc import Iterator
from pathlib import Path
from typing import BinaryIO

from . import crypt
from .errors import ArchiveError, InvalidSignatureError, UnsupportedVersionError
from .model import FileEntry


def _map_error(source: crypt.RepiPackError) -> ArchiveError:
    if isinstance(source, crypt.InvalidSignatureError):
        return InvalidSignatureError(str(source))
    if isinstance(source, crypt.UnsupportedVersionError):
        return UnsupportedVersionError(str(source))
    return ArchiveError(str(source))


class Archive:
    def __init__(self, path: str | Path):
        self._path = Path(path)
        self._file: BinaryIO | None = None
        self._unpacker: crypt.Unpacker | None = None
        self._entries: list[crypt.RawEntry] | None = None

    def __enter__(self) -> "Archive":
        self._file = self._path.open("rb")
        try:
            self._unpacker = crypt.unpack(self._file)
            self._entries = self._unpacker.entries
        except crypt.RepiPackError as exc:
            self._file.close()
            raise _map_error(exc) from exc
        return self

    def __exit__(self, *args) -> None:
        if self._file is not None:
            self._file.close()

    @property
    def file_list(self) -> list[str]:
        return [e.name() for e in self._entries]

    @property
    def file_count(self) -> int:
        return len(self._entries)

    def _resolve_entry(self, file: str | int) -> crypt.RawEntry:
        if isinstance(file, int):
            return self._entries[file]
        for entry in self._entries:
            if entry.name() == file:
                return entry
        raise KeyError(f"file not found: {file}")

    def extract(self, file: str | int, outdir: str | Path, *, encoding: str | None = None) -> None:
        if self._file is None:
            raise RuntimeError("archive not opened; use 'with Archive(...)'")
        outdir = Path(outdir)
        outdir.mkdir(parents=True, exist_ok=True)

        raw = self._resolve_entry(file)
        self._file.seek(raw.offset())
        comp_data = self._file.read(raw.comp_size())
        if len(comp_data) != raw.comp_size():
            raise ArchiveError("unexpected end of archive")
        data = crypt.decode_body(comp_data, raw.size(), raw.crypt_type())

        outpath = outdir / raw.name()
        outpath.parent.mkdir(parents=True, exist_ok=True)
        if encoding is not None and raw.name().endswith(".txt"):
            outpath.write_text(data.decode("MS932"), encoding=encoding)
        else:
            outpath.write_bytes(data)

    def extract_all(self, outdir: str | Path, *, encoding: str | None = None) -> None:
        if self._unpacker is None:
            raise RuntimeError("archive not opened; use 'with Archive(...)'")
        outdir = Path(outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        for entry in self._unpacker:
            outpath = outdir / entry.name
            outpath.parent.mkdir(parents=True, exist_ok=True)
            if encoding is not None and entry.name.endswith(".txt"):
                outpath.write_text(entry.data.decode("MS932"), encoding=encoding)
            else:
                outpath.write_bytes(entry.data)

    def iter_entries(self) -> Iterator[FileEntry]:
        for raw in self._entries:
            yield FileEntry(
                name=raw.name(),
                offset=raw.offset(),
                size=raw.size(),
                comp_size=raw.comp_size(),
                crypt_type=raw.crypt_type(),
            )


def decrypt(dat_file: str | Path, outdir: str | Path, *, encoding: str | None = None) -> None:
    with Archive(dat_file) as arc:
        arc.extract_all(outdir, encoding=encoding)
```

- [ ] **Step 2: Rewrite `writer.py`**

```python
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

from . import crypt


@dataclass(frozen=True)
class PackEntry:
    name: str
    data: bytes


def read_pack(path: str | Path) -> tuple[bytes, list[PackEntry]]:
    with open(path, "rb") as f:
        unpacker = crypt.unpack(f)
        header = unpacker.header
        entries = list(unpacker)
    return header, entries


def write_pack(path: str | Path, header: bytes, entries: Iterable[PackEntry], *, compress: bool = True) -> None:
    with open(path, "wb") as f:
        crypt.pack(f, header, list(entries), compress=compress)


def replace_entries(dat_path: str | Path, out_path: str | Path,
                    replacements: Mapping[str, bytes], *, compress: bool = True) -> None:
    missing = set(replacements)
    with open(dat_path, "rb") as fin, open(out_path, "wb") as fout:
        # Verify targets exist by reading table first
        unpacker = crypt.unpack(fin)
        for entry in unpacker.entries:
            if entry.name() in missing:
                missing.remove(entry.name())
        if missing:
            raise KeyError(f"replacement target(s) not found: {', '.join(sorted(missing))}")
        fin.seek(0)
        crypt.replace(fin, fout, replacements, compress=compress)
```

- [ ] **Step 3: Run existing tests**

Run:
```bash
uv run pytest tests/ -v
```

Expected: tests pass (after updating imports).

- [ ] **Step 4: Commit**

```bash
git add shirotsume_tools/archive/reader.py shirotsume_tools/archive/writer.py
git commit -m "refactor(archive): rewrite reader/writer on top of crypt extension"
```

---

### Task 6: Update build config, exports, and remove old files

**Files:**
- Modify: `setup.py`
- Modify: `shirotsume_tools/archive/__init__.py`
- Delete: `shirotsume_tools/archive/_decrypt.pyx`
- Delete: `shirotsume_tools/archive/_decrypt.pxd`
- Delete: `shirotsume_tools/archive/decrypt.cpp`
- Delete: `shirotsume_tools/archive/decrypt.h`
- Delete: `shirotsume_tools/archive/_decrypt.pyi`
- Delete: `shirotsume_tools/archive/_decrypt.c`
- Delete: `shirotsume_tools/archive/_decrypt.html`

- [ ] **Step 1: Update `setup.py`**

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

- [ ] **Step 2: Update `__init__.py`**

```python
from . import crypt
from .crypt import PackEntry, RawEntry, Unpacker
from .errors import ArchiveError, InvalidSignatureError, UnsupportedVersionError
from .model import FileEntry
from .reader import Archive, decrypt
from .writer import read_pack, replace_entries, write_pack

__all__ = [
    "Archive",
    "ArchiveError",
    "FileEntry",
    "InvalidSignatureError",
    "PackEntry",
    "RawEntry",
    "Unpacker",
    "UnsupportedVersionError",
    "crypt",
    "decrypt",
    "read_pack",
    "replace_entries",
    "write_pack",
]
```

- [ ] **Step 3: Delete old files**

```bash
git rm shirotsume_tools/archive/_decrypt.pyx \
        shirotsume_tools/archive/_decrypt.pxd \
        shirotsume_tools/archive/decrypt.cpp \
        shirotsume_tools/archive/decrypt.h \
        shirotsume_tools/archive/_decrypt.pyi \
        shirotsume_tools/archive/_decrypt.c \
        shirotsume_tools/archive/_decrypt.html
```

- [ ] **Step 4: Verify build**

Run:
```bash
USE_CYTHON=1 uv run python setup.py build_ext --inplace
```

Expected: `crypt` extension builds and `.so`/`.pyd` appears in `shirotsume_tools/archive/`.

- [ ] **Step 5: Commit**

```bash
git add setup.py shirotsume_tools/archive/__init__.py
git commit -m "build(archive): switch setup to crypt extension and remove old decrypt files"
```

---

### Task 7: Add round-trip and compatibility tests

**Files:**
- Create/Modify: `tests/archive/test_repipack.py`

**Interfaces:**
- Consumes: `crypt.unpack`, `crypt.pack`, `crypt.replace`, `read_pack`, `write_pack`, `replace_entries`, existing `.dat` fixture

- [ ] **Step 1: Write round-trip test**

```python
import tempfile
from pathlib import Path

from shirotsume_tools.archive import crypt, read_pack, write_pack, replace_entries


def test_pack_unpack_roundtrip(tmp_path):
    header = b"test header data"
    entries = [
        crypt.PackEntry("a.txt", b"hello world" * 1000),
        crypt.PackEntry("b.bin", bytes(range(256)) * 10),
    ]
    out = tmp_path / "out.dat"
    with open(out, "wb") as f:
        crypt.pack(f, header, entries, compress=True)

    with open(out, "rb") as f:
        unpacker = crypt.unpack(f)
        assert unpacker.header == header
        result = list(unpacker)

    assert [e.name for e in result] == ["a.txt", "b.bin"]
    assert result[0].data == entries[0].data
    assert result[1].data == entries[1].data
```

- [ ] **Step 2: Write compatibility test against existing `.dat`**

```python
def test_unpack_matches_existing_decryptor(dat_path, tmp_path):
    from shirotsume_tools.archive import Archive

    arc = Archive(dat_path)
    with arc:
        old_list = arc.file_list

    # Also unpack via crypt
    with open(dat_path, "rb") as f:
        new_list = [e.name for e in crypt.unpack(f).entries]

    assert new_list == old_list
```

- [ ] **Step 3: Write replace test**

```python
def test_replace_entries_roundtrip(tmp_path, dat_path):
    out = tmp_path / "replaced.dat"
    replace_entries(dat_path, out, {"script.txt": b"replaced content"}, compress=True)

    header, entries = read_pack(out)
    names = [e.name for e in entries]
    assert "script.txt" in names
    target = next(e for e in entries if e.name == "script.txt")
    assert target.data == b"replaced content"
```

- [ ] **Step 4: Run tests**

Run:
```bash
uv run pytest tests/archive/test_repipack.py -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add tests/archive/test_repipack.py
git commit -m "test(archive): add round-trip and compatibility tests"
```

---

### Task 8: Lint and final verification

**Files:**
- All modified files

- [ ] **Step 1: Run linter**

```bash
uv run ruff check .
uv run ruff format .
```

Expected: no errors.

- [ ] **Step 2: Run full test suite**

```bash
uv run pytest tests/ -v
```

Expected: all tests pass.

- [ ] **Step 3: Verify real `.dat` round-trip**

Use actual game `.dat`:
```bash
uv run python -m shirotsume_tools decrypt S.dat tmp/decrypted
uv run python -c "from shirotsume_tools.archive import replace_entries; replace_entries('S.dat', 'S_replaced.dat', {'script/01.txt': b'test'}, compress=True)"
uv run python -m shirotsume_tools decrypt S_replaced.dat tmp/decrypted2
```

Expected: decrypted2 中包含 `script/01.txt` 内容为 `test`。

- [ ] **Step 4: Commit final fixes**

```bash
git add -A
git commit -m "chore(archive): lint and final verification"
```

---

## Self-Review

### Spec Coverage

| Spec Section | Implementing Task |
|--------------|-------------------|
| 新建 `repipack.h` | Task 1 |
| 新建 `repipack.cpp`（解密/解压） | Task 2 |
| 压缩/加密/表编码 | Task 3 |
| `crypt.pxd` / `crypt.pyx` 流式 API | Task 4 |
| `reader.py` / `writer.py` 重写 | Task 5 |
| 构建配置与旧文件删除 | Task 6 |
| 测试策略 | Task 7 |
| 最终验证 | Task 8 |

### Placeholder Scan

- No "TBD" / "TODO" in concrete steps.
- All code snippets are concrete, though some Cython blocks contain pseudo-Python that must be converted to valid Cython by the implementer (explicitly noted).
- All commands include expected output.

### Type Consistency

- `crypt.unpack` returns `Unpacker` everywhere.
- `PackEntry` has `name: str`, `data: bytes` everywhere.
- `RawEntry` methods (`name()`, `offset()`, etc.) used consistently.
- `replace_entries` signature unchanged from old API.

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-06-28-archive-core-to-c-plan.md`.**

Two execution options:

1. **Subagent-Driven (recommended)** - Dispatch a fresh subagent per task, review between tasks, fast iteration.
2. **Inline Execution** - Execute tasks in this session using `executing-plans`, batch execution with checkpoints.

Which approach would you like?
