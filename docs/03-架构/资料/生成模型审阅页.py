"""输出当前Mermaid ER源与离线字段/引用浏览页，不将导出等同视觉验收。"""
import html
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
model = json.loads((BASE / "资料/物理数据模型-V0.1.json").read_text())
tables = model["tables"]
stores = {s["id"]: s["label"] for s in model["stores"]}
mermaid = ["erDiagram"]
relations = []
sections = []
for table in tables:
    name = table["name"]
    mermaid.append(f"    {name} {{")
    rows = []
    for c in table["columns"]:
        # Mermaid's type token cannot contain spaces; the full physical type stays in comment.
        type_token = c["sqlType"].split("(")[0].split()[0]
        roles = [k.upper() for k in c.get("key", []) if k in ("pk", "uk")]
        key_text = ",".join(roles)
        description = c["sqlType"] + "；" + c["description"]
        if c.get("references"):
            description += "；逻辑关联，无物理外键 " + c["references"]
            target = c["references"].split(".")[0]
            right = "o|" if c["nullable"] else "||"
            left = "|o" if [c["name"]] in table["unique"] else "}o"
            relations.append(f'    {name} {left}..{right} {target} : "{c["name"]}"')
        mermaid.append(f'        {type_token} {c["name"]} {key_text} "{description.replace(chr(34), chr(39))}"')
        target_html = "—"
        if c.get("references"):
            target = c["references"].split(".")[0]
            target_html = f'<a href="#{target}">{html.escape(c["references"])}</a>'
        rows.append(
            f'<tr><th scope="row">{html.escape(c["name"])}</th>'
            f'<td>{html.escape(c["sqlType"])}</td><td>{"是" if c["nullable"] else "否"}</td>'
            f'<td>{html.escape(key_text or ("REF" if c.get("references") else "—"))}</td><td>{target_html}</td>'
            f'<td>{html.escape(c["description"])}</td></tr>')
    mermaid.append("    }")
    uniques = "；".join("(" + ",".join(k) + ")" for k in table["unique"])
    sections.append(
        f'<section id="{name}" data-domain="{html.escape(table["domain"])}" data-store="{table["store"]}"><h2>{name} · {html.escape(table["label"])}</h2>'
        f'<p>存储：{stores[table["store"]]}（{table["store"]}）；领域：{table["domain"]}；唯一约束：{html.escape(uniques)}</p>'
        '<table><thead><tr><th>字段</th><th>SQL类型</th><th>可空</th><th>键/关联</th><th>逻辑关联目标</th><th>语义</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table><p>{html.escape(table["rules"])}</p>'
        f'<p>删除：{html.escape(table["deletePolicy"])}</p><a href="#top">回目录</a></section>')
mermaid += relations
mermaid.insert(1, "    %% 全部连线仅表示逻辑关联；不建立物理外键。")
(BASE / "图表/完整物理ER-V0.1.mmd").write_text("\n".join(mermaid) + "\n")
nav = "".join(f'<li><a href="#{t["name"]}">{t["domain"]} · {t["label"]}</a></li>' for t in tables)
document = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>间隙PLAY · 物理模型审阅</title>
<style>
:root{{color-scheme:light dark}}body{{font:15px/1.7 "PingFang SC","Noto Sans CJK SC",sans-serif;margin:0 auto;max-width:1240px;padding:24px;overflow-wrap:anywhere;color:light-dark(#242c29,#e4eee9);background:light-dark(#f7f7f0,#15221d)}}
h1,h2{{font-weight:600}}h1{{font-size:26px}}h2{{font-size:21px;overflow-wrap:anywhere}}a{{color:light-dark(#146a50,#9fe5c9)}}nav ul{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:4px 20px;padding-left:20px}}
section{{margin:36px 0;scroll-margin-top:20px}}table{{border-collapse:collapse;width:100%;table-layout:fixed}}th,td{{text-align:left;vertical-align:top;padding:10px 7px;border-bottom:1px solid light-dark(#d1dcd5,#3c5146);overflow-wrap:anywhere}}
th:nth-child(1){{width:16%}}th:nth-child(2){{width:15%}}th:nth-child(3){{width:5%}}th:nth-child(4){{width:6%}}th:nth-child(5){{width:18%}}th:nth-child(6){{width:40%}}label{{display:block;margin:18px 0}}input{{font:inherit;max-width:100%;box-sizing:border-box;padding:8px}}[hidden]{{display:none!important}}
@media(max-width:650px){{body{{padding:14px}}table,thead,tbody,tr,th,td{{display:block;width:auto!important}}thead{{display:none}}tr{{margin:18px 0}}td:before{{content:attr(data-label) "：";font-weight:600}}}}
</style></head><body id="top">
<h1>间隙PLAY · 物理模型审阅草案</h1>
<p>{model["date"]} · {len(tables)}张设计表 · {sum(len(t["columns"]) for t in tables)}列 · 未建表；MCP仅做过元数据只读核对。</p>
<p>SD2已确认：所有平台/游戏表设计使用当前MCP数据库xj_play；当前模型全部{len(tables)}表在同一MySQL，具体独立游戏玩法表尚未设计/创建。RK1已明确：全部{len(model["logicalRelations"])}条连线和REF仅表示逻辑关联，物理外键0条；前缀区分归属，不代表独立恢复或访问权限。</p>
<p>字段与引用浏览入口；可编辑关系源为<a href="完整物理ER-V0.1.mmd">Mermaid ER源</a>、<a href="完整物理ER-V0.1.dot">DOT源</a>；<a href="完整物理ER-V0.1.svg">完整字段大画幅SVG</a>已导出，统一规格源为<a href="../资料/物理数据模型-V0.1.json">物理模型JSON</a>。当前保留一份模型及必要源文件，旧排版失败候选已清理；大画幅SVG尚未完成全图人工视觉验收。</p>
<label>查找表名、领域或字段语义 <input type="search" aria-label="查找模型" placeholder="如：退款、cash_fact、存档"></label>
<div role="status" aria-live="polite" id="count">显示全部{len(tables)}张表</div>
<nav aria-label="模型目录"><ul>{nav}</ul></nav>
<aside aria-label="数据归属说明"><h2>数据归属与同库边界</h2><p>平台：xj_；各游戏：登记的xjg_&lt;gameKey&gt;_；底座固定前缀按源码保留。同库事务不跨游戏HTTP自动原子，限制链也随整库恢复。关联存在、归属与删除并发由应用服务事务和守卫检查；不由数据库外键强制。</p></aside>
<main>{"".join(sections)}</main>
<script>
const sections=[...document.querySelectorAll('section')];const search=document.querySelector('input');
const labels=['字段','SQL类型','可空','键/关联','逻辑关联目标','语义'];
document.querySelectorAll('tbody tr').forEach(row=>[...row.children].forEach((cell,i)=>cell.dataset.label=labels[i]));
search.addEventListener('input',()=>{{let count=0;const q=search.value.toLowerCase().trim();sections.forEach(s=>{{s.hidden=q&&!s.textContent.toLowerCase().includes(q);if(!s.hidden)count++;}});document.querySelector('#count').textContent='显示'+count+'张表';}});
document.querySelectorAll('a[href^="#xj_"]').forEach(a=>a.addEventListener('click',()=>{{search.value='';search.dispatchEvent(new Event('input'));}}));
</script></body></html>
"""
(BASE / "图表/物理模型审阅页.html").write_text(document)
print("当前Mermaid ER源及离线字段/引用页已生成；不等同全图人工视觉验收")
