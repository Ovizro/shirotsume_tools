# 迁移 trans-tool 重构到 shirotsume_tools 设计文档

## 1. 背景与目标

### 1.1 当前状态

存在两份代码:

- **源 `trans-tool/shirotsume_tools/`**(v0.2.0):已完成架构重构,模块化布局 `archive/` `cli/` `export/` `index/` `parser/`,使用 pydantic v2 + koilang + typer,有完整 tests/。重构设计见 `trans-tool/docs/superpowers/specs/2026-06-24-trans-tool-refactoring-design.md`。
- **目标 `shirotsume_tools/`**(v0.1.2,已发布):扁平结构,额外具备 OpenAI 翻译能力 —— `translate_agent.py`(openai SDK)、`script_patch.py`(脚本补丁,依赖 parser ANTLR 类 + custom_encoding + repack)、`repack.py`(归档重打包)、`custom_encoding.py`(JIS 兼容编码)。CLI 有 5 个命令:decrypt、myindex、patch-script、translate-scripts、sync-translation-csvs。

### 1.2 目标

把 trans-tool 的重构成果迁移到目标包 `shirotsume_tools/`,同时**深度整合**目标包的 OpenAI 翻译能力到新架构,保留翻译功能逻辑但统一数据模型与模块边界。

**核心决策(经设计对话确认):**

1. **深度整合**:翻译模块重构以使用新架构的数据模型(TextEntry/Index),而非原样保留。
2. **模块组织**:新增 `translation/` 子模块装翻译流水线;`repack.py` 的写归档能力并入 `archive/`(让 archive/ 同时负责读+写)。
3. **不保留旧 API 别名**:`MyIndex`/`parse`/`parse_file`/`get_counter`/`reset_counter`/`build_dataframe`/`Decryptor` 等旧名不保留,调用方按新路径迁移。
4. **openai 可选依赖**:核心包不含 openai;`[translation]` extra 提供 openai,与 `[export]` extra(pandas/openpyxl)模式一致。

## 2. 整体架构

### 2.1 目录结构

```
shirotsume_tools/                          # 目标包根(git 仓库)
├── pyproject.toml                         # 合并后的依赖与构建配置
├── setup.py                               # 仅保留 Cython 扩展声明
├── shirotsume_tools/
│   ├── __init__.py                        # 顶层导出(新 API,无旧别名)
│   ├── __main__.py                        # CLI app 创建 + 命令注册
│   ├── _version.py                        # __version__ = "0.2.0"
│   ├── archive/                           # 扩展:读 + 写
│   │   ├── __init__.py                    # 导出 Archive, decrypt, FileEntry, PackEntry, write_pack, replace_entries, errors
│   │   ├── reader.py                      # Archive(读)、decrypt
│   │   ├── writer.py                      # 新:PackEntry、write_pack、replace_entries(从 repack.py 迁入)
│   │   ├── model.py                       # FileEntry
│   │   ├── errors.py                      # ArchiveError, InvalidSignatureError, UnsupportedVersionError
│   │   ├── _decrypt.pyx / .pxd / .pyi / .cpp / .h
│   ├── parser/                            # 重构后的 ANTLR 解析(扩展提取器到 5 个函数)
│   │   ├── __init__.py / core.py / listener.py / model.py / errors.py
│   │   └── Shirotsume.g4 + ANTLR 生成文件
│   ├── index/                             # 不变
│   │   ├── __init__.py / core.py / io.py / model.py
│   ├── export/                            # 不变
│   │   ├── __init__.py / core.py
│   ├── translation/                       # 新子模块:翻译流水线
│   │   ├── __init__.py                    # 导出 public API
│   │   ├── agent.py                       # 从 translate_agent.py 迁入,改用 TextEntry
│   │   ├── patch.py                       # 从 script_patch.py 迁入,改用 TextEntry
│   │   ├── encoding.py                    # 从 custom_encoding.py 迁入
│   │   └── errors.py                      # TranslationError
│   └── cli/
│       ├── __init__.py                    # app + 注册 6 个命令
│       ├── commands.py                    # decrypt/myindex/parse + patch_script/translate_scripts/sync_translation_csvs
│       └── logging_config.py
└── tests/                                 # 从 trans-tool 迁入 + 新增 translation 测试
    ├── conftest.py
    ├── test_archive.py / test_archive_decrypt.py
    ├── test_parser.py / test_index.py / test_export.py
    ├── test_cli.py / test_scaffold.py
    └── test_translation.py                # 新增
```

### 2.2 模块职责

| 模块 | 职责 | 不做什么 |
|------|------|----------|
| `archive` | 读取 `.dat` 归档(`Archive`/`decrypt`),写入/重打包归档(`write_pack`/`replace_entries`) | 不做脚本解析、不碰 CSV |
| `parser` | 解析 Shirotsume 脚本,提取文本条目(5 个函数) | 不做序列化、不碰 pandas |
| `index` | 存储文本条目,读写 `.myi`/`.ktxt` | 不做导出 |
| `export` | 导出 CSV/Excel/DataFrame | 不做解析 |
| `translation` | OpenAI 翻译编排、脚本补丁、自定义编码 | 不做归档读写(依赖 archive) |
| `cli` | 命令行入口,编排各模块 | 不含业务逻辑 |

### 2.3 依赖方向(无循环)

```
cli
├── archive
├── parser
├── index
├── export
└── translation
    ├── parser (TextEntry, parse_script/parse_directory/parse_script_text)
    └── archive (replace_entries)

export → index
translation/agent → {parser, translation/patch}
translation/patch → {translation/encoding, parser, archive}
```

## 3. 关键整合点

### 3.1 `archive/writer.py`(repack 整合)

`repack.py` 是纯 Python 实现的 RepiPack 读写。Cython `_decrypt.pyx` 只负责读,写路径保留纯 Python。把 `repack.py` 整体迁入 `archive/writer.py`,逻辑原样,接入 `archive` 命名空间:

```python
# archive/writer.py
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Iterable, Mapping
import struct

@dataclass(frozen=True)
class PackEntry:
    name: str
    data: bytes
    crypt_type: int = 1

def read_pack(path: str | Path) -> tuple[bytes, list[PackEntry]]: ...   # 原样
def write_pack(path: str | Path, header: bytes, entries: Iterable[PackEntry]) -> None: ...  # 原样
def replace_entries(dat_path: str | Path, out_path: str | Path, replacements: Mapping[str, bytes]) -> None: ...  # 原样
```

`archive/__init__.py` 增加 `PackEntry`、`write_pack`、`replace_entries` 导出。写归档走函数式 API,`Archive` 类暂不加写方法(读/写路径解耦)。

### 3.2 数据模型统一(TextSpan/TranslationItem → TextEntry)

当前三处重复定义:

| 来源 | 类型 | 字段 |
|------|------|------|
| `parser/model.py` | `TextEntry` | text, file_path, line, start, stop |
| `script_patch.py` | `TextSpan` | raw_text, start, stop, line |
| `translate_agent.py` | `TranslationItem` | id, file, index, line, raw_text |

**统一方案:** 全部用 `parser.TextEntry`。

- `translation/patch.py` 的 `find_text_spans` 改为返回 `list[TextEntry]`(`file_path` 在文件级调用时填入)。
- `TranslationItem` 删除;`translation/agent.py` 直接用 `TextEntry`,`id` 由 `file_path`+索引在运行时拼出(`f"{entry.file_path}#{i}"`),不入模型。

### 3.3 parser 提取器扩展

当前两处 Listener 提取的函数集不同:

| 函数 | parser `TextExtractionListener` | patch `TextSpanListener` |
|------|:---:|:---:|
| CreateBalloon | ✓ | ✓ |
| CreateBalloonEx | ✓ | ✓ |
| AddText | ✓ | ✓ |
| CreateBalloonBie | ✗ | ✓ |
| CreateText | ✗ | ✓ |

**方案:** 把 `parser/listener.py` 的 `TEXT_EXTRACTORS` 扩展到 5 个函数,parser 与 translation 共用同一个 `TextExtractionListener`。`translation/patch.py` 不再自带 Listener,直接复用 parser 的解析能力。

**副作用:** `.myi` 索引会多出 CreateBalloonBie/CreateText 的条目(更完整,与旧索引不兼容 —— 已在"不保留旧 API"决策内接受)。

**字符串输入解析:** `patch_script_text` 接收 `script: str`(非文件路径),而 `parse_script(path)` 用 `FileStream`。为此在 `parser/core.py` 新增字符串输入变体:

```python
def parse_script_text(script: str, *, file_path: str = "", encoding: str = "utf-8") -> list[TextEntry]:
    """从字符串解析脚本,返回 TextEntry 列表(供 patch 等需要字符串输入的场景)。"""
    input_stream = InputStream(script)
    lexer = ShirotsumeLexer(input_stream)
    parser = ShirotsumeParser(CommonTokenStream(lexer))
    listener = TextExtractionListener(file_path)
    parser.addParseListener(listener)
    parser.program()
    return listener.entries
```

`translation/patch.py` 的 `find_text_spans` 删除,改为直接调用 `parse_script_text`。

### 3.4 `translation/` 子模块内部

```
translation/
├── __init__.py     # 导出: translate_scripts, sync_translation_csvs,
│                   #        patch_script_file, patch_script_text, load_replacements
├── agent.py        # OpenAI 调用: translate_batch, translate_batch_with_retry,
│                   #           translate_scripts, sync_translation_csvs,
│                   #           CSV 读写辅助, memory 管理
├── patch.py        # 脚本补丁: patch_script_text, patch_script_file, patch_dat_script,
│                   #          _escape_script_string, normalize_replacement_text,
│                   #          load_replacements
├── encoding.py     # custom_encoding.py 原样迁入
└── errors.py       # TranslationError
```

**导入调整:**

- `agent.py`:`from .patch import patch_script_file`(替代 `from .script_patch import ...`)
- `patch.py`:`from ..parser import TextEntry, parse_script_text`(字符串输入解析);`from ..archive import replace_entries`(替代 `from .repack import replace_entries`);`from .encoding import encode_script_text, load_mapping, save_mapping`
- `agent.py` 的 `extract_translation_items` 用 `parse_directory`/`parse_script` 返回的 `TextEntry` 列表(文件级解析);`patch.py` 的 `patch_script_text` 用 `parse_script_text` 解析字符串并定位 span 偏移。

### 3.5 OpenAI 调用保留点

`agent.py` 的 OpenAI 调用逻辑原样保留:

- `translate_batch`:`client.responses.create(model=..., input=[system, user], temperature=...)`
- `translate_batch_with_retry`:二分重试策略不变
- 系统提示词(`translation_system_prompt`,en/zh 双语)、memory JSON 结构、CSV 格式全部不变

仅外层适配 `TextEntry`:

```python
# 旧
items: list[TranslationItem]  # 自定义 dataclass
payload "items" 从 item.raw_text / item.id 构造

# 新
items: list[TextEntry]        # 复用 parser 模型
payload "items" 从 item.text / f"{item.file_path}#{i}" 构造
```

`from openai import OpenAI` 保持延迟导入,`ModuleNotFoundError` 转为 `RuntimeError("Install with: pip install shirotsume_tools[translation]")`,与 `export/core.py` 处理 pandas 的方式一致。

## 4. CLI 命令

`cli/commands.py` 合并源包和目标包的命令,共 6 个:

| 命令 | 来源 | 主要改动 |
|------|------|----------|
| `decrypt` | 源包 | 不变 |
| `myindex` | 源包 | 不变(用 `Index.load`/`to_csv`/`to_excel`) |
| `parse` | 源包 | 不变 |
| `patch-script` | 目标包 | `from ..translation import patch_script_file` |
| `translate-scripts` | 目标包 | `from ..translation import translate_scripts` |
| `sync-translation-csvs` | 目标包 | `from ..translation import sync_translation_csvs` |

`translate-scripts` 和 `sync-translation-csvs` 的所有 Typer 参数(model/api_base_url/batch_size/memory_path/limit/temperature/story_context/prompt_language/no_patch 等)原样保留。`cli/__init__.py` 注册全部 6 个命令 + `configure_logging` 回调。

## 5. 依赖与构建

### 5.1 `pyproject.toml`

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

[tool.setuptools.dynamic]
version = {attr = "shirotsume_tools._version.__version__"}
```

### 5.2 `setup.py`(仅 Cython 扩展)

```python
import os
from setuptools import setup, Extension

USE_CYTHON = "USE_CYTHON" in os.environ
FILE_SUFFIX = ".pyx" if USE_CYTHON else ".c"

extensions = [
    Extension(
        "shirotsume_tools.archive._decrypt",
        ["shirotsume_tools/archive/_decrypt" + FILE_SUFFIX,
         "shirotsume_tools/archive/_decrypt.cpp"],
    ),
]

if USE_CYTHON:
    from Cython.Build import cythonize
    extensions = cythonize(extensions, annotate=True,
                           compiler_directives={"language_level": "3"})

setup(ext_modules=extensions)
```

扩展名从 `shirotsume_tools.decrypt` 改为 `shirotsume_tools.archive._decrypt`(随模块化调整)。

### 5.3 删除 `setup.cfg`

其内容仅 `[egg_info]` 无关紧要,删除。

## 6. 测试

从 `trans-tool/tests/` 整体迁入 `shirotsume_tools/tests/`:

- `conftest.py`、`test_archive.py`、`test_archive_decrypt.py`、`test_parser.py`、`test_index.py`、`test_export.py`、`test_cli.py`、`test_scaffold.py` 原样迁移
- `test_scaffold.py` 的 `test_submodules_importable` 扩展为:
  ```python
  from shirotsume_tools import archive, cli, export, index, parser, translation
  ```
- 新增 `test_translation.py`,覆盖:
  - `parse_script_text`:5 个函数(CreateBalloon/CreateBalloonEx/CreateBalloonBie/CreateText/AddText)提取
  - `patch_script_text`:Mapping 和 Sequence 两种 replacements 模式
  - `encode_text`:自定义映射分配新码点
  - `sync_translation_csvs`:新增条目追加,已有翻译保留
  - `replace_entries`:写回归档往返一致
  - OpenAI 调用用 monkeypatch 桩,不发真实请求

## 7. 顶层导出

`shirotsume_tools/__init__.py`:

```python
from . import archive, cli, export, index, parser, translation
from ._version import __version__

__all__ = ["__version__", "archive", "cli", "export", "index", "parser", "translation"]
```

不导出 `decrypt`、`MyIndex`、`parse`、`build_dataframe`、`translate_scripts` 等旧顶层名;调用方走 `shirotsume_tools.translation.translate_scripts` 等子模块路径。

## 8. 旧 → 新 API 迁移映射

| 旧 API(目标包) | 新 API |
|---|---|
| `from shirotsume_tools import decrypt` | `from shirotsume_tools.archive import decrypt` |
| `from shirotsume_tools import MyIndex` | `from shirotsume_tools.index import Index` |
| `from shirotsume_tools import parse, parse_file` | `from shirotsume_tools.parser import parse_script, parse_directory` |
| `from shirotsume_tools import build_dataframe` | `from shirotsume_tools.export import to_dataframe` |
| `from shirotsume_tools import patch_script_file` | `from shirotsume_tools.translation import patch_script_file` |
| `from shirotsume_tools.translate_agent import translate_scripts` | `from shirotsume_tools.translation import translate_scripts` |
| `from shirotsume_tools.repack import replace_entries` | `from shirotsume_tools.archive import replace_entries` |
| `from shirotsume_tools.custom_encoding import encode_text` | `from shirotsume_tools.translation.encoding import encode_text` |
| `MyIndex().parse_file(path)` | `Index.load(path)` 或 `parse_script` + `Index.from_text_entries` |
| `MyIndex().save_csv(path)` | `to_csv(index, path)` |
| `Decryptor` | `Archive` |

## 9. 文件清理(目标包)

迁移完成后从目标包删除:

- `shirotsume_tools/decrypt.pyx`/`decrypt.c`/`_decrypt.cpp`/`decrypt.h`/`decrypt.pxd`/`decrypt.pyi`(被 `archive/_decrypt.*` 取代)
- `shirotsume_tools/myindex.py`、`repack.py`、`script_patch.py`、`translate_agent.py`、`custom_encoding.py`(已迁入子模块)
- `shirotsume_tools/parser/__init__.py` 旧版(全局计数器)被新版覆盖
- `setup.cfg`、`PKG-INFO`(构建产物)
- `shirotsume_tools/__init__.py`、`__main__.py` 旧版被新版覆盖

## 10. 验证流水线

迁移完成后端到端验证:

1. `python -m shirotsume_tools decrypt S.dat -o S` — 解包
2. `python -m shirotsume_tools parse S -i S.myi -c S.csv` — 解析+索引+导出
3. `python -m shirotsume_tools myindex S.myi -c S.csv` — 索引转 CSV
4. `python -m shirotsume_tools sync-translation-csvs S -o translations` — 同步翻译 CSV
5. `python -m shirotsume_tools patch-script S/1-01.txt translations/1-01.csv out/1-01.txt` — 补丁脚本
6. `pytest` — 全部测试通过

## 11. 决策记录

| 决策 | 理由 |
|---|---|
| 深度整合(重构翻译模块用新数据模型) | 用户选择;统一 TextEntry 消除三处重复定义,与模块化架构一致 |
| 新增 `translation/` 子模块 | 翻译流水线自成体系,与核心库(archive/parser/index/export)解耦 |
| `repack.py` 并入 `archive/writer.py` | 归档读+写同域,Cython 只读、纯 Python 写,函数式 API 解耦 |
| parser 提取器扩展到 5 个函数 | 消除 patch Listener 与 parser Listener 的重复;CreateBalloonBie/CreateText 也是文本函数,索引更完整 |
| 不保留旧 API 别名 | 用户选择;与 trans-tool 重构决策一致,代码最干净 |
| openai 可选 `[translation]` extra | 与 `[export]` extra 模式一致,核心包不增重 |
| 版本 0.2.0 | 对齐 trans-tool 重构版本 |
| Cython 扩展名 `archive._decrypt` | 随模块化路径调整 |
| 删除 `setup.cfg` | 内容无关紧要 |
| OpenAI 调用逻辑原样保留 | 已验证可用,仅外层适配 TextEntry |

## 12. 后续步骤

1. 编写实现计划(`writing-plans` skill)。
2. 按模块逐个实现与测试:archive/writer → parser 扩展 → translation/ → cli 合并 → 顶层导出 → 清理 → 测试。
3. 端到端验证流水线。
