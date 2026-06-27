# 迁移 trans-tool 重构到 shirotsume_tools 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 `trans-tool/shirotsume_tools/` 的模块化重构架构迁移到已发布包 `shirotsume_tools/`,同时把 OpenAI 翻译流水线深度整合进新架构的 `translation/` 子模块和 `archive/writer.py`。

**Architecture:** 以 trans-tool 的重构为基线(archive/parser/index/export/cli 五模块 + pydantic v2 + koilang + typer),把目标包的 `translate_agent.py`/`script_patch.py`/`custom_encoding.py` 迁入 `translation/`(agent.py/patch.py/encoding.py),`repack.py` 迁入 `archive/writer.py`。数据模型统一到 `parser.TextEntry`,parser 提取器扩展到 5 个函数。不保留旧 API,openai 设为可选 `[translation]` extra。

**Tech Stack:** Python 3.10+, pydantic v2, koilang, antlr4-python3-runtime, typer, Cython 3, openai(optional), pandas/openpyxl(optional)

## Global Constraints

- 目标仓库根:`d:\Games\gal\白詰草話\shirotsume_tools`(git 仓库,user=ovizro)
- 源重构包:`d:\Games\gal\白詰草話\trans-tool\shirotsume_tools\`
- 源测试:`d:\Games\gal\白詰草話\trans-tool\tests\`
- Python >=3.10;版本号 `0.2.0`
- `__init__.py` 只做导入/导出,不含实现代码
- `Runtime` 类不继承,用 `env_enter`/`env_exit` 推环境栈
- 不保留旧 API 别名(MyIndex/parse/parse_file/get_counter/reset_counter/build_dataframe/Decryptor)
- openai 延迟导入,`ModuleNotFoundError` 转 `RuntimeError` 提示装 `[translation]` extra
- PowerShell 环境,用 `Copy-Item` 复制文件

## File Structure

| 文件 | 动作 | 责任 |
|------|------|------|
| `pyproject.toml` | 覆盖 | 依赖(核心+[export]+[translation]+[dev])、构建配置、ruff/pyright |
| `setup.py` | 覆盖 | Cython 扩展 `shirotsume_tools.archive._decrypt` |
| `setup.cfg` | 删除 | 无关紧要 |
| `PKG-INFO` | 删除 | 构建产物 |
| `shirotsume_tools/_version.py` | 覆盖 | `__version__ = "0.2.0"` |
| `shirotsume_tools/__init__.py` | 覆盖 | 导出 archive/cli/export/index/parser/translation |
| `shirotsume_tools/__main__.py` | 覆盖 | `from .cli import app; app()` |
| `shirotsume_tools/archive/*` | 复制+新增 | reader/model/errors/_decrypt.* 从 trans-tool 复制;writer.py 新建 |
| `shirotsume_tools/parser/*` | 复制+修改 | 从 trans-tool 复制;listener.py 扩展 5 函数;core.py 加 parse_script_text |
| `shirotsume_tools/index/*` | 复制 | 从 trans-tool 复制 |
| `shirotsume_tools/export/*` | 复制 | 从 trans-tool 复制 |
| `shirotsume_tools/translation/*` | 新建 | agent.py/patch.py/encoding.py/errors.py/__init__.py |
| `shirotsume_tools/cli/*` | 复制+修改 | 从 trans-tool 复制;commands.py 加 3 翻译命令;__init__.py 注册 6 命令 |
| `tests/*` | 复制+修改+新增 | 从 trans-tool 复制;test_scaffold 加 translation;新增 test_translation.py |
| 旧扁平文件 | 删除 | decrypt.pyx/.c/_decrypt.cpp/.h/.pxd/.pyi、myindex.py、repack.py、script_patch.py、translate_agent.py、custom_encoding.py |

---

### Task 1: 构建配置与版本号

**Files:**
- Overwrite: `pyproject.toml`
- Overwrite: `setup.py`
- Overwrite: `shirotsume_tools/_version.py`
- Delete: `setup.cfg`, `PKG-INFO`

**Interfaces:**
- Produces: 构建配置就绪,版本 `0.2.0`

- [ ] **Step 1: 覆盖 `pyproject.toml`**

```toml
[build-system]
requires = ["setuptools>=61.0", "Cython>=3.0"]
build-backend = "setuptools.build_meta"

[project]
name = "shirotsume_tools"
dynamic = ["version"]
description = "tools for shirotsume"
license = "GPL-3.0-or-later"
authors = [
    {name = "Moe"},
    {name = "Ovizro", email = "Ovizro@visecy.org"},
]
requires-python = ">=3.10"
classifiers = [
    "Programming Language :: Python :: 3",
    "Operating System :: OS Independent",
]
dependencies = [
    "typing_extensions",
    "antlr4-python3-runtime>=4.13",
    "KoiLang>=2.0.0b1",
    "pydantic>=2.0",
    "typer>=0.9.0",
]

[project.optional-dependencies]
export = ["pandas", "openpyxl"]
translation = ["openai>=1.0.0"]
dev = ["ruff", "coverage", "pytest", "cython"]

[project.urls]
Homepage = "https://github.com/Ovizro/shirotsume_tools"

[tool.setuptools]
package-data = {"*" = ["*.pyi", "*.pyx", "*.pxd", "*.h", "*.g4"]}

[tool.setuptools.dynamic]
version = {attr = "shirotsume_tools._version.__version__"}

[tool.setuptools.packages.find]
where = ["."]
include = ["shirotsume_tools*"]
exclude = ["build*", "tests*"]

[tool.ruff]
line-length = 127
target-version = "py310"
exclude = [
    "shirotsume_tools/parser/Shirotsume*.py",
    "build",
    "dist",
]

[tool.ruff.lint]
select = ["E", "F", "W", "I", "UP", "B", "C4", "SIM", "RUF"]
ignore = ["E402", "B008"]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]

[tool.ruff.lint.isort]
known-first-party = ["shirotsume_tools"]

[tool.ruff.format]
line-ending = "lf"

[tool.pyright]
include = ["shirotsume_tools", "tests"]
exclude = [
    "shirotsume_tools/parser/Shirotsume*.py",
    ".venv",
    "build",
    "dist",
]
pythonVersion = "3.10"
typeCheckingMode = "standard"
reportMissingTypeStubs = "none"
reportPossiblyUnboundVariable = "warning"
```

- [ ] **Step 2: 覆盖 `setup.py`**

```python
import os
from setuptools import setup, Extension


USE_CYTHON = "USE_CYTHON" in os.environ
FILE_SUFFIX = ".pyx" if USE_CYTHON else ".c"

extensions = [
    Extension(
        "shirotsume_tools.archive._decrypt",
        [
            "shirotsume_tools/archive/_decrypt" + FILE_SUFFIX,
            "shirotsume_tools/archive/_decrypt.cpp",
        ],
    ),
]

if USE_CYTHON:
    from Cython.Build import cythonize

    extensions = cythonize(
        extensions,
        annotate=True,
        compiler_directives={"language_level": "3"},
    )


setup(
    ext_modules=extensions,
)
```

- [ ] **Step 3: 覆盖 `shirotsume_tools/_version.py`**

```python
__version__ = "0.2.0"
```

- [ ] **Step 4: 删除 `setup.cfg` 和 `PKG-INFO`**

Run: `Remove-Item setup.cfg, PKG-INFO -Force`

- [ ] **Step 5: 提交**

```bash
git add pyproject.toml setup.py shirotsume_tools/_version.py
git rm setup.cfg PKG-INFO
git commit -m "chore: update build config and version to 0.2.0"
```

---

### Task 2: 复制重构后的核心模块与测试

**Files:**
- Copy: `shirotsume_tools/archive/` (reader.py, model.py, errors.py, _decrypt.pyx, _decrypt.pxd, _decrypt.pyi, _decrypt.cpp, _decrypt.h, __init__.py)
- Copy: `shirotsume_tools/parser/` (全部,含 ANTLR 生成文件 + core.py/listener.py/model.py/errors.py/__init__.py)
- Copy: `shirotsume_tools/index/` (core.py, io.py, model.py, __init__.py)
- Copy: `shirotsume_tools/export/` (core.py, __init__.py)
- Copy: `shirotsume_tools/cli/` (commands.py, logging_config.py, __init__.py)
- Overwrite: `shirotsume_tools/__init__.py`, `shirotsume_tools/__main__.py`
- Copy: `tests/` (conftest.py, test_archive.py, test_archive_decrypt.py, test_parser.py, test_index.py, test_export.py, test_cli.py, test_scaffold.py)

**Interfaces:**
- Produces: 可导入的 5 子模块包(archive/parser/index/export/cli),tests/ 可运行

- [ ] **Step 1: 复制 archive/ 目录**

Run:
```powershell
Copy-Item -Path "..\trans-tool\shirotsume_tools\archive" -Destination "shirotsume_tools\archive" -Recurse -Force
```

- [ ] **Step 2: 复制 parser/ 目录(覆盖旧版)**

Run:
```powershell
Remove-Item -Path "shirotsume_tools\parser" -Recurse -Force
Copy-Item -Path "..\trans-tool\shirotsume_tools\parser" -Destination "shirotsume_tools\parser" -Recurse -Force
```

- [ ] **Step 3: 复制 index/、export/、cli/ 目录**

Run:
```powershell
Copy-Item -Path "..\trans-tool\shirotsume_tools\index" -Destination "shirotsume_tools\index" -Recurse -Force
Copy-Item -Path "..\trans-tool\shirotsume_tools\export" -Destination "shirotsume_tools\export" -Recurse -Force
Copy-Item -Path "..\trans-tool\shirotsume_tools\cli" -Destination "shirotsume_tools\cli" -Recurse -Force
```

- [ ] **Step 4: 覆盖 `shirotsume_tools/__init__.py`**

```python
from . import archive, cli, export, index, parser
from ._version import __version__

__all__ = ["__version__", "archive", "cli", "export", "index", "parser"]
```

- [ ] **Step 5: 覆盖 `shirotsume_tools/__main__.py`**

```python
from .cli import app

if __name__ == "__main__":
    app()
```

- [ ] **Step 6: 复制 tests/ 目录**

Run:
```powershell
Copy-Item -Path "..\trans-tool\tests" -Destination "tests" -Recurse -Force
```

- [ ] **Step 7: 安装包并编译 Cython 扩展**

Run:
```powershell
pip install -e .
```
Expected: 成功编译 `shirotsume_tools.archive._decrypt` 扩展。如果 Cython 不可用,设置 `$env:USE_CYTHON=1` 后重新安装。

- [ ] **Step 8: 运行测试验证**

Run: `pytest tests/ -v`
Expected: test_archive/test_parser/test_index/test_export/test_cli/test_scaffold 全部 PASS(test_archive_decrypt 需要 Cython 扩展)。

- [ ] **Step 9: 提交**

```bash
git add shirotsume_tools/archive shirotsume_tools/parser shirotsume_tools/index shirotsume_tools/export shirotsume_tools/cli shirotsume_tools/__init__.py shirotsume_tools/__main__.py tests
git commit -m "feat: migrate refactored modular architecture from trans-tool"
```

---

### Task 3: 扩展 parser 提取器到 5 个函数 + parse_script_text

**Files:**
- Modify: `shirotsume_tools/parser/listener.py` (TEXT_EXTRACTORS 扩展)
- Modify: `shirotsume_tools/parser/core.py` (加 parse_script_text)
- Modify: `shirotsume_tools/parser/__init__.py` (导出 parse_script_text)
- Modify: `tests/test_parser.py` (加 5 函数 + parse_script_text 测试)

**Interfaces:**
- Consumes: `TextEntry` 模型(已存在)
- Produces: `parse_script_text(script: str, *, file_path: str = "", encoding: str = "utf-8") -> list[TextEntry]`;`TEXT_EXTRACTORS` 支持 CreateBalloon/CreateBalloonEx/AddText/CreateBalloonBie/CreateText

- [ ] **Step 1: 写失败测试 —— 5 函数提取 + parse_script_text**

在 `tests/test_parser.py` 末尾追加:

```python
from shirotsume_tools.parser import parse_script_text

FIVE_FUNC_SCRIPT = '''\
page TestPage {
CreateBalloon("a", "balloon text");
CreateBalloonEx("a", "b", "c", "ex text", "e", "f", "g");
CreateBalloonBie("a", "bie text");
CreateText("text content");
AddText("win", "add text");
}
'''


def test_parse_script_text_extracts_all_five_functions():
    entries = parse_script_text(FIVE_FUNC_SCRIPT, file_path="test.txt")
    assert len(entries) == 5
    assert entries[0].text == "balloon text"
    assert entries[1].text == "ex text"
    assert entries[2].text == "bie text"
    assert entries[3].text == "text content"
    assert entries[4].text == "add text"
    assert all(e.file_path == "test.txt" for e in entries)


def test_parse_script_text_sets_start_stop():
    entries = parse_script_text('CreateBalloon("x", "hi");', file_path="t.txt")
    assert len(entries) == 1
    assert entries[0].start < entries[0].stop
    assert entries[0].line >= 1
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_parser.py::test_parse_script_text_extracts_all_five_functions -v`
Expected: FAIL —— `parse_script_text` 不存在;且 CreateBalloonBie/CreateText 不被提取。

- [ ] **Step 3: 扩展 `shirotsume_tools/parser/listener.py` 的 TEXT_EXTRACTORS**

把 `TEXT_EXTRACTORS` 改为:

```python
TEXT_EXTRACTORS = {
    "CreateBalloon":    lambda exprs: exprs[-1],
    "CreateBalloonEx":  lambda exprs: exprs[-4],
    "CreateBalloonBie": lambda exprs: exprs[-1],
    "CreateText":       lambda exprs: exprs[-1],
    "AddText":          lambda exprs: exprs[1],
}
```

- [ ] **Step 4: 在 `shirotsume_tools/parser/core.py` 加 parse_script_text**

在 `parse_script` 函数后追加:

```python
from antlr4 import CommonTokenStream, FileStream, InputStream


def parse_script_text(script: str, *, file_path: str = "", encoding: str = "utf-8") -> list[TextEntry]:
    """从字符串解析脚本,返回 TextEntry 列表(供 patch 等需要字符串输入的场景)。"""
    input_stream = InputStream(script)
    from .ShirotsumeLexer import ShirotsumeLexer
    from .ShirotsumeParser import ShirotsumeParser
    lexer = ShirotsumeLexer(input_stream)
    parser = ShirotsumeParser(CommonTokenStream(lexer))
    listener = TextExtractionListener(file_path)
    parser.addParseListener(listener)
    parser.program()
    return listener.entries
```

注意:把文件顶部的 `from antlr4 import CommonTokenStream, FileStream` 改为 `from antlr4 import CommonTokenStream, FileStream, InputStream`。

- [ ] **Step 5: 在 `shirotsume_tools/parser/__init__.py` 导出 parse_script_text**

```python
from .core import parse_directory, parse_script, parse_script_text
from .errors import ParserError
from .listener import TextExtractionListener
from .model import TextEntry

__all__ = [
    "ParserError",
    "TextEntry",
    "TextExtractionListener",
    "parse_directory",
    "parse_script",
    "parse_script_text",
]
```

- [ ] **Step 6: 运行测试验证通过**

Run: `pytest tests/test_parser.py -v`
Expected: 全部 PASS(含原有 3 函数测试 + 新 5 函数测试)。

- [ ] **Step 7: 提交**

```bash
git add shirotsume_tools/parser/listener.py shirotsume_tools/parser/core.py shirotsume_tools/parser/__init__.py tests/test_parser.py
git commit -m "feat(parser): extend extractors to 5 functions and add parse_script_text"
```

---

### Task 4: archive/writer.py(repack 迁移)

**Files:**
- Create: `shirotsume_tools/archive/writer.py` (从旧 `shirotsume_tools/shirotsume_tools/repack.py` 迁入)
- Modify: `shirotsume_tools/archive/__init__.py` (导出 PackEntry/write_pack/replace_entries)
- Create: `tests/test_archive_writer.py`

**Interfaces:**
- Produces: `PackEntry(name, data, crypt_type=1)`;`read_pack(path) -> (header, entries)`;`write_pack(path, header, entries)`;`replace_entries(dat_path, out_path, replacements)`

- [ ] **Step 1: 写失败测试 —— write_pack/replace_entries 往返**

创建 `tests/test_archive_writer.py`:

```python
import pytest
from shirotsume_tools.archive import PackEntry, write_pack, read_pack, replace_entries


def test_pack_roundtrip(tmp_path):
    header = b"\x00" * 16
    entries = [
        PackEntry(name="a.txt", data=b"hello world"),
        PackEntry(name="b.txt", data=b"second file"),
    ]
    pack_path = tmp_path / "test.dat"
    write_pack(pack_path, header, entries)
    read_header, read_entries = read_pack(pack_path)
    assert read_header == header
    assert len(read_entries) == 2
    assert read_entries[0].name == "a.txt"
    assert read_entries[0].data == b"hello world"
    assert read_entries[1].name == "b.txt"
    assert read_entries[1].data == b"second file"


def test_replace_entries(tmp_path):
    header = b"\x00" * 8
    entries = [PackEntry(name="script.txt", data=b"original")]
    src = tmp_path / "src.dat"
    write_pack(src, header, entries)
    out = tmp_path / "out.dat"
    replace_entries(src, out, {"script.txt": b"patched"})
    _, read_entries = read_pack(out)
    assert read_entries[0].data == b"patched"


def test_replace_entries_missing_key(tmp_path):
    header = b"\x00"
    entries = [PackEntry(name="a.txt", data=b"x")]
    src = tmp_path / "src.dat"
    write_pack(src, header, entries)
    out = tmp_path / "out.dat"
    with pytest.raises(KeyError):
        replace_entries(src, out, {"nonexistent.txt": b"y"})
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_archive_writer.py -v`
Expected: FAIL —— `PackEntry`/`write_pack`/`read_pack`/`replace_entries` 无法从 `archive` 导入。

- [ ] **Step 3: 创建 `shirotsume_tools/archive/writer.py`**

从旧 `repack.py` 复制全部内容(位于 `d:\Games\gal\白詰草話\shirotsume_tools\shirotsume_tools\repack.py`),原样保留所有函数(`PackEntry`/`read_pack`/`write_pack`/`replace_entries` 及私有辅助函数)。文件内容不变,只是位置从 `shirotsume_tools/repack.py` 移到 `shirotsume_tools/archive/writer.py`。

```python
from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Iterable, Mapping


SIG = b"RepiPack"
VERSION = 2
HEADER_KEY = 0x837FC07A
FILE_KEY = 0xF517AA26


@dataclass(frozen=True)
class PackEntry:
    name: str
    data: bytes
    crypt_type: int = 1


def _crypt_words(data: bytes, key: int) -> bytes:
    buf = bytearray(data)
    for offset in range(0, len(buf) - (len(buf) % 4), 4):
        value = struct.unpack_from("<I", buf, offset)[0]
        struct.pack_into("<I", buf, offset, value ^ key)
        rotated = (((value << 16) | (value >> 16)) & 0xFFFFFFFF) ^ 0x98FCDBA2
        key = (key + rotated) & 0xFFFFFFFF
    return bytes(buf)


def _decrypt_words(data: bytes, key: int) -> bytes:
    buf = bytearray(data)
    for offset in range(0, len(buf) - (len(buf) % 4), 4):
        value = struct.unpack_from("<I", buf, offset)[0] ^ key
        struct.pack_into("<I", buf, offset, value)
        rotated = (((value << 16) | (value >> 16)) & 0xFFFFFFFF) ^ 0x98FCDBA2
        key = (key + rotated) & 0xFFFFFFFF
    return bytes(buf)


def _file_decrypt(data: bytes) -> bytes:
    buf = bytearray(data)
    for offset in range(0, len(buf) - (len(buf) % 4), 4):
        value = struct.unpack_from("<I", buf, offset)[0]
        value = (value << 6) ^ (((value << 6) ^ ((value ^ 0x9B9B9B9B) >> 2)) & 0x3F3F3F3F)
        struct.pack_into("<I", buf, offset, value & 0xFFFFFFFF)
    return bytes(buf)


def _decompress(comp: bytes, size: int) -> bytes:
    out = bytearray()
    cache = bytearray(0x1000)
    cache_ptr = 0xFEE
    cursor = 0
    read_mask = 0
    mask = 0
    while len(out) < size:
        if read_mask == 0:
            read_mask = 0xFF
            mask = comp[cursor]
            cursor += 1
        if mask & 1:
            value = comp[cursor]
            cursor += 1
            out.append(value)
            cache[cache_ptr] = value
            cache_ptr = (cache_ptr + 1) & 0xFFF
        else:
            byte_0 = comp[cursor]
            byte_1 = comp[cursor + 1]
            cursor += 2
            offset = ((byte_1 & 0xF0) << 4) | byte_0
            length = (byte_1 & 0x0F) + 3
            for i in range(length):
                value = cache[(offset + i) & 0xFFF]
                out.append(value)
                cache[cache_ptr] = value
                cache_ptr = (cache_ptr + 1) & 0xFFF
                if len(out) == size:
                    break
        read_mask >>= 1
        mask >>= 1
    return bytes(out)


def _read_exact(file: BinaryIO, size: int) -> bytes:
    data = file.read(size)
    if len(data) != size:
        raise EOFError("unexpected end of RepiPack file")
    return data


def read_pack(path: str | Path) -> tuple[bytes, list[PackEntry]]:
    with Path(path).open("rb") as file:
        if _read_exact(file, 8) != SIG:
            raise ValueError("not a RepiPack file")
        version = struct.unpack("<I", _read_exact(file, 4))[0]
        if version != VERSION:
            raise ValueError(f"unsupported RepiPack version {version}")
        header_size = struct.unpack("<I", _read_exact(file, 4))[0]
        header = _decrypt_words(_read_exact(file, header_size), HEADER_KEY)
        file_count = struct.unpack("<I", _read_exact(file, 4))[0]

        table = []
        for _ in range(file_count):
            raw = _decrypt_words(_read_exact(file, 80), FILE_KEY)
            name = raw[:0x40].split(b"\0", 1)[0].decode("cp932")
            offset, size, comp_size = struct.unpack_from("<III", raw, 0x40)
            crypt_type = raw[0x4C]
            table.append((name, offset, size, comp_size, crypt_type))

        entries: list[PackEntry] = []
        for name, offset, size, comp_size, crypt_type in table:
            file.seek(offset)
            data = _read_exact(file, comp_size)
            if crypt_type == 1:
                data = _decrypt_words(data, FILE_KEY)
            elif crypt_type == 2:
                data = _file_decrypt(data)
            if comp_size != size:
                data = _decompress(data, size)
            entries.append(PackEntry(name=name, data=data, crypt_type=crypt_type))

    return header, entries


def write_pack(path: str | Path, header: bytes, entries: Iterable[PackEntry]) -> None:
    entries = list(entries)
    table_offset = 8 + 4 + 4 + len(header) + 4
    data_offset = table_offset + len(entries) * 80
    offset = data_offset
    table = bytearray()
    bodies = []

    for entry in entries:
        name = entry.name.encode("cp932")
        if len(name) >= 0x40:
            raise ValueError(f"packed name is too long: {entry.name}")
        body = _crypt_words(entry.data, FILE_KEY)
        raw = bytearray(80)
        raw[:len(name)] = name
        struct.pack_into("<III", raw, 0x40, offset, len(entry.data), len(body))
        raw[0x4C] = 1
        table.extend(_crypt_words(bytes(raw), FILE_KEY))
        bodies.append(body)
        offset += len(body)

    with Path(path).open("wb") as file:
        file.write(SIG)
        file.write(struct.pack("<I", VERSION))
        file.write(struct.pack("<I", len(header)))
        file.write(_crypt_words(header, HEADER_KEY))
        file.write(struct.pack("<I", len(entries)))
        file.write(table)
        for body in bodies:
            file.write(body)


def replace_entries(dat_path: str | Path, out_path: str | Path, replacements: Mapping[str, bytes]) -> None:
    header, entries = read_pack(dat_path)
    missing = set(replacements)
    patched = []
    for entry in entries:
        data = replacements.get(entry.name, entry.data)
        if entry.name in replacements:
            missing.remove(entry.name)
        patched.append(PackEntry(entry.name, data, 1))
    if missing:
        raise KeyError(f"replacement target(s) not found: {', '.join(sorted(missing))}")
    write_pack(out_path, header, patched)
```

- [ ] **Step 4: 更新 `shirotsume_tools/archive/__init__.py` 导出 writer**

```python
from .errors import ArchiveError, InvalidSignatureError, UnsupportedVersionError
from .model import FileEntry
from .reader import Archive, decrypt
from .writer import PackEntry, read_pack, replace_entries, write_pack

__all__ = [
    "Archive",
    "ArchiveError",
    "FileEntry",
    "InvalidSignatureError",
    "PackEntry",
    "UnsupportedVersionError",
    "decrypt",
    "read_pack",
    "replace_entries",
    "write_pack",
]
```

- [ ] **Step 5: 运行测试验证通过**

Run: `pytest tests/test_archive_writer.py tests/test_archive.py -v`
Expected: 全部 PASS。

- [ ] **Step 6: 提交**

```bash
git add shirotsume_tools/archive/writer.py shirotsume_tools/archive/__init__.py tests/test_archive_writer.py
git commit -m "feat(archive): migrate repack into archive/writer.py"
```

---

### Task 5: translation/encoding.py + errors.py

**Files:**
- Create: `shirotsume_tools/translation/__init__.py` (临时空导出,Task 7 补全)
- Create: `shirotsume_tools/translation/encoding.py` (从旧 custom_encoding.py 迁入)
- Create: `shirotsume_tools/translation/errors.py`
- Create: `tests/test_translation_encoding.py`

**Interfaces:**
- Produces: `encode_text(text, mapping=None) -> bytes`;`encode_script_text(text, mapping=None) -> bytes`;`load_mapping(path) -> dict`;`save_mapping(path, mapping)`;`jis_private_codes()`;`TranslationError`

- [ ] **Step 1: 写失败测试 —— encode_text 自定义映射**

创建 `tests/test_translation_encoding.py`:

```python
from shirotsume_tools.translation.encoding import (
    encode_text, encode_script_text, load_mapping, save_mapping, jis_private_codes,
)


def test_encode_text_cp932_passthrough():
    assert encode_text("abc") == b"abc"


def test_encode_text_custom_mapping_assigns_new_code():
    mapping = {}
    result = encode_text("漢", mapping=mapping)
    assert "漢" in mapping
    assert len(result) == 2
    code = (result[0] << 8) | result[1]
    assert code == mapping["漢"]


def test_encode_text_reuses_existing_mapping():
    mapping = {"漢": 0xF040}
    result = encode_text("漢", mapping=mapping)
    assert result == bytes([0xF0, 0x40])


def test_save_load_mapping_roundtrip(tmp_path):
    mapping = {"漢": 0xF040, "字": 0xF041}
    path = tmp_path / "map.json"
    save_mapping(path, mapping)
    loaded = load_mapping(path)
    assert loaded == mapping


def test_jis_private_codes_in_range():
    codes = list(jis_private_codes())
    assert codes[0] == 0xF040
    assert all(0xF040 <= c <= 0xF9FC for c in codes)
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_translation_encoding.py -v`
Expected: FAIL —— `shirotsume_tools.translation` 模块不存在。

- [ ] **Step 3: 创建 `shirotsume_tools/translation/errors.py`**

```python
class TranslationError(Exception):
    """翻译流水线错误"""
    pass
```

- [ ] **Step 4: 创建 `shirotsume_tools/translation/encoding.py`**

从旧 `custom_encoding.py` 原样复制全部内容:

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, Mapping, MutableMapping


CP932 = "cp932"


def jis_private_codes() -> Iterable[int]:
    for lead in range(0xF0, 0xFA):
        for trail in list(range(0x40, 0x7F)) + list(range(0x80, 0xFD)):
            yield (lead << 8) | trail


def load_mapping(path: str | Path | None) -> Dict[str, int]:
    if path is None or not Path(path).exists():
        return {}
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    mapping: Dict[str, int] = {}
    for char, value in data.items():
        if isinstance(value, str):
            mapping[char] = int(value, 16)
        else:
            mapping[char] = int(value)
    return mapping


def save_mapping(path: str | Path, mapping: Mapping[str, int]) -> None:
    data = {char: f"{code:04X}" for char, code in sorted(mapping.items(), key=lambda item: item[1])}
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def encode_text(text: str, mapping: MutableMapping[str, int] | None = None) -> bytes:
    result = bytearray()
    available_codes = None
    if mapping is not None:
        used = set(mapping.values())
        available_codes = (code for code in jis_private_codes() if code not in used)

    for char in text:
        try:
            result.extend(char.encode(CP932))
            continue
        except UnicodeEncodeError:
            pass

        if mapping is None:
            raise UnicodeEncodeError(CP932, char, 0, 1, "character has no custom mapping")

        code = mapping.get(char)
        if code is None:
            assert available_codes is not None
            code = next(available_codes)
            mapping[char] = code
        result.append((code >> 8) & 0xFF)
        result.append(code & 0xFF)

    return bytes(result)


def encode_script_text(text: str, mapping: MutableMapping[str, int] | None = None) -> bytes:
    return encode_text(text, mapping)
```

- [ ] **Step 5: 创建临时 `shirotsume_tools/translation/__init__.py`**

```python
from .encoding import encode_script_text, encode_text, load_mapping, save_mapping
from .errors import TranslationError

__all__ = [
    "TranslationError",
    "encode_script_text",
    "encode_text",
    "load_mapping",
    "save_mapping",
]
```

- [ ] **Step 6: 运行测试验证通过**

Run: `pytest tests/test_translation_encoding.py -v`
Expected: 全部 PASS。

- [ ] **Step 7: 提交**

```bash
git add shirotsume_tools/translation tests/test_translation_encoding.py
git commit -m "feat(translation): migrate custom_encoding into translation/encoding.py"
```

---

### Task 6: translation/patch.py(script_patch 迁移)

**Files:**
- Create: `shirotsume_tools/translation/patch.py` (从旧 script_patch.py 迁入,改用 TextEntry + parse_script_text + archive.replace_entries)
- Modify: `shirotsume_tools/translation/__init__.py` (导出 patch 函数)
- Create: `tests/test_translation_patch.py`

**Interfaces:**
- Consumes: `parse_script_text` from parser;`TextEntry` from parser;`replace_entries` from archive;`encode_script_text`/`load_mapping`/`save_mapping` from encoding
- Produces: `patch_script_text(script, replacements) -> (str, int)`;`patch_script_file(script_path, replacements_path, out_path, *, source_encoding, mapping_path) -> int`;`patch_dat_script(dat_path, script_name, patched_script_path, out_dat)`;`load_replacements(path)`;`normalize_replacement_text(text)`

- [ ] **Step 1: 写失败测试 —— patch_script_text 两种模式**

创建 `tests/test_translation_patch.py`:

```python
from shirotsume_tools.translation.patch import (
    patch_script_text, load_replacements, normalize_replacement_text,
)


SAMPLE = 'CreateBalloon("x", "こんにちは");'


def test_patch_script_text_mapping():
    patched, count = patch_script_text(SAMPLE, {"こんにちは": "你好"})
    assert count == 1
    assert "你好" in patched
    assert "こんにちは" not in patched


def test_patch_script_text_sequence():
    patched, count = patch_script_text(SAMPLE, ["你好"])
    assert count == 1
    assert "你好" in patched


def test_patch_script_text_no_match():
    patched, count = patch_script_text(SAMPLE, {"不存在的文本": "x"})
    assert count == 0
    assert patched == SAMPLE


def test_patch_script_text_five_functions():
    script = '''page T {
CreateBalloon("a", "b1");
CreateBalloonEx("a","b","c","b2","d","e","f");
CreateBalloonBie("a", "b3");
CreateText("b4");
AddText("w", "b5");
}'''
    patched, count = patch_script_text(script, {"b1": "c1", "b2": "c2", "b3": "c3", "b4": "c4", "b5": "c5"})
    assert count == 5
    for c in ("c1", "c2", "c3", "c4", "c5"):
        assert c in patched


def test_load_replacements_csv_mapping(tmp_path):
    csv_path = tmp_path / "r.csv"
    csv_path.write_text("raw_text,text,comment\n原,译,\n", encoding="utf-8-sig")
    result = load_replacements(csv_path)
    assert result == {"原": "译"}


def test_normalize_replacement_text_pause():
    assert normalize_replacement_text("･･････") == "……"
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_translation_patch.py -v`
Expected: FAIL —— `shirotsume_tools.translation.patch` 不存在。

- [ ] **Step 3: 创建 `shirotsume_tools/translation/patch.py`**

从旧 `script_patch.py` 迁入,做以下修改:
1. 删除 `TextSpan` dataclass 和 `TextSpanListener` 类(改用 parser 的 `parse_script_text`)
2. 删除 `find_text_spans` 函数(改用 `parse_script_text`)
3. 导入改为 `from ..parser import TextEntry, parse_script_text` 和 `from ..archive import replace_entries` 和 `from .encoding import encode_script_text, load_mapping, save_mapping`
4. `patch_script_text` 内部 `find_text_spans(script)` 改为 `parse_script_text(script)`,返回的 `TextEntry` 用 `.text`(替代 `.raw_text`)、`.start`、`.stop`、`.line`

```python
from __future__ import annotations

import csv
from io import StringIO
import json
from pathlib import Path
from typing import Mapping, Sequence

from ..archive import replace_entries
from ..parser import TextEntry, parse_script_text
from .encoding import encode_script_text, load_mapping, save_mapping


def _escape_script_string(text: str) -> str:
    result = ['"']
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    index = 0
    while index < len(text):
        char = text[index]
        if char == "\\":
            if index + 1 < len(text):
                result.append(text[index:index + 2])
                index += 2
                continue
            result.append("\\")
        elif char == '"':
            result.append('\\"')
        elif char == "\n":
            result.append("\r\n")
        else:
            result.append(char)
        index += 1
    result.append('"')
    return "".join(result)


def normalize_replacement_text(text: str) -> str:
    """Normalize visible pause punctuation without touching script tags."""
    parts: list[str] = []
    in_tag = False
    buffer: list[str] = []

    def flush_visible() -> None:
        if not buffer:
            return
        visible = "".join(buffer)
        buffer.clear()

        output: list[str] = []
        index = 0
        pause_chars = {".", ",", "，", "、", "。", "･", "・", "·", "…"}
        while index < len(visible):
            char = visible[index]
            if char in pause_chars:
                start = index
                while index < len(visible) and visible[index] in pause_chars:
                    index += 1
                run = visible[start:index]
                if len(run) >= 2 and any(mark in run for mark in ("･", "・", "·", ".", "…")):
                    output.append("……")
                else:
                    output.append(run)
                continue
            output.append(char)
            index += 1

        normalized = "".join(output)
        normalized = normalized.replace("……。", "……")
        normalized = normalized.replace("……，", "……")
        normalized = normalized.replace("……、", "……")
        parts.append(normalized)

    for char in text:
        if char == "<":
            flush_visible()
            in_tag = True
            parts.append(char)
        elif char == ">" and in_tag:
            in_tag = False
            parts.append(char)
        elif in_tag:
            parts.append(char)
        else:
            buffer.append(char)
    flush_visible()
    return "".join(parts)


def load_replacements(path: str | Path) -> Sequence[str] | Mapping[str, str]:
    path = Path(path)
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [str(item) for item in data]
        return {str(key): str(value) for key, value in data.items()}

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
    if not rows:
        return []
    if "raw_text" in reader.fieldnames and "text" in reader.fieldnames:
        return {row["raw_text"]: normalize_replacement_text(row["text"]) for row in rows if row.get("text")}
    if "text" in reader.fieldnames:
        return [normalize_replacement_text(row["text"]) for row in rows]
    raise ValueError("replacement CSV must have a text column, or raw_text and text columns")


def patch_script_text(script: str, replacements: Sequence[str] | Mapping[str, str]) -> tuple[str, int]:
    entries = parse_script_text(script)
    edits: list[tuple[int, int, str]] = []
    if isinstance(replacements, Mapping):
        for entry in entries:
            replacement = replacements.get(entry.text)
            if replacement is not None:
                edits.append((entry.start, entry.stop, replacement))
    else:
        if len(replacements) > len(entries):
            raise ValueError(f"{len(replacements)} replacements provided for {len(entries)} script text spans")
        for entry, replacement in zip(entries, replacements):
            edits.append((entry.start, entry.stop, replacement))

    if not edits:
        return script, 0

    patched = StringIO()
    cursor = 0
    for start, stop, replacement in edits:
        patched.write(script[cursor:start])
        patched.write(_escape_script_string(replacement))
        cursor = stop + 1
    patched.write(script[cursor:])
    return patched.getvalue(), len(edits)


def patch_script_file(
    script_path: str | Path,
    replacements_path: str | Path,
    out_path: str | Path,
    *,
    source_encoding: str = "cp932",
    mapping_path: str | Path | None = None,
) -> int:
    mapping = load_mapping(mapping_path)
    with Path(script_path).open("r", encoding=source_encoding, newline="") as file:
        script = file.read()
    patched, count = patch_script_text(script, load_replacements(replacements_path))
    encoded = encode_script_text(patched, mapping)
    Path(out_path).write_bytes(encoded)
    if mapping_path is not None:
        save_mapping(mapping_path, mapping)
    return count


def patch_dat_script(
    dat_path: str | Path,
    script_name: str,
    patched_script_path: str | Path,
    out_dat: str | Path,
) -> None:
    replace_entries(dat_path, out_dat, {script_name: Path(patched_script_path).read_bytes()})
```

- [ ] **Step 4: 更新 `shirotsume_tools/translation/__init__.py` 导出 patch**

```python
from .encoding import encode_script_text, encode_text, load_mapping, save_mapping
from .errors import TranslationError
from .patch import load_replacements, normalize_replacement_text, patch_dat_script, patch_script_file, patch_script_text

__all__ = [
    "TranslationError",
    "encode_script_text",
    "encode_text",
    "load_mapping",
    "load_replacements",
    "normalize_replacement_text",
    "patch_dat_script",
    "patch_script_file",
    "patch_script_text",
    "save_mapping",
]
```

- [ ] **Step 5: 运行测试验证通过**

Run: `pytest tests/test_translation_patch.py tests/test_translation_encoding.py -v`
Expected: 全部 PASS。

- [ ] **Step 6: 提交**

```bash
git add shirotsume_tools/translation/patch.py shirotsume_tools/translation/__init__.py tests/test_translation_patch.py
git commit -m "feat(translation): migrate script_patch into translation/patch.py using TextEntry"
```

---

### Task 7: translation/agent.py(translate_agent 迁移)

**Files:**
- Create: `shirotsume_tools/translation/agent.py` (从旧 translate_agent.py 迁入,改用 TextEntry)
- Modify: `shirotsume_tools/translation/__init__.py` (导出 agent 函数)
- Create: `tests/test_translation_agent.py`

**Interfaces:**
- Consumes: `TextEntry` from parser;`parse_directory`/`parse_script` from parser;`patch_script_file` from patch
- Produces: `translate_scripts(...)`;`sync_translation_csvs(...)`;`extract_translation_items(...)`

- [ ] **Step 1: 写失败测试 —— extract_translation_items + translate_batch(monkeypatch)**

创建 `tests/test_translation_agent.py`:

```python
import json
from unittest.mock import MagicMock, patch

import pytest

from shirotsume_tools.translation.agent import (
    extract_translation_items, translate_batch, translate_scripts, sync_translation_csvs,
)


SAMPLE_SCRIPT = 'CreateBalloon("x", "テスト");'


def test_extract_translation_items(tmp_path):
    script = tmp_path / "1-01.txt"
    script.write_text(SAMPLE_SCRIPT, encoding="cp932")
    items = extract_translation_items(str(tmp_path), source_encoding="cp932")
    assert len(items) == 1
    assert items[0].text == "テスト"
    assert items[0].file_path.endswith("1-01.txt")


def test_translate_batch_monkeypatch(tmp_path):
    from shirotsume_tools.parser import TextEntry
    batch = [TextEntry(text="こんにちは", file_path="a.txt", line=1, start=0, stop=10)]
    mock_response = MagicMock()
    mock_response.output_text = json.dumps({
        "translations": [{"id": "a.txt#0", "text": "你好"}],
        "memory_suggestions": [],
    })
    with patch("shirotsume_tools.translation.agent.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_client.responses.create.return_value = mock_response
        mock_openai.return_value = mock_client
        translations, suggestions = translate_batch(
            batch, model="gpt-4.1", target_language="Simplified Chinese",
            memory={"glossary": {}, "characters": {}, "style": [], "decisions": [], "pending_suggestions": []},
        )
    assert translations == {"a.txt#0": "你好"}
    assert suggestions == []


def test_sync_translation_csvs(tmp_path):
    script = tmp_path / "1-01.txt"
    script.write_text(SAMPLE_SCRIPT, encoding="cp932")
    repl_dir = tmp_path / "translations"
    added = sync_translation_csvs(str(tmp_path), str(repl_dir), source_encoding="cp932")
    assert added >= 1
    csv_path = repl_dir / "1-01.csv"
    assert csv_path.exists()
    content = csv_path.read_text(encoding="utf-8-sig")
    assert "テスト" in content
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_translation_agent.py -v`
Expected: FAIL —— `shirotsume_tools.translation.agent` 不存在。

- [ ] **Step 3: 创建 `shirotsume_tools/translation/agent.py`**

从旧 `translate_agent.py` 迁入,做以下修改:
1. 删除 `TranslationItem` dataclass 和 `iter_script_files`(改用 parser 的 `parse_directory`)
2. 删除 `from .script_patch import find_text_spans, patch_script_file`,改 `from .patch import patch_script_file`
3. 删除 `from dataclasses import dataclass`(不再需要)
4. `extract_translation_items` 改用 `parse_directory` 返回 `list[TextEntry]`
5. `translate_batch` 的 payload `items` 从 `item.raw_text`→`item.text`,`item.id`→`f"{item.file_path}#{i}"`
6. `translate_scripts` 中 `item.raw_text`→`item.text`,`item.id`→`f"{item.file_path}#{i}"`
7. `from openai import OpenAI` 的 `ModuleNotFoundError` 信息改为提示 `pip install shirotsume_tools[translation]`

```python
from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from ..parser import TextEntry, parse_directory
from .patch import patch_script_file


DEFAULT_MEMORY: dict[str, Any] = {
    "glossary": {},
    "characters": {},
    "style": [
        "Translate Japanese visual novel dialogue into natural Simplified Chinese.",
        "Preserve script tags, markup, escapes, variables, and line breaks exactly unless they are human-readable prose.",
        "Keep recurring names, places, items, and special terms consistent with the glossary.",
    ],
    "decisions": [],
    "pending_suggestions": [],
}


def extract_translation_items(script_dir: str | Path, *, source_encoding: str = "cp932", limit: int | None = None) -> list[TextEntry]:
    entries = parse_directory(str(script_dir), encoding=source_encoding)
    if limit is not None:
        entries = entries[:limit]
    return entries


def chunked_by_budget(items: Sequence[TextEntry], max_items: int, max_source_chars: int) -> Iterable[Sequence[TextEntry]]:
    batch: list[TextEntry] = []
    char_count = 0
    for item in items:
        item_chars = len(item.text)
        if batch and (len(batch) >= max_items or char_count + item_chars > max_source_chars):
            yield batch
            batch = []
            char_count = 0
        batch.append(item)
        char_count += item_chars
    if batch:
        yield batch


def _response_text(response: object) -> str:
    text = getattr(response, "output_text", None)
    if isinstance(text, str) and text:
        return text
    return str(response)


def _json_object_from_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return json.loads(text)


def load_translation_memory(path: str | Path | None) -> dict[str, Any]:
    if path is None:
        return dict(DEFAULT_MEMORY)
    memory_path = Path(path)
    if not memory_path.exists():
        return dict(DEFAULT_MEMORY)
    loaded = json.loads(memory_path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"Translation memory must be a JSON object: {memory_path}")
    memory = dict(DEFAULT_MEMORY)
    memory.update(loaded)
    for key in ("glossary", "characters"):
        if not isinstance(memory.get(key), dict):
            raise ValueError(f"Translation memory field must be an object: {key}")
    for key in ("style", "decisions", "pending_suggestions"):
        if not isinstance(memory.get(key), list):
            raise ValueError(f"Translation memory field must be a list: {key}")
    return memory


def save_translation_memory(path: str | Path, memory: dict[str, Any]) -> None:
    memory_path = Path(path)
    memory_path.parent.mkdir(parents=True, exist_ok=True)
    memory_path.write_text(json.dumps(memory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _proposal_key(proposal: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(proposal.get("type", "")),
        str(proposal.get("source", "")),
        str(proposal.get("target", "")),
    )


def merge_memory_suggestions(memory: dict[str, Any], suggestions: Sequence[dict[str, Any]]) -> int:
    pending = memory.setdefault("pending_suggestions", [])
    if not isinstance(pending, list):
        pending = []
        memory["pending_suggestions"] = pending

    seen = {_proposal_key(item) for item in pending if isinstance(item, dict)}
    added = 0
    for suggestion in suggestions:
        if not isinstance(suggestion, dict):
            continue
        proposal = {
            "type": str(suggestion.get("type", "decision")),
            "source": str(suggestion.get("source", "")),
            "target": str(suggestion.get("target", "")),
            "note": str(suggestion.get("note", "")),
        }
        if not proposal["source"] and not proposal["target"] and not proposal["note"]:
            continue
        key = _proposal_key(proposal)
        if key in seen:
            continue
        pending.append(proposal)
        seen.add(key)
        added += 1
    return added


def translation_system_prompt(prompt_language: str = "en") -> str:
    if prompt_language.lower() in {"zh", "cn", "chinese", "zh-cn"}:
        return (
            "你正在把日文视觉小说游戏脚本翻译成简体中文。\n"
            "在写出译文前，请在内部仔细判断当前场景、说话者意图、情绪语气、上下文承接和自然中文表达。"
            "这些思考只用于生成译文；JSON 输出中不要包含分析、注释、备选译法或解释。\n"
            "\n"
            "翻译记忆具有约束力：\n"
            "- 人名、地名、物品、组织、专有名词必须严格遵守 glossary。\n"
            "- 角色称呼、语气、口癖、关系距离必须遵守 characters。\n"
            "- 在做新选择前，优先遵守 style 和 decisions。\n"
            "- 如果你认为已有术语决定不合适，不要在译文中擅自改写；请放入 memory_suggestions。\n"
            "\n"
            "脚本安全规则：\n"
            "- 必须保留标签、标记、转义、变量、类似命令的片段、引擎需要的标点和换行。\n"
            "- 必须原样保留纯标点演出片段，尤其是 <TYPE interval=60>･･････</TYPE> 这样的定时停顿。\n"
            "- 只翻译 source_text 中给玩家阅读的自然语言文本。\n"
            "- 每条输出都必须能直接替换对应的原文字符串。\n"
            "- 把同一文件中按顺序排列的 items 当成连续场景来理解，保持相邻条目的叙事连续性。\n"
            "- 不要生硬照搬日语语法、身体部位惯用表达、省略号和句尾；中文自然表达优先。\n"
            "- 标签必须保留在相对于其作用文本的原始位置。不要删除或翻译标签名和属性。\n"
            "- 文风应是润色后的中文视觉小说叙事和对白，而不是字典式直译。\n"
            "\n"
            "记忆更新规则：\n"
            "- 每批都主动检查是否有值得记录的长期决定；如果有，请返回 1 到 5 条 suggestions。\n"
            "- 合适的建议包括角色/姓名译名、称呼方式、研究机构、反复出现的地点/物品、专有术语和文风决定。\n"
            "- 不要为一次性普通短语添加建议。\n"
            "- 不要重复 memory 中已经存在的建议。\n"
            "- 如果本批确实没有可复用决定，memory_suggestions 可以为空数组。\n"
            "\n"
            "只返回如下形状的 JSON：\n"
            "{"
            '"translations":[{"id":"same id","text":"translated Chinese text"}],'
            '"memory_suggestions":[{"type":"glossary|character|style|decision","source":"Japanese term or topic","target":"Chinese decision","note":"short reason"}]'
            "}."
        )

    return (
        "You are translating Japanese visual novel game scripts into Simplified Chinese.\n"
        "Think through the local scene context, speaker intent, emotional tone, and idiomatic Chinese phrasing before writing each translation. "
        "Do this reasoning internally; do not include analysis, notes, alternatives, or explanations in the JSON output.\n"
        "\n"
        "Translation memory is binding:\n"
        "- Follow glossary entries exactly for names, places, items, organizations, and special terms.\n"
        "- Follow character notes for pronouns, speech register, catchphrases, and relationship tone.\n"
        "- Follow style and decisions before making new choices.\n"
        "- If a glossary decision seems wrong, do not override it in the translation. Add a suggestion instead.\n"
        "\n"
        "Script safety rules:\n"
        "- Preserve tags, markup, escapes, variables, command-like fragments, punctuation required by the engine, and line breaks.\n"
        "- Preserve punctuation-only display fragments exactly, especially timed pauses such as <TYPE interval=60>･･････</TYPE>.\n"
        "- Translate only human-readable prose inside source_text.\n"
        "- Keep each output line usable as a direct replacement for the corresponding source string.\n"
        "- Use ordered items in each file as one continuous scene; preserve continuity across adjacent entries.\n"
        "- Avoid stiff literal translations of Japanese grammar, body-part idioms, ellipses, and sentence endings when natural Chinese would phrase them differently.\n"
        "- Keep tags at their original positions relative to the text they affect. Do not delete or translate tag names or attributes.\n"
        "- Prefer polished visual-novel narration and dialogue over dictionary-literal wording.\n"
        "\n"
        "Memory update rules:\n"
        "- Actively check every batch for durable decisions worth recording; if any exist, return 1 to 5 suggestions.\n"
        "- Good suggestions include character/name translations, forms of address, research groups, recurring places/items, special terminology, and style decisions.\n"
        "- Do not suggest one-off ordinary phrases.\n"
        "- Do not repeat suggestions already present in memory.\n"
        "- If the batch truly has no reusable decisions, memory_suggestions may be an empty array.\n"
        "\n"
        "Return only JSON with this exact shape:\n"
        "{"
        '"translations":[{"id":"same id","text":"translated Chinese text"}],'
        '"memory_suggestions":[{"type":"glossary|character|style|decision","source":"Japanese term or topic","target":"Chinese decision","note":"short reason"}]'
        "}."
    )


def translate_batch(
    batch: Sequence[TextEntry],
    *,
    model: str,
    target_language: str,
    memory: dict[str, Any],
    story_context: str = "",
    temperature: float = 0.2,
    api_base_url: str | None = None,
    prompt_language: str = "en",
) -> tuple[dict[str, str], list[dict[str, Any]]]:
    try:
        from openai import OpenAI
    except ModuleNotFoundError as exc:
        raise RuntimeError("Install the OpenAI SDK first: pip install shirotsume_tools[translation]") from exc

    client_kwargs: dict[str, str] = {}
    if api_base_url:
        client_kwargs["base_url"] = api_base_url
    client = OpenAI(**client_kwargs)
    payload = {
        "target_language": target_language,
        "story_context": story_context,
        "translation_memory": memory,
        "memory_instruction": (
            "After translating, propose durable glossary/character/style/decision updates for recurring names, "
            "terms, organizations, forms of address, or style choices found in this batch. "
            "Return 1 to 5 memory_suggestions when useful; return [] only when there is truly nothing reusable."
        ),
        "items": [
            {
                "id": f"{item.file_path}#{i}",
                "file": item.file_path,
                "index": i,
                "line": item.line,
                "source_text": item.text,
            }
            for i, item in enumerate(batch)
        ],
    }
    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": translation_system_prompt(prompt_language)},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
        temperature=temperature,
    )
    data = _json_object_from_response(_response_text(response))
    translations = data.get("translations")
    if not isinstance(translations, list):
        raise ValueError("OpenAI response did not contain a translations list")
    result: dict[str, str] = {}
    for entry in translations:
        if not isinstance(entry, dict) or "id" not in entry or "text" not in entry:
            raise ValueError(f"Invalid translation entry: {entry!r}")
        result[str(entry["id"])] = str(entry["text"])
    suggestions = data.get("memory_suggestions", [])
    if not isinstance(suggestions, list):
        raise ValueError("OpenAI response memory_suggestions must be a list")
    return result, [item for item in suggestions if isinstance(item, dict)]


def translate_batch_with_retry(
    batch: Sequence[TextEntry],
    *,
    model: str,
    target_language: str,
    memory: dict[str, Any],
    story_context: str = "",
    temperature: float = 0.2,
    api_base_url: str | None = None,
    prompt_language: str = "en",
) -> tuple[dict[str, str], list[dict[str, Any]]]:
    try:
        return translate_batch(
            batch,
            model=model,
            target_language=target_language,
            memory=memory,
            story_context=story_context,
            temperature=temperature,
            api_base_url=api_base_url,
            prompt_language=prompt_language,
        )
    except Exception:
        if len(batch) <= 1:
            raise
        midpoint = len(batch) // 2
        left_translations, left_suggestions = translate_batch_with_retry(
            batch[:midpoint],
            model=model,
            target_language=target_language,
            memory=memory,
            story_context=story_context,
            temperature=temperature,
            api_base_url=api_base_url,
            prompt_language=prompt_language,
        )
        right_translations, right_suggestions = translate_batch_with_retry(
            batch[midpoint:],
            model=model,
            target_language=target_language,
            memory=memory,
            story_context=story_context,
            temperature=temperature,
            api_base_url=api_base_url,
            prompt_language=prompt_language,
        )
        left_translations.update(right_translations)
        return left_translations, left_suggestions + right_suggestions


def write_replacement_csv(path: str | Path, rows: Sequence[tuple[str, str]]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["raw_text", "text", "comment"])
        writer.writeheader()
        for raw_text, text in rows:
            writer.writerow({"raw_text": raw_text, "text": text, "comment": ""})


def read_existing_replacement_csv(path: str | Path) -> dict[str, tuple[str, str]]:
    path = Path(path)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames or "raw_text" not in reader.fieldnames:
            return {}
        existing: dict[str, tuple[str, str]] = {}
        for row in reader:
            raw_text = row.get("raw_text", "")
            if not raw_text:
                continue
            existing[raw_text] = (row.get("text", ""), row.get("comment", ""))
        return existing


def write_merged_replacement_csv(path: str | Path, raw_texts: Sequence[str], translations: Mapping[str, str]) -> int:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = read_existing_replacement_csv(path)
    added = 0
    seen: set[str] = set()
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["raw_text", "text", "comment"])
        writer.writeheader()
        for raw_text in raw_texts:
            if raw_text in seen:
                continue
            seen.add(raw_text)
            previous = existing.get(raw_text)
            if previous is None:
                added += 1
                text = translations.get(raw_text, "")
                comment = ""
            else:
                text, comment = previous
                if raw_text in translations:
                    text = translations[raw_text]
            writer.writerow({"raw_text": raw_text, "text": text, "comment": comment})
    return added


def sync_translation_csvs(
    script_dir: str | Path,
    replacements_dir: str | Path,
    *,
    source_encoding: str = "cp932",
) -> int:
    script_root = Path(script_dir)
    replacements_root = Path(replacements_dir)
    items = extract_translation_items(script_root, source_encoding=source_encoding)
    by_file: dict[str, list[str]] = {}
    for item in items:
        by_file.setdefault(item.file_path, []).append(item.text)

    added = 0
    for relative_file, raw_texts in by_file.items():
        csv_path = replacements_root / Path(relative_file).with_suffix(".csv")
        added += write_merged_replacement_csv(csv_path, raw_texts, {})
    return added


def translate_scripts(
    script_dir: str | Path,
    replacements_dir: str | Path,
    *,
    patched_dir: str | Path | None = None,
    mapping_path: str | Path | None = None,
    model: str | None = None,
    target_language: str = "Simplified Chinese",
    source_encoding: str = "cp932",
    batch_size: int = 24,
    limit: int | None = None,
    story_context: str = "",
    temperature: float = 0.2,
    memory_path: str | Path | None = None,
    api_base_url: str | None = None,
    prompt_language: str = "en",
    max_source_chars: int = 6000,
) -> int:
    model = model or os.environ.get("OPENAI_MODEL", "gpt-4.1")
    script_root = Path(script_dir)
    replacements_root = Path(replacements_dir)
    items = extract_translation_items(script_root, source_encoding=source_encoding, limit=limit)
    memory = load_translation_memory(memory_path)

    existing_by_file: dict[str, dict[str, tuple[str, str]]] = {}
    existing_translations: dict[str, str] = {}
    missing_items: list[TextEntry] = []
    for item in items:
        existing = existing_by_file.get(item.file_path)
        if existing is None:
            csv_path = replacements_root / Path(item.file_path).with_suffix(".csv")
            existing = read_existing_replacement_csv(csv_path)
            existing_by_file[item.file_path] = existing
        previous = existing.get(item.text)
        if previous is not None and previous[0]:
            existing_translations[item.text] = previous[0]
        else:
            missing_items.append(item)

    translations: dict[str, str] = dict(existing_translations)
    for batch in chunked_by_budget(missing_items, batch_size, max_source_chars):
        batch_translations, suggestions = translate_batch_with_retry(
            batch,
            model=model,
            target_language=target_language,
            memory=memory,
            story_context=story_context,
            temperature=temperature,
            api_base_url=api_base_url,
            prompt_language=prompt_language,
        )
        translations.update(batch_translations)
        if merge_memory_suggestions(memory, suggestions) and memory_path is not None:
            save_translation_memory(memory_path, memory)

    by_file: dict[str, list[str]] = {}
    for i, item in enumerate(items):
        translated = translations.get(item.text)
        if translated is None and item in missing_items:
            translated = translations.get(f"{item.file_path}#{i}")
        if translated is None:
            raise ValueError(f"Missing translation for {item.file_path}#{i}")
        translations[item.text] = translated
        by_file.setdefault(item.file_path, []).append(item.text)

    for relative_file, raw_texts in by_file.items():
        relative_path = Path(relative_file)
        csv_path = replacements_root / relative_path.with_suffix(".csv")
        write_merged_replacement_csv(csv_path, raw_texts, translations)
        if patched_dir is not None:
            source_path = script_root / relative_path
            out_path = Path(patched_dir) / relative_path
            out_path.parent.mkdir(parents=True, exist_ok=True)
            patch_script_file(source_path, csv_path, out_path, source_encoding=source_encoding, mapping_path=mapping_path)

    if memory_path is not None:
        save_translation_memory(memory_path, memory)

    return len(items)
```

- [ ] **Step 4: 更新 `shirotsume_tools/translation/__init__.py` 导出 agent**

```python
from .agent import extract_translation_items, sync_translation_csvs, translate_scripts
from .encoding import encode_script_text, encode_text, load_mapping, save_mapping
from .errors import TranslationError
from .patch import load_replacements, normalize_replacement_text, patch_dat_script, patch_script_file, patch_script_text

__all__ = [
    "TranslationError",
    "encode_script_text",
    "encode_text",
    "extract_translation_items",
    "load_mapping",
    "load_replacements",
    "normalize_replacement_text",
    "patch_dat_script",
    "patch_script_file",
    "patch_script_text",
    "save_mapping",
    "sync_translation_csvs",
    "translate_scripts",
]
```

- [ ] **Step 5: 运行测试验证通过**

Run: `pytest tests/test_translation_agent.py -v`
Expected: 全部 PASS(monkeypatch 拦截 OpenAI 调用)。

- [ ] **Step 6: 提交**

```bash
git add shirotsume_tools/translation/agent.py shirotsume_tools/translation/__init__.py tests/test_translation_agent.py
git commit -m "feat(translation): migrate translate_agent into translation/agent.py using TextEntry"
```

---

### Task 8: 合并 CLI(6 命令)+ 更新顶层导出

**Files:**
- Modify: `shirotsume_tools/cli/commands.py` (加 patch_script_cmd/translate_scripts_cmd/sync_translation_csvs_cmd)
- Modify: `shirotsume_tools/cli/__init__.py` (注册 3 新命令)
- Modify: `shirotsume_tools/__init__.py` (加 translation 导出)
- Modify: `tests/test_scaffold.py` (加 translation 导入)
- Modify: `tests/test_cli.py` (加 translation 命令测试)

**Interfaces:**
- Produces: 6 个 CLI 命令注册到 app

- [ ] **Step 1: 写失败测试 —— scaffold 含 translation + CLI help 含新命令**

修改 `tests/test_scaffold.py`:

```python
def test_version():
    from shirotsume_tools import __version__
    assert __version__ == "0.2.0"


def test_submodules_importable():
    from shirotsume_tools import archive, cli, export, index, parser, translation  # noqa: F401
```

在 `tests/test_cli.py` 末尾追加:

```python
def test_cli_help_includes_translation_commands():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "patch-script" in result.output
    assert "translate-scripts" in result.output
    assert "sync-translation-csvs" in result.output


def test_sync_translation_csvs_command(tmp_path):
    script = tmp_path / "1-01.txt"
    script.write_text('CreateBalloon("x", "テスト");', encoding="cp932")
    repl_dir = tmp_path / "translations"
    result = runner.invoke(app, [
        "sync-translation-csvs", str(tmp_path), "-o", str(repl_dir),
        "-e", "cp932",
    ])
    assert result.exit_code == 0
    assert (repl_dir / "1-01.csv").exists()
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_scaffold.py tests/test_cli.py -v`
Expected: FAIL —— `translation` 不可导入;scaffold 测试失败;CLI help 不含新命令。

- [ ] **Step 3: 在 `shirotsume_tools/cli/commands.py` 末尾追加 3 个翻译命令**

在文件末尾追加(保留现有 decrypt_cmd/myindex/parse_cmd 不变):

```python
from ..translation import patch_script_file, sync_translation_csvs, translate_scripts


def patch_script_cmd(
    script_path: Path = typer.Argument(help="Extracted script text file to patch"),
    replacements_path: Path = typer.Argument(help="CSV or JSON replacements"),
    out_path: Path = typer.Argument(help="Output patched script path"),
    source_encoding: str = typer.Option("cp932", "-e", "--source-encoding", help="Encoding of the extracted script"),
    mapping_path: Path | None = typer.Option(None, "-m", "--mapping", help="JSON custom character map to read/update"),
) -> None:
    """Patch dialogue strings in an extracted script and encode with custom JIS-compatible bytes."""
    count = patch_script_file(
        script_path,
        replacements_path,
        out_path,
        source_encoding=source_encoding,
        mapping_path=mapping_path,
    )
    logger.info("Patched %d text span(s) into %s", count, out_path)
    if mapping_path:
        logger.info("Updated custom encoding map: %s", mapping_path)


def translate_scripts_cmd(
    script_dir: Path = typer.Argument(help="Directory containing extracted game scripts, for example ./S"),
    replacements_dir: Path = typer.Option(
        Path("translation_patch/translations"),
        "-o",
        "--out",
        help="Directory for generated replacement CSV files",
    ),
    patched_dir: Path | None = typer.Option(
        Path("translation_patch/scripts/S"),
        "-p",
        "--patched-dir",
        help="Directory for patched script files, or omit with --no-patch",
    ),
    mapping_path: Path | None = typer.Option(
        Path("translation_patch/scripts/shiro_patch_charmap.json"),
        "-m",
        "--mapping",
        help="JSON custom character map to read/update while emitting patched scripts",
    ),
    memory_path: Path | None = typer.Option(
        Path("translation_patch/translation_memory.json"),
        "--memory",
        help="Persistent translation memory JSON file",
    ),
    model: str | None = typer.Option(None, "--model", help="OpenAI model, defaults to OPENAI_MODEL or gpt-4.1"),
    api_base_url: str | None = typer.Option(None, "--api-base-url", help="Custom OpenAI-compatible API base URL"),
    target_language: str = typer.Option("Simplified Chinese", "-t", "--target-language", help="Translation target language"),
    source_encoding: str = typer.Option("cp932", "-e", "--source-encoding", help="Encoding of extracted scripts"),
    batch_size: int = typer.Option(24, "-b", "--batch-size", min=1, help="Number of strings per OpenAI request"),
    max_source_chars: int = typer.Option(6000, "--max-source-chars", min=1, help="Maximum source characters per OpenAI request"),
    limit: int | None = typer.Option(None, "--limit", min=1, help="Translate only the first N strings"),
    story_context: str = typer.Option("", "--context", help="Global story/style context passed to the translator"),
    temperature: float = typer.Option(0.2, "--temperature", min=0.0, max=2.0, help="OpenAI sampling temperature"),
    prompt_language: str = typer.Option("en", "--prompt-language", help="System prompt language: en or zh"),
    no_patch: bool = typer.Option(False, "--no-patch", help="Write replacement CSVs only"),
) -> None:
    """Translate extracted scripts to Chinese with OpenAI and optionally emit patched script files."""
    count = translate_scripts(
        script_dir,
        replacements_dir,
        patched_dir=None if no_patch else patched_dir,
        mapping_path=None if no_patch else mapping_path,
        model=model,
        api_base_url=api_base_url,
        target_language=target_language,
        source_encoding=source_encoding,
        batch_size=batch_size,
        max_source_chars=max_source_chars,
        limit=limit,
        story_context=story_context,
        temperature=temperature,
        memory_path=memory_path,
        prompt_language=prompt_language,
    )
    logger.info("Translated %d text span(s)", count)


def sync_translation_csvs_cmd(
    script_dir: Path = typer.Argument(help="Directory containing extracted game scripts, for example ./S"),
    replacements_dir: Path = typer.Option(
        Path("translation_patch/translations"),
        "-o",
        "--out",
        help="Directory containing replacement CSV files to preserve and extend",
    ),
    source_encoding: str = typer.Option("cp932", "-e", "--source-encoding", help="Encoding of extracted scripts"),
) -> None:
    """Append newly detected text spans to replacement CSVs without calling the translation API."""
    added = sync_translation_csvs(script_dir, replacements_dir, source_encoding=source_encoding)
    logger.info("Added %d untranslated text span(s)", added)
```

- [ ] **Step 4: 更新 `shirotsume_tools/cli/__init__.py` 注册 3 新命令**

```python
import typer

from .commands import (
    decrypt_cmd,
    myindex,
    parse_cmd,
    patch_script_cmd,
    sync_translation_csvs_cmd,
    translate_scripts_cmd,
)
from .logging_config import configure_logging

app = typer.Typer(name="shirotsume_tools", help="tools for shirotsume")

app.command("decrypt")(decrypt_cmd)
app.command("myindex")(myindex)
app.command("parse")(parse_cmd)
app.command("patch-script")(patch_script_cmd)
app.command("translate-scripts")(translate_scripts_cmd)
app.command("sync-translation-csvs")(sync_translation_csvs_cmd)
app.callback(invoke_without_command=True)(configure_logging)

if __name__ == "__main__":
    app()
```

- [ ] **Step 5: 更新 `shirotsume_tools/__init__.py` 加 translation 导出**

```python
from . import archive, cli, export, index, parser, translation
from ._version import __version__

__all__ = ["__version__", "archive", "cli", "export", "index", "parser", "translation"]
```

- [ ] **Step 6: 运行测试验证通过**

Run: `pytest tests/test_scaffold.py tests/test_cli.py -v`
Expected: 全部 PASS。

- [ ] **Step 7: 提交**

```bash
git add shirotsume_tools/cli/commands.py shirotsume_tools/cli/__init__.py shirotsume_tools/__init__.py tests/test_scaffold.py tests/test_cli.py
git commit -m "feat(cli): merge 3 translation commands and export translation submodule"
```

---

### Task 9: 删除旧扁平文件 + 全量测试

**Files:**
- Delete: `shirotsume_tools/decrypt.pyx`, `shirotsume_tools/decrypt.c`, `shirotsume_tools/_decrypt.cpp`, `shirotsume_tools/decrypt.h`, `shirotsume_tools/decrypt.pxd`, `shirotsume_tools/decrypt.pyi`
- Delete: `shirotsume_tools/myindex.py`, `shirotsume_tools/repack.py`, `shirotsume_tools/script_patch.py`, `shirotsume_tools/translate_agent.py`, `shirotsume_tools/custom_encoding.py`

**Interfaces:**
- Produces: 仓库只保留新模块化结构

- [ ] **Step 1: 删除旧扁平文件**

Run:
```powershell
Remove-Item -Path "shirotsume_tools\decrypt.pyx", "shirotsume_tools\decrypt.c", "shirotsume_tools\_decrypt.cpp", "shirotsume_tools\decrypt.h", "shirotsume_tools\decrypt.pxd", "shirotsume_tools\decrypt.pyi", "shirotsume_tools\myindex.py", "shirotsume_tools\repack.py", "shirotsume_tools\script_patch.py", "shirotsume_tools\translate_agent.py", "shirotsume_tools\custom_encoding.py" -Force
```

- [ ] **Step 2: 验证包仍可导入**

Run: `python -c "import shirotsume_tools; print(shirotsume_tools.__version__); from shirotsume_tools import archive, cli, export, index, parser, translation; print('OK')"`
Expected: `0.2.0` + `OK`

- [ ] **Step 3: 运行全量测试**

Run: `pytest tests/ -v`
Expected: 全部 PASS。

- [ ] **Step 4: 提交**

```bash
git rm shirotsume_tools/decrypt.pyx shirotsume_tools/decrypt.c shirotsume_tools/_decrypt.cpp shirotsume_tools/decrypt.h shirotsume_tools/decrypt.pxd shirotsume_tools/decrypt.pyi shirotsume_tools/myindex.py shirotsume_tools/repack.py shirotsume_tools/script_patch.py shirotsume_tools/translate_agent.py shirotsume_tools/custom_encoding.py
git commit -m "chore: remove legacy flat modules replaced by modular architecture"
```

---

### Task 10: 端到端验证

**Files:**
- 验证 CLI 流水线(不改动代码)

**Interfaces:**
- Produces: 验证完整的 .dat → .txt → .myi → .csv → 翻译 → 补丁 流水线

- [ ] **Step 1: 编译 Cython 扩展**

Run:
```powershell
$env:USE_CYTHON = "1"; pip install -e .
```
Expected: 成功编译 `shirotsume_tools.archive._decrypt`。

- [ ] **Step 2: 验证 CLI help 列出 6 命令**

Run: `python -m shirotsume_tools --help`
Expected: 列出 decrypt/myindex/parse/patch-script/translate-scripts/sync-translation-csvs。

- [ ] **Step 3: 验证 decrypt 流水线(用真实 S.dat)**

Run:
```powershell
python -m shirotsume_tools decrypt "..\S.dat" -o S_test
```
Expected: 解包成功,`S_test/` 下生成 .txt 脚本文件。

- [ ] **Step 4: 验证 parse 流水线**

Run:
```powershell
python -m shirotsume_tools parse S_test -i S_test.myi -c S_test.csv -e cp932
```
Expected: 生成 `S_test.myi` 和 `S_test.csv`,日志显示解析的语句数和字符数。

- [ ] **Step 5: 验证 myindex 流水线**

Run:
```powershell
python -m shirotsume_tools myindex S_test.myi -c S_test_myi.csv
```
Expected: 从 .myi 生成 CSV。

- [ ] **Step 6: 验证 sync-translation-csvs**

Run:
```powershell
python -m shirotsume_tools sync-translation-csvs S_test -o translations_test -e cp932
```
Expected: 在 `translations_test/` 下生成对应 .csv 文件,日志显示新增条目数。

- [ ] **Step 7: 验证 patch-script**

Run:
```powershell
python -m shirotsume_tools patch-script "S_test\1-01.txt" "translations_test\1-01.csv" "out_test\1-01.txt" -e cp932
```
Expected: 生成 `out_test\1-01.txt`(若 1-01.txt 不存在,选一个存在的脚本文件)。

- [ ] **Step 8: 运行全量测试**

Run: `pytest tests/ -v`
Expected: 全部 PASS。

- [ ] **Step 9: 清理验证产物**

Run:
```powershell
Remove-Item -Path "S_test", "S_test.myi", "S_test.csv", "S_test_myi.csv", "translations_test", "out_test" -Recurse -Force
```

- [ ] **Step 10: 提交(如有改动)**

如果验证过程中无代码改动,跳过提交。否则:
```bash
git add -A
git commit -m "test: end-to-end validation of migrated pipeline"
```

---

## Self-Review

**1. Spec coverage:**
- §2.1 目录结构 → Task 2(复制核心)+ Task 4-7(新建 translation/+writer)+ Task 9(删除旧文件)✓
- §3.1 archive/writer.py → Task 4 ✓
- §3.2 数据模型统一 TextEntry → Task 6(patch)+ Task 7(agent)✓
- §3.3 parser 5 函数 + parse_script_text → Task 3 ✓
- §3.4 translation/ 子模块 → Task 5(encoding)+ Task 6(patch)+ Task 7(agent)✓
- §3.5 OpenAI 调用保留 → Task 7 ✓
- §4 CLI 6 命令 → Task 8 ✓
- §5 依赖与构建 → Task 1 ✓
- §6 测试 → Task 2(迁移)+ Task 3-7(新增)+ Task 8(scaffold)✓
- §7 顶层导出 → Task 8 ✓
- §9 文件清理 → Task 9 ✓
- §10 验证流水线 → Task 10 ✓

**2. Placeholder scan:** 无 TBD/TODO,所有步骤含具体代码或命令。✓

**3. Type consistency:**
- `parse_script_text(script: str, *, file_path: str = "", encoding: str = "utf-8") -> list[TextEntry]` — Task 3 定义,Task 6 使用 ✓
- `TextEntry(text, file_path, line, start, stop)` — Task 3 导出,Task 6/7 使用 `.text`/`.start`/`.stop`/`.file_path` ✓
- `PackEntry(name, data, crypt_type=1)` — Task 4 定义 ✓
- `patch_script_text(script, replacements) -> (str, int)` — Task 6 定义,Task 7 不直接用但 patch_script_file 被用 ✓
- `translate_scripts(...)` 参数 — Task 7 定义,Task 8 CLI 调用参数对齐 ✓

无类型不一致。
