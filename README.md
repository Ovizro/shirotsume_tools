# shirotsume_tools

白詰草話 (Shirotsume) 脚本 extraction / parsing / translation toolkit.

## 功能

- **解包 `.dat` 档案** — Cython 加速的解密/解压流程,支持 NEC 特殊字符编码
- **解析脚本语法** — 基于 ANTLR4 的语法分析器,提取 `CreateBalloon` / `CreateBalloonEx` / `CreateBalloonBie` / `CreateText` / `AddText` 五类文本指令
- **索引导出** — 将提取的文本生成 `.myi` 索引文件并导出为 CSV / Excel
- **翻译辅助** — 对接 OpenAI API 批量翻译,支持翻译记忆 (glossary / characters / style / decisions) 和增量同步
- **脚本回填** — 将翻译后的文本编码回 JIS 兼容字节并写回脚本文件,支持自定义字符映射 (CP932 私用区)

## 安装

需要 Python >= 3.10。推荐使用 [uv](https://docs.astral.sh/uv/):

```bash
# 从 git 源安装 (含 Cython 编译)
uv pip install "git+https://github.com/Ovizro/shirotsume_tools.git"

# 安装可选依赖
uv pip install "git+https://github.com/Ovizro/shirotsume_tools.git#egg=shirotsume_tools[export,translation]"
```

也可以从本地克隆安装:

```bash
git clone https://github.com/Ovizro/shirotsume_tools.git
cd shirotsume_tools
uv sync --all-extras          # 创建 .venv 并安装全部依赖
# 或仅安装核心依赖:
uv sync
```

### 可选依赖

| Extra | 包 | 用途 |
|-------|------|------|
| `export` | pandas, openpyxl | CSV / Excel 导出 |
| `translation` | openai | OpenAI 翻译 API |
| `dev` | ruff, coverage, pytest, cython | 开发与测试 |

未安装 `translation` 时调用翻译命令会提示 `pip install shirotsume_tools[translation]`。

## 使用

### CLI

```bash
python -m shirotsume_tools --help
```

六个子命令:

```
decrypt                解包 .dat 档案
parse                  解析脚本目录,生成 .myi 索引 + CSV
myindex                从 .myi 索引导出 CSV / Excel
sync-translation-csvs  扫描脚本,将新文本追加到翻译 CSV (不调用 API)
translate-scripts      批量翻译脚本并回填 (需要 openai)
patch-script           将翻译后的文本编码回单个脚本文件
```

### 典型工作流

```bash
# 1. 解包游戏数据
python -m shirotsume_tools decrypt S.dat -o S_out

# 2. 解析脚本,生成索引和 CSV
python -m shirotsume_tools parse S_out -i S.myi -c S.csv -e cp932

# 3. (可选) 从索引导出 Excel
python -m shirotsume_tools myindex S.myi -x S.xlsx

# 4. 生成翻译 CSV 骨架 (不调用 API)
python -m shirotsume_tools sync-translation-csvs S_out -o translations -e cp932

# 5. 编辑 translations/ 下的 CSV 填入翻译,然后回填到脚本
python -m shirotsume_tools patch-script S_out/1-01.txt translations/1-01.csv out/1-01.txt -e cp932

# 或者用 OpenAI 自动翻译并回填
python -m shirotsume_tools translate-scripts S_out -o translations -p patched_scripts -e cp932
```

### Python API

```python
from shirotsume_tools.archive import decrypt, read_pack, replace_entries
from shirotsume_tools.parser import parse_script, parse_script_text, TextEntry
from shirotsume_tools.translation import (
    sync_translation_csvs,
    translate_scripts,
    patch_script_file,
    encode_script_text,
)
```

## 开发

```bash
git clone https://github.com/Ovizro/shirotsume_tools.git
cd shirotsume_tools
uv sync --all-extras          # 安装全部依赖 (含 dev)
uv run pytest tests/ -v       # 运行测试
uv run ruff check .           # lint
```

Cython 扩展在安装时自动从 `.pyx` 编译。如需强制重新编译:

```bash
USE_CYTHON=1 uv sync --reinstall-package shirotsume_tools
```

## 许可证

GPL-3.0-or-later
