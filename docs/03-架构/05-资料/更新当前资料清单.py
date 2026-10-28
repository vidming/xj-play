"""更新当前资料指纹，不赋予审批效力；检查结果独立维护以免循环引用。"""
import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "docs/README.md").is_file())
TARGET = ROOT / "docs/03-架构/04-评审/当前资料清单.json"
EXCLUDED = {TARGET, TARGET.with_name("当前验证记录.json")}
LOCAL_ONLY = {"00-项目管理", "04-变更与复盘", "05-工具"}
EXCLUDED_DIRS = {"__pycache__"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}
files = [
    p for p in (ROOT / "docs").rglob("*")
    if p.is_file() and p not in EXCLUDED
    and not any(part.startswith(".") for part in p.relative_to(ROOT / "docs").parts)
    and not EXCLUDED_DIRS.intersection(p.relative_to(ROOT / "docs").parts)
    and p.suffix not in EXCLUDED_SUFFIXES
    and p.relative_to(ROOT / "docs").parts[0] not in LOCAL_ONLY
]
files += [ROOT / name for name in ("README.md", "AGENTS.md", "PRODUCT.md", "DESIGN.md")]
items = []
for file in sorted(files):
    data = file.read_bytes()
    items.append({
        "path": file.relative_to(ROOT).as_posix(),
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
    })
TARGET.write_text(json.dumps({
    "date": datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat(),
    "status": "当前设计与实现资料快照；不是重新批准或完整架构验收",
    "authority": "docs/03-架构/01-决策/当前有效决策.md",
    "entry": "docs/README.md",
    "exclusions": ["本清单及当前验证记录，避免指纹循环；本地忽略目录、隐藏文件与Python字节码缓存不纳入；源码仓库不在此文档清单内"],
    "files": items,
}, ensure_ascii=False, indent=2) + "\n")
print(f"已更新当前资料清单：{len(items)}份文件")
