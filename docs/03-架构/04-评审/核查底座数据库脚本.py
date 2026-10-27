"""只读核查底座DDL和实体表名；不输出种子数据、不连接数据库或执行SQL。

这只是针对当前导出格式的静态扫描，不是通用SQL解析器或兼容验收。
"""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "docs/README.md").is_file())
BACKEND = ROOT / "backend/yudao-boot-mini"
DDL_PATTERN = re.compile(
    r"^CREATE TABLE\s+`(?P<name>[^`]+)`\s*\((?P<body>.*?)"
    r"^\)\s*(?P<options>ENGINE\b[^;]*);", re.M | re.S | re.I
)


def audit_sql(relative):
    path = BACKEND / relative
    data = path.read_bytes()
    text = data.decode("utf-8-sig")
    tables = []
    for match in DDL_PATTERN.finditer(text):
        body, options = match.group("body", "options")
        foreign_keys = [
            {"columns": re.findall(r"`([^`]+)`", fk[0]),
             "target": fk[1], "targetColumns": re.findall(r"`([^`]+)`", fk[2])}
            for fk in re.findall(
                r"FOREIGN KEY\s*\(([^)]+)\)\s*REFERENCES\s*`([^`]+)`\s*\(([^)]+)\)",
                body, re.I
            )
        ]
        tables.append({
            "table": match.group("name"),
            "line": text.count("\n", 0, match.start()) + 1,
            "engine": re.search(r"ENGINE\s*=\s*(\w+)", options, re.I).group(1),
            "explicitDynamicRow": bool(re.search(r"ROW_FORMAT\s*=\s*DYNAMIC", options, re.I)),
            "jsonColumns": len(re.findall(r"^\s*`[^`]+`\s+json\b", body, re.M | re.I)),
            "foreignKeys": foreign_keys,
        })
    declared = len(re.findall(r"^CREATE TABLE\b", text, re.M | re.I))
    if len(tables) != declared:
        raise ValueError(f"{relative}: DDL扫描仅覆盖{len(tables)}/{declared}，需人工复核格式")
    names = [table["table"] for table in tables]
    if len(set(names)) != len(names):
        raise ValueError(f"{relative}: 重复CREATE TABLE")
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": hashlib.sha256(data).hexdigest(),
        "createTables": declared,
        "dropTables": len(re.findall(r"^DROP TABLE\b", text, re.M | re.I)),
        "foreignKeyChecksStatements": len(re.findall(
            r"^SET\s+FOREIGN_KEY_CHECKS\b", text, re.M | re.I)),
        "physicalForeignKeys": sum(len(t["foreignKeys"]) for t in tables),
        "engines": dict(Counter(t["engine"] for t in tables)),
        "tables": tables,
    }


def entity_mappings():
    mappings = []
    for module in ("system", "infra"):
        base = BACKEND / f"yudao-module-{module}/src/main/java/cn/iocoder/yudao/module/{module}/dal/dataobject"
        for path in sorted(base.rglob("*.java")):
            text = path.read_text()
            for match in re.finditer(r'@TableName\s*\(\s*(?:value\s*=\s*)?"([^"]+)"', text):
                mappings.append({
                    "table": match.group(1), "module": module,
                    "path": path.relative_to(ROOT).as_posix(),
                    "line": text.count("\n", 0, match.start()) + 1,
                })
    return mappings


def audit():
    scripts = [audit_sql(f"sql/mysql/{name}") for name in ("ruoyi-vue-pro.sql", "quartz.sql")]
    mappings = entity_mappings()
    entities = {row["table"] for row in mappings}
    base_tables = {row["table"] for row in scripts[0]["tables"]}
    return {
        "scope": "当前格式静态扫描；读SQL文件字节但仅输出DDL元数据，未提取或展示种子行",
        "scripts": scripts,
        "entityMappings": mappings,
        "mappingComparison": {
            "mappings": len(mappings), "uniqueTables": len(entities),
            "modules": dict(Counter(row["module"] for row in mappings)),
            "tablesWithoutEntity": sorted(base_tables - entities),
            "entitiesWithoutTable": sorted(entities - base_tables),
        },
        "limits": "不解析有效POM、ORM动态SQL或运行配置；不验证5.7.14真实建表、权限、事务或调度行为",
    }


if __name__ == "__main__":
    print(json.dumps(audit(), ensure_ascii=False, indent=2))
