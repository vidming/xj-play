#!/usr/bin/env python3
"""AV1：仅复制 POM、Lombok编译约定与主源码，不启动任何应用。"""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


def main():
    root = next(parent for parent in Path(__file__).resolve().parents if (parent / "docs/README.md").is_file())
    work = Path(sys.argv[1]).resolve()
    compile_only = "--compile-only" in sys.argv[2:]
    if work == root or work.is_relative_to(root) or root.is_relative_to(work):
        raise ValueError("Verification directory must be separate from the project")
    tools = json.loads((work / "tool-paths.json").read_text())
    source = root / "backend/yudao-boot-mini"
    evidence = work / "evidence"
    records = []
    for path in sorted(source.rglob("*")):
        rel = path.relative_to(source)
        if any(part in {".git", "target", "node_modules"} for part in rel.parts):
            continue
        allowed = path.name in {"pom.xml", "lombok.config"} or (
            path.suffix == ".java" and "/src/main/java/" in "/" + rel.as_posix()
        )
        if not allowed or not path.is_file():
            continue
        if path.is_symlink() or any(parent.is_symlink() for parent in path.parents):
            raise ValueError("Whitelist source must not be a symlink")
        data = path.read_bytes()
        records.append({"path": rel.as_posix(), "sha256": hashlib.sha256(data).hexdigest()})
        for variant in ("baseline", "candidate"):
            dest = work / "java" / variant / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
    (evidence / "java-source-manifest.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n"
    )

    candidate = work / "java/candidate"
    for rel in ("pom.xml", "yudao-dependencies/pom.xml"):
        path = candidate / rel
        text = path.read_text()
        old = "<mapstruct.version>1.7.0.Beta2</mapstruct.version>"
        if text.count(old) != 1:
            raise ValueError("Unexpected MapStruct source declaration")
        path.write_text(text.replace(old, "<mapstruct.version>1.6.3</mapstruct.version>"))
    bom = candidate / "yudao-dependencies/pom.xml"
    text = bom.read_text()
    marker = "<dependencyManagement>\n        <dependencies>"
    if text.count(marker) != 1:
        raise ValueError("Unexpected dependencyManagement")
    text = text.replace(
        marker,
        marker + """
            <dependency>
                <groupId>com.mysql</groupId>
                <artifactId>mysql-connector-j</artifactId>
                <version>8.2.0</version>
            </dependency>""",
    )
    bom.write_text(text)
    settings = work / "maven-settings.xml"
    settings.write_text("""<settings xmlns="http://maven.apache.org/SETTINGS/1.2.0">
  <mirrors><mirror><id>av1-central</id><mirrorOf>*</mirrorOf>
    <url>https://repo.maven.apache.org/maven2</url>
  </mirror></mirrors>
</settings>
""")
    global_settings = work / "maven-global-settings.xml"
    global_settings.write_text('<settings xmlns="http://maven.apache.org/SETTINGS/1.2.0"/>')
    home = work / "maven-user"
    home.mkdir(exist_ok=True)
    temporary = work / "tmp"
    temporary.mkdir(exist_ok=True)
    env = {
        "PATH": str(Path(tools["java"]).parent) + ":/usr/bin:/bin:/usr/sbin:/sbin",
        "JAVA_HOME": tools["javaHome"],
        "LANG": "en_US.UTF-8",
        "MAVEN_SKIP_RC": "true",
        "MAVEN_OPTS": "-Duser.home=" + str(home) + " -Djava.io.tmpdir=" + str(temporary),
        "TMPDIR": str(temporary),
    }
    command = [
        tools["maven"], "-B", "-ntp", "-s", str(settings), "-gs", str(global_settings),
        "-Dmaven.repo.local=" + str(work / "maven-repository"),
        "-Duser.home=" + str(home), "-DskipTests",
    ]
    results = []
    if compile_only:
        results = [result for result in json.loads((evidence / "java-results.json").read_text())
                   if result["step"] != "compile"]
    for variant in ("baseline", "candidate"):
        folder = work / "java" / variant
        if compile_only:
            for target in folder.rglob("target"):
                if target.is_dir() and not target.is_symlink():
                    shutil.rmtree(target)
        steps = [
            ("effective-pom", ["org.apache.maven.plugins:maven-help-plugin:3.5.1:effective-pom",
                               "-Doutput=" + str(evidence / (variant + "-effective-pom.xml"))]),
            ("dependency-tree", ["org.apache.maven.plugins:maven-dependency-plugin:3.8.1:tree",
                                 "-Dverbose"]),
            ("compile", ["compile"]),
        ]
        if compile_only:
            steps = [step for step in steps if step[0] == "compile"]
        for name, args in steps:
            log = evidence / (variant + "-" + name + ".log")
            started = time.monotonic()
            policy = (
                "(version 1)(allow default)(deny file-write*)"
                "(allow file-write* (subpath " + json.dumps(str(work)) + ') (literal "/dev/null"))'
                "(deny file-read* (subpath " + json.dumps(str(Path.home())) + "))"
            )
            step_command = command + args
            if name == "compile":
                policy += "(deny network*)"
                step_command = command + ["-o"] + args
            step_command = ["/usr/bin/sandbox-exec", "-p", policy] + step_command
            with log.open("w") as output:
                try:
                    run = subprocess.run(step_command, cwd=folder, env=env,
                                         stdout=output, stderr=subprocess.STDOUT, timeout=900)
                    code = run.returncode
                except subprocess.TimeoutExpired:
                    code = 124
            item = {
                "variant": variant, "step": name, "exit": code,
                "seconds": round(time.monotonic() - started, 1),
                "log": log.name,
                "writesRestrictedToVerificationDirectory": True,
                "userHomeReadDenied": True,
                "offlineNetworkDenied": name == "compile",
            }
            results.append(item)
            (evidence / "java-results.json").write_text(json.dumps(results, indent=2) + "\n")
            print(json.dumps(item), flush=True)
        generated = []
        for path in folder.rglob("target/generated-sources/annotations/**/*.java"):
            data = path.read_bytes()
            generated.append({
                "path": path.relative_to(folder).as_posix(),
                "sha256": hashlib.sha256(data).hexdigest(),
            })
        (evidence / (variant + "-generated-mappers.json")).write_text(
            json.dumps(generated, indent=2) + "\n"
        )
    print("AV1 Java finished; no application was started.", flush=True)
    return 1 if any(result["exit"] for result in results) else 0


if __name__ == "__main__":
    sys.exit(main())
