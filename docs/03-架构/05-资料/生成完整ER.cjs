// 使用环境已有Graphviz运行库生成完整字段的海报式ER；不安装依赖。
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { instance } = require('@viz-js/viz');
const base = path.resolve(__dirname, '..');
const model = JSON.parse(fs.readFileSync(path.join(__dirname, '物理数据模型-V0.1.json'), 'utf8'));
const esc = s => String(s).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
const textWidth = s => [...String(s)].reduce((n, c) => n + (c.charCodeAt(0) > 127 ? 16 : 10), 28);
const lines = [
  'digraph XJ {',
  `graph [rankdir=LR, bgcolor="#fafbf7", nodesep=0.5, ranksep=1.2, fontname="Helvetica", label="间隙PLAY · 数据表逻辑关联 · ${model.tables.length}张表 · 物理外键0条 · 设计未实施", labelloc=t];`,
  'node [shape=plain, fontname="Helvetica", fontsize=14];',
  'edge [color="#526d60", arrowsize=0.7, fontname="Helvetica", fontsize=10];'
];
const stores = Object.fromEntries(model.stores.map(s => [s.id, s.label]));
const domains = [...new Set(model.tables.map(t => t.store + '/' + t.domain))];
for (let i = 0; i < domains.length; i++) {
  const [store, domain] = domains[i].split('/');
  lines.push(`subgraph cluster_${i} { label="${stores[store]} / ${domain}"; color="#a8b9ad";`);
  for (const table of model.tables.filter(t => t.store === store && t.domain === domain)) {
    const data = table.columns.map(c => {
      const roles = [...(c.key || [])];
      if (table.unique.some(k => k.length === 1 && k[0] === c.name) && !roles.includes('uk')) roles.push('uk');
      return [c.name, c.sqlType, roles.join(',') + ' ' + (c.nullable ? 'NULL' : 'NOT NULL'), c.description];
    });
    const widths = [0,1,2,3].map(i => Math.max(...data.map(row => textWidth(row[i]))));
    const rows = data.map(row => '<TR>' + row.map((value, i) =>
      `<TD ${i === 0 ? `PORT="${row[0]}"` : ''} WIDTH="${widths[i]}" ALIGN="LEFT">${esc(value)}</TD>`).join('') + '</TR>').join('');
    const title = `<TR><TD COLSPAN="4" BGCOLOR="#dae8df"><B>${table.name} · ${esc(table.label)}</B></TD></TR>`;
    const unique = `<TR><TD COLSPAN="4" ALIGN="LEFT">UNIQUE ${esc(table.unique.map(k => '(' + k.join(',') + ')').join('; '))}</TD></TR>`;
    lines.push(`${table.name} [label=<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="6">${title}${rows}${unique}</TABLE>>];`);
  }
  lines.push('}');
}
for (const table of model.tables) for (const c of table.columns) if (c.references) {
  const [target, column] = c.references.split('.');
  // Crow's foot marks child maximum; optionality follows nullability at the parent end.
  const child = table.unique.some(k => k.length === 1 && k[0] === c.name) ? 'teeodot' : 'crowodot';
  const parent = c.nullable ? 'teeodot' : 'teetee';
  lines.push(`${target}:${column} -> ${table.name}:${c.name} [style=dashed, dir=both, arrowtail="${parent}", arrowhead="${child}", tooltip="${esc('逻辑关联，无物理外键：' + c.references + ' → ' + table.name + '.' + c.name)}"];`);
}
lines.push('}');
const dot = lines.join('\n') + '\n';
fs.writeFileSync(path.join(base, '02-图表/完整物理ER-V0.1.dot'), dot);
(async () => {
  const viz = await instance();
  const result = viz.render(dot, { format: 'svg', engine: 'dot' });
  if (result.status !== 'success') throw new Error(JSON.stringify(result.errors));
  fs.writeFileSync(path.join(base, '02-图表/完整物理ER-V0.1.svg'), result.output);
  const sha = value => crypto.createHash('sha256').update(value).digest('hex');
  const receipt = { date: new Intl.DateTimeFormat('en-CA', {timeZone:'Asia/Shanghai'}).format(new Date()), status: '已渲染', engine: '环境已有@viz-js/viz', graphvizVersion: viz.graphvizVersion,
    tables: model.tables.length, columns: model.tables.reduce((n,t)=>n+t.columns.length,0),
    physicalForeignKeys: model.physicalForeignKeys.length,
    logicalRelations: model.logicalRelations.length,
    stores: model.stores.map(s => ({id:s.id,label:s.label,tables:model.tables.filter(t=>t.store===s.id).length})),
    modelSha256: sha(fs.readFileSync(path.join(__dirname, '物理数据模型-V0.1.json'))),
    dotSha256: sha(dot), svgSha256: sha(result.output),
    warnings: result.errors, scope: '完整字段大画幅SVG；不声称通过Archify或手机视口检查' };
  console.log(JSON.stringify(receipt));
})().catch(e => { console.error(e); process.exitCode=1; });
