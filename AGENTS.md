# shirotsume_tools — Agent Guide

本文档面向需要维护、扩展或调试 `shirotsume_tools` 的 AI Agent / 开发者。它描述代码结构、数据链路、关键约定和常见陷阱。

## 1. 项目定位

`shirotsume_tools` 是《白詰草話》(Shirotsume) 的脚本处理工具链，覆盖：

1. 解包 `.dat` 归档（RepiPack 格式）
2. 解析游戏脚本，提取可翻译文本
3. 构建 `.myi` 索引并导出 CSV/Excel
4. 调用 OpenAI API 批量翻译
5. 将翻译后的文本编码回脚本并写回 `.dat`

## 2. 顶层目录结构

```
shirotsume_tools/
├── shirotsume_tools/          # 主包
│   ├── archive/               # .dat 解密/解包/写回
│   ├── cli/                   # Typer 命令行
│   ├── export/                # CSV / Excel 导出
│   ├── index/                 # .myi 索引读写
│   ├── parser/                # ANTLR4 脚本解析
│   ├── translation/           # 翻译、回填、编码
│   ├── __init__.py            # 仅导出版本和子包
│   ├── __main__.py            # python -m shirotsume_tools
│   └── _version.py
├── tests/                     # pytest 测试
├── docs/superpowers/          # 设计文档
├── pyproject.toml
└── README.md
```

## 3. 模块职责与链路

### 3.1 完整工作流

```
.dat (archive)
  │
  ▼
decrypt ──► 解压后的 .txt 脚本目录
  │
  ▼
parser ──► TextEntry 列表
  │
  ▼
index ──► Index / .myi 文件
  │
  ▼
export ──► CSV / Excel（人工翻译或给 AI 参考）
  │
  ▼
translation.agent ──► 调用 OpenAI API 生成翻译
  │
  ▼
translation.patch ──► 替换原文并编码为 JIS 兼容字节
  │
  ▼
archive.writer ──► 写回 .dat
```

### 3.2 子包详细说明

#### `archive` — `.dat` 归档处理

- `reader.py`: `Archive` 上下文管理器、`decrypt()`。底层通过 Cython 扩展 `_decrypt` 加速；若 Cython 不可用，纯 Python 回退在 `writer.py` 中。
- `writer.py`: 纯 Python 实现的 `read_pack()` / `write_pack()` / `replace_entries()`，用于测试和回编译 `.dat`。
- `model.py`: `FileEntry`（Pydantic 模型）。
- `errors.py`: `ArchiveError` / `InvalidSignatureError` / `UnsupportedVersionError`。

关键调用链：
- CLI `decrypt` → `archive.decrypt()` → `Archive.extract_all()` → `_decrypt.Decryptor`
- `translation.patch.patch_dat_script()` → `archive.replace_entries()` → `read_pack()` + `write_pack()`

#### `parser` — 脚本解析

- `Shirotsume.g4` + 生成的 `ShirotsumeLexer.py` / `ShirotsumeParser.py` / `ShirotsumeListener.py`: ANTLR4 语法。
- `core.py`: `parse_script()` / `parse_script_text()` / `parse_directory()`（使用 `ProcessPoolExecutor` 并发）。
- `listener.py`: `TextExtractionListener`，从 5 类函数中提取文本：
  - `CreateBalloon`
  - `CreateBalloonEx`
  - `CreateBalloonBie`
  - `CreateText`
  - `AddText`
- `model.py`: `TextEntry(text, file_path, line, start, stop)`。

关键调用链：
- `parse_script()` → ANTLR4 `parser.program()` + `TextExtractionListener`
- `translation.agent.extract_translation_items()` → `parse_directory()`
- `translation.patch.patch_script_text()` → `parse_script_text()`

#### `index` — `.myi` 索引

- `core.py`: `Index` 类（Pydantic），可从 `list[TextEntry]` 构建。
- `model.py`: `IndexEntry(text, file_path, line, index)`。
- `io.py`: `read_index()` / `write_index()`，基于 `KoiLang` 的 `Runtime` / `Writer`。

关键调用链：
- CLI `parse` → `Index.from_text_entries(entries)` → 可选 `index.save()` / `to_csv()`
- CLI `myindex` → `Index.load()` → `to_csv()` / `to_excel()`

注意：`read_index()` 使用 `Runtime` 执行 `.myi` 文件，并通过 `env_enter`/`env_exit` 把 `IndexReader` 作为环境对象压入栈。**不要继承 `Runtime`**，应使用环境对象模式（见项目约束）。

#### `export` — CSV / Excel 导出

- `core.py`: `to_csv()` / `to_excel()` / `to_dataframe()`。
- DataFrame 列：`raw_text`, `text`, `comment`, `file`, `line`, `start`, `stop`。
- 可选依赖：`pandas`, `openpyxl`；未安装时抛出带安装提示的 `ImportError`。

#### `translation` — 翻译与回填

- `agent.py`: 核心翻译流程
  - `extract_translation_items()`：扫描脚本目录，返回相对路径的 `TextEntry`。
  - `translate_batch()` / `translate_batch_with_retry()`：调用 OpenAI `responses.create()`。
  - `translate_scripts()`：完整流程，含读取已有翻译 CSV、增量翻译、生成 CSV、可选回填。
  - `sync_translation_csvs()`：仅扫描并追加新文本到 CSV，不调用 API。
  - `load_translation_memory()` / `save_translation_memory()`：JSON 翻译记忆（glossary / characters / style / decisions / pending_suggestions）。
- `patch.py`: 脚本回填
  - `patch_script_text()`: 在字符串级别替换原文（基于 `start/stop`）。
  - `patch_script_file()`: 读文件 → 替换 → `encode_script_text()` → 写二进制。
  - `patch_dat_script()`: 用 `archive.replace_entries()` 替换 `.dat` 中的单条脚本。
  - `load_replacements()`: 支持 CSV（`raw_text,text,comment`）或 JSON。
- `encoding.py`: JIS/CP932 编码，支持自定义字符映射到私用区。
  - `encode_text()`: 先尝试 CP932；失败时查 `mapping` 或使用新的私用区码位。
  - `load_mapping()` / `save_mapping()`: JSON 字符映射读写。
- `errors.py`: `TranslationError`。

#### `cli` — 命令行

- `__init__.py`: 创建 `typer.Typer` app，注册 6 条命令。
- `commands.py`: 6 条命令实现：
  - `decrypt_cmd`
  - `parse_cmd`
  - `myindex`
  - `sync_translation_csvs_cmd`
  - `translate_scripts_cmd`
  - `patch_script_cmd`
- `logging_config.py`: `--verbose` / `-v` 日志配置。

命令与内部函数映射：

| CLI 命令 | 内部函数 |
|---------|---------|
| `decrypt` | `archive.decrypt()` |
| `parse` | `parser.parse_directory()` / `parse_script()` → `Index.from_text_entries()` |
| `myindex` | `Index.load()` → `export.to_csv()` / `to_excel()` |
| `sync-translation-csvs` | `translation.sync_translation_csvs()` |
| `translate-scripts` | `translation.translate_scripts()` |
| `patch-script` | `translation.patch_script_file()` |

## 4. 数据模型速查

```python
# parser.model.TextEntry
text: str          # 提取的文本内容
file_path: str     # 源脚本路径
line: int          # 行号
start: int         # 在文件中的起始字符位置
stop: int          # 结束字符位置

# index.model.IndexEntry
text: str
file_path: str
line: int
index: tuple[int, ...]   # (start, stop)

# archive.model.FileEntry
name: str
offset: int
size: int
comp_size: int
crypt_type: int
```

## 5. 关键约定与约束

### 5.1 模块分层

- `__init__.py` 只负责导入/导出，不能放实现代码。
- 功能按职责分到 `core.py`（主逻辑）、`model.py`（数据模型）、`errors.py`（异常）、`io.py`（I/O）。
- CLI 命令实现放在 `commands.py`，`cli/__init__.py` 只做 app 创建和注册。

### 5.2 `Runtime` 使用

- `koilang.Runtime` **不可继承**。
- 应把环境对象压入栈：`runtime.env_enter(obj)` / `runtime.env_exit(obj)`。
- 参考实现：`index/io.py` 中的 `read_index()`。

### 5.3 编码与字符映射

- 脚本默认编码是 `cp932`（不是 UTF-8）。
- 当中文字符无法直接编码 CP932 时，使用 `translation.encoding` 的自定义映射写入 JIS 私用区（`0xF040`–`0xF9FC`）。
- 映射文件是 JSON：`{ "中文字": "F040" }`（值可以是 16 进制字符串或整数）。

### 5.4 翻译 CSV 格式

- 表头：`raw_text,text,comment`
- `raw_text` 用于匹配原文；`text` 为译文。
- CSV 使用 UTF-8-BOM 编码（`utf-8-sig`），方便 Excel 打开。

### 5.5 可选依赖

- `export`: `pandas`, `openpyxl`
- `translation`: `openai`
- 未安装时函数内部抛出 `ImportError` 并附带安装命令提示，而不是在顶层导入失败。

### 5.6 ANTLR 生成文件

- `parser/Shirotsume*.py` 是 ANTLR4 生成文件，被 ruff / pyright 排除。
- 修改语法应编辑 `parser/Shirotsume.g4` 并重新生成，不要直接改生成的 Python。

## 6. 开发与测试

```bash
# 安装全部依赖
uv sync --all-extras

# 运行测试
uv run pytest tests/ -v

# lint
uv run ruff check .
uv run ruff format .
```

## 7. 常见改动场景

| 场景 | 应修改的文件 |
|------|-------------|
| 新增需要提取文本的脚本函数 | `parser/listener.py` 的 `TEXT_EXTRACTORS` |
| 调整导出 CSV 列 | `export/core.py` 的 `_to_records()` |
| 调整 OpenAI 提示词 | `translation/agent.py` 的 `translation_system_prompt()` |
| 新增字符映射规则 | `translation/encoding.py` |
| 新增 CLI 命令 | `cli/commands.py` + `cli/__init__.py` |
| 修改 `.dat` 写回逻辑 | `archive/writer.py` |

## 8. 调试提示

- 翻译结果未回填：检查 `translation.patch.patch_script_text()` 中 `start/stop` 是否与提取时一致；CP932 编码失败会走自定义映射，需确认 `mapping_path`。
- OpenAI 返回解析失败：`agent.py` 的 `_json_object_from_response()` 会剥离 Markdown 代码块，但结构必须严格匹配 `{translations:[...], memory_suggestions:[...]}`。
- `.myi` 读写异常：确认 `KoiLang` 的 `Runtime` 环境对象实现了 `do_file()` / `do_line()` / `at_text()`。
