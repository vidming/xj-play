#!/usr/bin/env python3
"""AV1管理端预检：固定锁安装，源配置排除，替身请求层，仅测试副本。"""

import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import time


def main():
    root = Path(__file__).resolve().parents[3]
    work = Path(sys.argv[1]).resolve()
    tools = json.loads((work / "tool-paths.json").read_text())
    if len(sys.argv) > 2 and not sys.argv[2].startswith("--"):
        preflight = json.loads(Path(sys.argv[2]).read_text())
    else:
        current = json.loads((root / "docs/03-架构/评审/当前验证记录.json").read_text())
        preflight = current["localCompatibilityValidation"]["adminPreflight"]
    reuse = "--reuse-copy" in sys.argv[2:]
    source = root / "frontend/yudao-ui-admin-vue3"
    if work == root or work.is_relative_to(root) or root.is_relative_to(work):
        raise ValueError("Verification directory must be separate from the project")
    dest = work / "admin"
    dest.mkdir(exist_ok=reuse)
    evidence = work / "evidence"
    roots = set(preflight["copy_allowlist"]["reviewed_root_files"])
    extensions = {
        ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".vue", ".json",
        ".css", ".scss", ".less", ".svg", ".png", ".jpg", ".jpeg", ".gif",
        ".ico", ".webp", ".woff", ".woff2", ".ttf", ".eot", ".mp3", ".wav",
    }
    manifest = []
    paths = []
    for folder, directories, filenames in os.walk(source, followlinks=False):
        parent = Path(folder)
        relative = parent.relative_to(source)
        directories[:] = [
            name for name in directories
            if not name.startswith(".") and not name.startswith("dist")
            and name not in {"node_modules", "target", "coverage"}
            and not (relative.parts == ("src",) and name == "config")
            and (parent != source or name in {"src", "types", "public", "build"})
            and not (parent / name).is_symlink()
        ]
        paths.extend(parent / name for name in filenames)
    for path in sorted(paths):
        rel = path.relative_to(source)
        parts = rel.parts
        if path.is_symlink() or any(parent.is_symlink() for parent in path.parents):
            continue
        if not path.is_file():
            continue
        if any(x.startswith(".") or x in {
            "node_modules", "dist", "target", "coverage"
        } or x.startswith("dist-") for x in parts):
            continue
        if parts[:2] == ("src", "config"):
            continue
        allowed = rel.as_posix() in roots or (
            parts[0] in {"src", "types", "public", "build"} and path.suffix.lower() in extensions
        )
        if not allowed:
            continue
        # O_NOFOLLOW防止盘点与读取之间被替换成链接。
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(fd, "rb") as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise ValueError("Non-regular whitelist source")
            data = stream.read()
        if b"-----BEGIN PRIVATE KEY-----" in data or b"-----BEGIN RSA PRIVATE KEY-----" in data:
            raise ValueError("Private material detected in whitelist source; refusing copy")
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if reuse and target.exists():
            if target.read_bytes() != data:
                raise ValueError("Existing copy changed; refusing to overwrite")
        else:
            with target.open("xb") as stream:
                stream.write(data)
        manifest.append({"path": rel.as_posix(), "sha256": hashlib.sha256(data).hexdigest()})
    (evidence / "admin-source-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    )
    config = dest / "src/config/axios"
    config.mkdir(parents=True, exist_ok=reuse)
    (config / "index.ts").write_text("""// AV1副本替身：只用于编译，不发送请求。
const unavailable = async <T = any>(..._args: any[]): Promise<T> => {
  throw new Error('AV1 request adapter is intentionally unavailable')
}
export default {
  get: unavailable, post: unavailable, put: unavailable, delete: unavailable,
  download: unavailable, upload: unavailable, patch: unavailable,
  postOriginal: unavailable, getOriginal: unavailable
}
""")
    (config / "service.ts").write_text("export const isRelogin = { show: false }\n")
    (config / "config.ts").write_text(
        "export const config = { base_url: 'https://av1-preflight.invalid', "
        "result_code: 200, default_headers: 'application/json', request_timeout: 30000 }\n"
    )
    (dest / ".env.av1-preflight").write_text(
        "".join(k + "=" + v + "\n" for k, v in preflight["validation_environment"]["values"].items())
    )
    (dest / "pnpm-workspace.yaml").write_text("packages: []\nonlyBuiltDependencies: []\n")
    env = {
        "PATH": str(Path(tools["node"]).parent) + ":/usr/bin:/bin",
        "LANG": "en_US.UTF-8", "CI": "true",
        "XDG_CACHE_HOME": str(work / "cache"), "XDG_CONFIG_HOME": str(work / "config"),
        "npm_config_userconfig": str(work / "empty-npmrc"),
        "npm_config_globalconfig": str(work / "empty-global-npmrc"),
        "TMPDIR": str(work / "tmp"),
    }
    (work / "tmp").mkdir(exist_ok=True)
    for filename in ("empty-npmrc", "empty-global-npmrc"):
        (work / filename).touch()
    results = []
    if reuse:
        previous = json.loads((evidence / "admin-results.json").read_text())
        results = [result for result in previous["results"] if result["step"] == "install"]

    def run(name, args, sandbox=False):
        log = evidence / ("admin-" + name + ".log")
        started = time.monotonic()
        policy = (
            "(version 1)(allow default)(deny file-write*)"
            "(allow file-write* (subpath " + json.dumps(str(work)) + ') (literal "/dev/null"))'
            "(deny file-read* (subpath " + json.dumps(str(Path.home())) + "))"
        )
        if sandbox:
            policy += "(deny network*)"
        args = ["/usr/bin/sandbox-exec", "-p", policy] + args
        with log.open("w") as stream:
            try:
                code = subprocess.run(args, cwd=dest, env=env, stdout=stream,
                                      stderr=subprocess.STDOUT, timeout=900).returncode
            except subprocess.TimeoutExpired:
                code = 124
        result = {"step": name, "exit": code, "seconds": round(time.monotonic() - started, 1),
                  "log": log.name, "networkAndUserHomeReadDenied": sandbox,
                  "userHomeReadDenied": True, "writesRestrictedToVerificationDirectory": True}
        results.append(result)
        (evidence / "admin-results.json").write_text(json.dumps({
            "results": results, "lifecycleWhitelist": [],
            "limits": "Source config/axios excluded and replaced with unavailable stubs; "
                      "not a full original request-layer compatibility check",
        }, indent=2) + "\n")
        print(json.dumps(result), flush=True)
        return code

    if not reuse and run("install", [tools["node"], tools["pnpm"], "install", "--frozen-lockfile",
                       "--ignore-scripts", "--ignore-pnpmfile", "--side-effects-cache=false",
                       "--store-dir", str(work / "pnpm-store"),
                       "--registry=https://registry.npmjs.org"]) != 0:
        return 1
    inventory = {}
    for path in (dest / "node_modules/.pnpm").glob("*/node_modules/**/package.json"):
        resolved = path.resolve()
        if not resolved.is_relative_to(dest):
            raise ValueError("Dependency escapes verification tree")
        if resolved in inventory:
            continue
        package = json.loads(path.read_text())
        scripts = {k: v for k, v in package.get("scripts", {}).items()
                   if k in {"preinstall", "install", "postinstall", "prepare"}}
        if scripts:
            inventory[resolved] = {
                "name": package.get("name"), "version": package.get("version"), "scripts": scripts,
            }
    (evidence / "admin-lifecycle-inventory.json").write_text(
        json.dumps(list(inventory.values()), indent=2) + "\n"
    )
    run("types", [tools["node"], "--max_old_space_size=8192",
                 "./node_modules/vue-tsc/bin/vue-tsc.js", "--noEmit", "--incremental",
                 "--tsBuildInfoFile", "node_modules/.cache/vue-tsc/tsconfig.tsbuildinfo"], True)
    run("build", [tools["node"], "--max_old_space_size=8192",
                 "./node_modules/vite/bin/vite.js", "build", "--mode", "av1-preflight"], True)
    for filename in ("package.json", "pnpm-lock.yaml"):
        assert (source / filename).read_bytes() == (dest / filename).read_bytes()
    return 1 if any(result["exit"] for result in results) else 0


if __name__ == "__main__":
    sys.exit(main())
