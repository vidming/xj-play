// 离线验证文档浏览器行为；不启动或测试平台业务。
const {chromium} = require('playwright');
const fs = require('node:fs');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const base = path.resolve(__dirname, '..');
let browser;
(async () => {
  browser = await chromium.launch({headless: true, channel: 'chrome'});
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  const file = path.join(base, '图表/物理模型审阅页.html');
  await page.goto(pathToFileURL(file).href);
  const model = JSON.parse(fs.readFileSync(path.join(base, '资料/物理数据模型-V0.1.json')));
  assert.equal(await page.locator('main section').count(), model.tables.length);
  assert.equal(await page.locator('tbody tr').count(), model.tables.reduce((n,t)=>n+t.columns.length,0));
  for (const store of model.stores) {
    assert.equal(await page.locator(`section[data-store="${store.id}"]`).count(),
      model.tables.filter(table => table.store === store.id).length);
  }
  assert.equal(model.stores.length, 1);
  assert.equal(model.stores[0].database, 'xj_play');
  assert.equal(model.physicalForeignKeys.length, 0);
  assert.equal(model.logicalRelations.length, model.tables.reduce((n,t)=>n+t.columns.filter(c=>c.references).length,0));
  assert.ok((await page.locator('body').textContent()).includes('物理外键0条'));
  assert.equal(await page.locator('aside[aria-label="数据归属说明"]').count(), 1);
  const viewports = [];
  for (const width of [320, 736, 1440]) {
    await page.setViewportSize({width, height:900});
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth <= innerWidth), '宽度'+width+'发生水平溢出');
    viewports.push(width);
  }
  await page.locator('input').fill('xj_cash_fact · 可信实收事实');
  assert.equal(await page.locator('section:not([hidden])').count(), 1);
  await page.locator('nav a[href="#xj_subject"]').click();
  assert.equal(await page.locator('input').inputValue(), '');
  assert.equal(await page.locator('section:not([hidden])').count(), model.tables.length);
  const svgFile = path.join(base, '图表/完整物理ER-V0.1.svg');
  await page.goto(pathToFileURL(svgFile).href);
  assert.equal(await page.locator('g.node').count(), model.tables.length);
  const glyph = await page.evaluate(() => {
    let overlaps=0;
    for(const node of document.querySelectorAll('g.node')){
      const rows = new Map();
      for(const text of node.querySelectorAll('text')){
        const box=text.getBBox(), key=Math.round(box.y);
        if(!rows.has(key))rows.set(key,[]);
        rows.get(key).push({x:box.x,right:box.x+box.width});
      }
      for(const row of rows.values()){
        row.sort((a,b)=>a.x-b.x);
        for(let i=1;i<row.length;i++)if(row[i].x<row[i-1].right-1)overlaps++;
      }
    }
    return {sameRowTextOverlaps:overlaps};
  });
  assert.equal(glyph.sameRowTextOverlaps,0, 'SVG表内文本重叠');
  assert.equal(errors.length,0);
  const sha = f => crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
  console.log(JSON.stringify({
    date:new Intl.DateTimeFormat('en-CA', {timeZone:'Asia/Shanghai'}).format(new Date()),status:'文档浏览器检查通过',htmlSha256:sha(file),svgSha256:sha(svgFile),
    checks:{tables:model.tables.length,columns:model.tables.reduce((n,t)=>n+t.columns.length,0),
      stores:model.stores.map(s=>({id:s.id,tables:model.tables.filter(t=>t.store===s.id).length})),
      logicalRelations:model.logicalRelations.length,physicalForeignKeys:model.physicalForeignKeys.length,
      viewports,filter:'字段/表名过滤与引用导航通过',...glyph,pageErrors:errors},
    limitations:'离线文档检查；SVG为大画幅，未完成全图人工视觉审阅；未测试真实平台/交易/存储'
  },null,2));
  await browser.close();
})().catch(async error=>{console.error(error);if(browser)await browser.close();process.exitCode=1;});
