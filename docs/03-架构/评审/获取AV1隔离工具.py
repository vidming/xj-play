#!/usr/bin/env python3
"""按当前验证记录的精确URL/摘要获取工具，只写独立验证目录。"""

import base64
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import urllib.request


def main():
    root = Path(__file__).resolve().parents[3]
    work = Path(sys.argv[1]).resolve()
    if work == root or work.is_relative_to(root) or root.is_relative_to(work):
        raise ValueError("Verification directory must be separate from the project")
    record = json.loads((root / "docs/03-架构/评审/当前验证记录.json").read_text())
    specs = record["localCompatibilityValidation"]["toolDownloads"]
    work.mkdir(parents=True, exist_ok=True)
    (work / "tools").mkdir()
    (work / "downloads").mkdir()
    (work / "evidence").mkdir(exist_ok=True)
    results = []
    for item in specs:
        name = item["tool"]
        archive = work / "downloads" / (name + ".tgz")
        digest = hashlib.new(item["algorithm"])
        with urllib.request.urlopen(item["url"], timeout=60) as response, archive.open("xb") as output:
            while block := response.read(1024 * 1024):
                digest.update(block)
                output.write(block)
        actual = (base64.b64encode(digest.digest()).decode()
                  if item["algorithm"] == "sha512" else digest.hexdigest())
        if actual != item["expected"]:
            raise ValueError("Official artifact digest mismatch: " + name)
        target = work / "tools" / name
        target.mkdir()
        with tarfile.open(archive) as package:
            package.extractall(target, filter="data")
        results.append({"tool": name, "bytes": archive.stat().st_size,
                        "actual": actual, "status": "verified-and-extracted"})
    java = next((work / "tools/jdk").glob("*/Contents/Home/bin/java"))
    node = next((work / "tools/node").glob("*/bin/node"))
    maven = shutil.which("mvn")
    if not maven:
        raise ValueError("Existing Maven required; do not install a replacement implicitly")
    tools = {"java": str(java), "javaHome": str(java.parent.parent), "node": str(node),
             "pnpm": str(work / "tools/pnpm/package/bin/pnpm.cjs"), "maven": maven}
    (work / "tool-paths.json").write_text(json.dumps(tools, indent=2) + "\n")
    versions = {}
    policy = (
        "(version 1)(allow default)(deny network*)(deny file-write*)"
        "(allow file-write* (subpath " + json.dumps(str(work)) + ') (literal "/dev/null"))'
        "(deny file-read* (subpath " + json.dumps(str(Path.home())) + "))"
    )
    for name, command in (
        ("node", [str(node), "--version"]), ("java", [str(java), "-version"]),
        ("pnpm", [str(node), tools["pnpm"], "--version"]),
    ):
        result = subprocess.run(
            ["/usr/bin/sandbox-exec", "-p", policy] + command, cwd=work,
            env={"PATH": str(node.parent) + ":/usr/bin:/bin", "LANG": "en_US.UTF-8"},
            capture_output=True, text=True, timeout=30,
        )
        result.check_returncode()
        versions[name] = {"exit": result.returncode, "output": result.stdout + result.stderr}
    (work / "evidence/tool-downloads.json").write_text(json.dumps(results, indent=2) + "\n")
    (work / "evidence/tool-versions.json").write_text(json.dumps(versions, indent=2) + "\n")
    print(json.dumps(versions, indent=2))


if __name__ == "__main__":
    main()
