"""从当前工作包生成离线相对甘特；未估时依赖保持阻塞，不伪造日历排期。"""
import hashlib
import html
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
source = BASE / "工作包清单.json"
plan = json.loads(source.read_text())
tasks = plan["packages"]
assert len({t["id"] for t in tasks}) == len(tasks)
known = set()
blocked = set()
scheduled = []
pending = []
cursor = 0
for task in tasks:
    assert set(task["dependsOn"]) <= known, task["id"]
    assert set(task.get("acceptanceDependsOn", [])) <= {t["id"] for t in tasks}
    effort = task["effortDays"]
    if effort:
        assert 0 < effort[0] <= effort[1]
    if effort is None or any(dep in blocked for dep in task["dependsOn"]):
        blocked.add(task["id"])
        pending.append(task)
    else:
        scheduled.append((task, cursor))
        cursor += effort[1]
    known.add(task["id"])

low = sum(t["effortDays"][0] for t in tasks if t["effortDays"])
high = sum(t["effortDays"][1] for t in tasks if t["effortDays"])
rows = []
for task, start in scheduled:
    a, b = task["effortDays"]
    rows.append(
        f'<tr><th scope="row">{html.escape(task["id"] + " " + task["title"])}</th>'
        f'<td>{a}–{b}人日</td><td>{html.escape("、".join(task["dependsOn"]) or "无")}</td>'
        f'<td><div class="track" aria-label="T{start}起，估计{a}至{b}人日">'
        f'<span class="range" style="left:{start / cursor * 100:.4f}%;width:{b / cursor * 100:.4f}%"></span>'
        f'<span class="core" style="left:{start / cursor * 100:.4f}%;width:{a / cursor * 100:.4f}%"></span>'
        f'</div><span class="time">T{start} → T{start + b}（上界参考）</span></td></tr>'
    )
pending_rows = []
for task in pending:
    effort = task["effortDays"]
    value = f'{effort[0]}–{effort[1]}人日，起点待定' if effort else "尚不可估"
    reason = task.get("estimateBlocker", "前置完整游戏工作量未定，不能排定起点")
    pending_rows.append(
        f'<tr><th scope="row">{html.escape(task["id"] + " " + task["title"])}</th>'
        f'<td>{value}</td><td>{html.escape("、".join(task["dependsOn"]))}</td>'
        f'<td>{html.escape(reason)}</td></tr>'
    )
digest = hashlib.sha256(source.read_bytes()).hexdigest()
document = """<!doctype html>
<html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>实施依赖与相对甘特</title>
<style>
:root { color-scheme:light dark; --paper:light-dark(#faf9f5,#191c1b); --ink:light-dark(#25312d,#e2e8e3);
--line:light-dark(#ccd3ce,#45534c); --mark:light-dark(#36644c,#86b497); --soft:light-dark(#dce6de,#34483b); }
*{box-sizing:border-box} body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.65 Georgia,"Songti SC",serif}
main{max-width:1160px;margin:auto;padding:28px 20px}h1{font-size:28px;font-weight:500}a{color:inherit}p{max-width:90ch}
table{border-collapse:collapse;width:100%;margin:20px 0}th,td{padding:12px 8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th:first-child{width:29%;font-weight:500}td:nth-child(2){width:15%}td:nth-child(3){width:15%}
.track{height:20px;position:relative;background:repeating-linear-gradient(to right,transparent 0,transparent calc(10% - 1px),var(--line) 10%)}
.range,.core{position:absolute;top:3px;height:14px;background:var(--soft)}.core{background:var(--mark)}.time{font:13px/1.5 monospace}
.tag{padding:3px 8px;background:var(--soft)}code{overflow-wrap:anywhere}caption{text-align:left;font-weight:500}
@media(max-width:650px){main{padding:18px 12px}thead{display:none}table,tbody,tr,th,td{display:block;width:100%!important}
tr{padding:12px 0;border-bottom:1px solid var(--line)}th,td{border:0;padding:3px 0}.track{margin-top:10px}}
</style><main>
<h1>实施依赖与相对甘特</h1>
<p class="tag">阶段4提交稿 · 全部未开始 · 只供计划审阅</p>
<p>单执行者按依赖拓扑串行的参考；T0不是开工日期。深色为工作量下界，浅色延伸至上界。
未确定团队、预算与外部等待，不把人日换算为承诺工期；有多个真实执行者时可重新排并行。</p>
<p>已估平台工作包合计 <strong>__LOW__–__HIGH__ 人日</strong>，不含完整G-A/G-B、V0.2/V0.3未知项和采购/商户审核等待。
W11虽有自身工作量估计，但前置游戏未知，因此不在时间轴上排定起点。</p>
<table><caption>平台集成之前的相对轴（T0至T__END__，按各包上界串行）</caption>
<thead><tr><th>工作包</th><th>工作量</th><th>开始依赖</th><th>相对轴</th></tr></thead><tbody>__ROWS__</tbody></table>
<table><caption>保留依赖、尚不能排定日历的工作包</caption>
<thead><tr><th>工作包</th><th>工作量</th><th>依赖</th><th>缺口</th></tr></thead><tbody>__PENDING__</tbody></table>
<p><a href="../01-文档/实施计划与里程碑.md">实施计划</a> · <a href="工作包清单.json">可编辑工作包数据</a></p>
<p>数据源SHA-256：<code>__HASH__</code>。页面由同目录生成脚本生成，不依赖网络，不承担确认或发布操作。</p>
</main></html>
"""
for token, value in {
    "__LOW__": str(low), "__HIGH__": str(high), "__END__": str(cursor),
    "__ROWS__": "".join(rows), "__PENDING__": "".join(pending_rows), "__HASH__": digest,
}.items():
    document = document.replace(token, value)
(BASE / "实施依赖与相对甘特.html").write_text(document)
print(json.dumps({"packages": len(tasks), "estimatedEffortDays": [low, high],
                  "scheduled": len(scheduled), "undated": len(pending),
                  "sourceSha256": digest}, ensure_ascii=False))
