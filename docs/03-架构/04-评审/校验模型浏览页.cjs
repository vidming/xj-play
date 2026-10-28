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
  const file = path.join(base, '02-图表/物理模型审阅页.html');
  await page.goto(pathToFileURL(file).href);
  const model = JSON.parse(fs.readFileSync(path.join(base, '05-资料/物理数据模型-V0.1.json')));
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
  const svgFile = path.join(base, '02-图表/完整物理ER-V0.1.svg');
  await page.goto(pathToFileURL(svgFile).href);
  assert.equal(await page.locator('g.node').count(), model.tables.length);
  const glyph = await page.evaluate(model => {
    let overlaps=0;
    const modelMismatches=[];
    const nodes = [...document.querySelectorAll('g.node')].map(node => {
      const box=node.getBBox();
      // BBox is local to the graph; canvas comparison uses the graph's translation.
      const graphMatrix=node.ownerSVGElement.querySelector('g.graph').transform.baseVal.consolidate().matrix;
      const canvasBox={x:box.x+graphMatrix.e,y:box.y+graphMatrix.f,width:box.width,height:box.height};
      const glyphs=[...node.querySelectorAll('text')];
      const texts=glyphs.map(text=>{
        const b=text.getBBox();
        return {x:b.x,y:b.y,right:b.x+b.width,bottom:b.y+b.height};
      });
      const table=model.tables.find(item=>item.name===node.querySelector('title')?.textContent);
      if(!table)modelMismatches.push({node:node.querySelector('title')?.textContent,reason:'模型中不存在'});
      else {
        const expected=[`${table.name} · ${table.label}`,...table.columns.flatMap(column=>{
          const roles=[...(column.key||[])];
          if(table.unique.some(key=>key.length===1&&key[0]===column.name)&&!roles.includes('uk'))roles.push('uk');
          return [column.name,column.sqlType,roles.join(',')+' '+(column.nullable?'NULL':'NOT NULL'),column.description];
        }),`UNIQUE ${table.unique.map(key=>'('+key.join(',')+')').join('; ')}`];
        const actual=glyphs.map(text=>text.textContent);
        if(JSON.stringify(actual)!==JSON.stringify(expected))modelMismatches.push({node:table.name,reason:'字段、约束或文字与模型不一致'});
      }
      return {title:node.querySelector('title')?.textContent,box,canvasBox,texts};
    });
    const nodeNames=nodes.map(node=>node.title);
    const expectedNames=model.tables.map(table=>table.name);
    if(nodeNames.length!==expectedNames.length || new Set(nodeNames).size!==nodeNames.length ||
       expectedNames.some(name=>!nodeNames.includes(name))){
      modelMismatches.push({reason:'表节点存在缺失或重复'});
    }
    const textOverflows=nodes.flatMap(({title,box,texts})=>texts.filter(text=>
      text.x < box.x-1 || text.right > box.x+box.width+1 ||
      text.y < box.y-1 || text.bottom > box.y+box.height+1
    ).map(()=>title));
    const nodeOverlaps=[];
    for(let i=0;i<nodes.length;i++)for(let j=i+1;j<nodes.length;j++){
      const a=nodes[i].box,b=nodes[j].box;
      if(Math.min(a.x+a.width,b.x+b.width)-Math.max(a.x,b.x)>1 &&
         Math.min(a.y+a.height,b.y+b.height)-Math.max(a.y,b.y)>1){
        nodeOverlaps.push([nodes[i].title,nodes[j].title]);
      }
    }
    const root=document.documentElement;
    const {x,y,width,height}=root.viewBox.baseVal;
    const canvas={x,y,width,height};
    const nodesOutsideCanvas=nodes.filter(({canvasBox:box})=>box.x < x-1 || box.y < y-1 ||
      box.x+box.width > x+width+1 || box.y+box.height > y+height+1
    ).map(({title})=>title);
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
    return {sameRowTextOverlaps:overlaps,textOverflows,nodeOverlaps,nodesOutsideCanvas,canvas,modelMismatches};
  },model);
  assert.equal(glyph.sameRowTextOverlaps,0, 'SVG表内文本重叠');
  assert.deepEqual(glyph.modelMismatches,[], 'SVG表文字与物理模型不一致');
  assert.deepEqual(glyph.textOverflows,[], 'SVG字段文字越出表节点');
  assert.deepEqual(glyph.nodeOverlaps,[], 'SVG表节点互相覆盖');
  assert.deepEqual(glyph.nodesOutsideCanvas,[], 'SVG表节点越出有效绘图边界');
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
