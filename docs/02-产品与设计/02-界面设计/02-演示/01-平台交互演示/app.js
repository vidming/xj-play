(() => {
  const X = window.XJ;
  const app=document.getElementById('app'), pageSelect=document.getElementById('demo-page'), modeSelect=document.getElementById('demo-state'), actor=document.getElementById('demo-actor'), notice=document.getElementById('notice');
  let lastHash=null;
  pageSelect.innerHTML=X.routes.map(r=>`<option value="${r.id}">${r.label}</option>`).join('');
  X.tell = text => { notice.textContent=text; };
  X.go = (route, mode='normal', query=null) => {
    const known=X.routes.some(r=>r.id===route);
    const params=new URLSearchParams();
    if(mode!=='normal') params.set('state',mode);
    const effectiveQuery=query===null && route==='store'?X.S.query:query;
    if(effectiveQuery!==null && effectiveQuery!=='') params.set('q',effectiveQuery);
    if(X.S.filter!=='all' && route==='store') params.set('filter',X.S.filter);
    if(X.S.game==='gb') params.set('game','gb');
    const target=`#/${known?route:'store'}${params.size?'?'+params:''}`;
    if(location.hash!==target) location.hash=target;
    readRoute(true);
  };
  function readRoute(force=false) {
    if(!force && lastHash===location.hash)return;
    lastHash=location.hash;
    const raw=location.hash.replace(/^#\/?/,'');
    const [name,search='']=raw.split('?');
    const params=new URLSearchParams(search);
    const route=X.routes.find(r=>r.id===(name||'store'));
    X.route=route?route.id:'store'; X.mode=route && route.states[params.get('state')] ? params.get('state') : route?'normal':'missing';
    if(X.route==='store') {
      X.S.query=params.get('q')||'';
      X.S.filter=['story','clue'].includes(params.get('filter'))?params.get('filter'):'all';
    }
    X.S.game=params.get('game')==='gb'?'gb':'ga';
    if(X.mode==='expired') {X.S.auth=false;X.S.verified=false;}
    render();
    document.getElementById('main')?.focus({preventScroll:true});
    window.scrollTo(0,0);
  }
  function generic() {
    const m=X.mode,r=X.route;
    if(m==='loading' && r!=='run') return `<main id="main" class="container" tabindex="-1"><h1>正在读取资料</h1><p role="status">保留当前条件，等待真实结果；这里是设计加载状态。</p><div class="loading-line"></div><div class="loading-line"></div>${X.btn('模拟重试读取','retry')}</main>`;
    const data=m==='denied'?['没有这项操作权限','不展示不属于当前身份的私人资料或草稿。可重新核对身份、角色和范围。']:m==='expired'?['身份已失效，请重新识别','原账号私人资料不继续展示；支持的本机来源保留，重登后核对归属。']:m==='error'&&!['verify','recover'].includes(r)?['暂时没能读取资料','已保留条件或草稿。可以重试、返回或联系支持。']:m==='maintenance'?['商店维护中','这里是维护状态设计，没有实际服务事故；保留查单与支持入口。']:m==='missing'?['这个页面暂时找不到','可能已变更或不可用，返回发现页查看当前作品。']:null;
    return data?`<main id="main" class="container narrow" tabindex="-1"><div class="empty"><h1>${data[0]}</h1><p>${data[1]}</p><div class="actions">${X.btn(m==='expired'?'重新识别演示身份':'重试 / 核对','retry','primary')}${X.link('返回商店','store','secondary')}${X.link('联系支持','support')}</div></div></main>`:null;
  }
  function render() {
    const route=X.routes.find(r=>r.id===X.route);
    document.title=`${route.label} · 间隙PLAY原稿比例修订版Demo`;
    pageSelect.value=X.route;
    modeSelect.innerHTML=Object.entries(route.states).map(([v,t])=>`<option value="${v}">${t}</option>`).join('');
    modeSelect.value=X.mode;
    actor.value=X.S.deletion?'deleting':X.S.auth?(X.S.verified?'verified':'unverified'):'guest';
    let html=X.route.startsWith('ops/')?X.admin():X.front();
    const fallback=generic();
    if(fallback) html=html.replace(/<main\b[\s\S]*?<\/main>/,fallback);
    const personal=['account','deletion','saves','import','order','support'];
    if(!fallback && personal.includes(X.route) && !X.S.auth && !(X.route==='deletion' && ['cleanup','overdue','done'].includes(X.mode))) {
      html=html.replace(/<main\b[\s\S]*?<\/main>/,X.page('先识别本人身份',`${X.status('登录后返回原操作','游客试玩仍然开放；当前不展示私人明细。','neutral')}${X.btn('模拟登录并返回','login-return','primary')}${X.link('返回商店','store','secondary')}`,true));
    }
    if(!fallback && X.S.auth && !X.S.verified && ['saves','import','order','support'].includes(X.route)) {
      html=html.replace(/<main\b[\s\S]*?<\/main>/,X.page('先验证邮箱再继续',`${X.status('私人资料需要验证','保留当前操作意图；游客试玩仍可继续。','neutral')}${X.link('前往模拟验证','verify','primary')}`,true));
    }
    if(!fallback && X.S.deletion && ['checkout','import','saves'].includes(X.route)) {
      html=html.replace(/<main\b[\s\S]*?<\/main>/,X.page('注销申请处理中',`${X.status('当前暂停新增资产与云档写入','查单、售后、注销进度和最终确认前撤回仍然可用。')}${X.link('查看进度 / 撤回','deletion','primary','requested')}${X.link('查单与支持','support','secondary')}`,true));
    }
    app.innerHTML=html;
    notice.setAttribute('role','status');
    notice.textContent='';
    for(const e of app.querySelectorAll('[data-go]')) if(e.dataset.go===X.route) e.setAttribute('aria-current','page');
  }
  function continueIntent() {
    if(X.S.intent==='library') return X.go('library');
    if(X.S.intent==='return') return X.go(X.S.returnTo||'account',X.S.returnMode||'normal');
    if(!X.S.verified) return X.go('verify');
    if(X.S.intent==='checkout' || X.S.intent==='free') return X.go(X.S.trial&&!X.S.imported?'import':'checkout',X.S.trial&&!X.S.imported?'normal':X.S.checkoutMode||'normal');
    X.go('detail');
  }
  function purchase() {
    if(X.S.deletion) return X.go('account','deleting');
    if(X.S.grants[X.S.game] && X.mode!=='free') return enter();
    X.S.intent=X.mode==='free'?'free':'checkout';
    X.S.checkoutMode=X.mode==='free'?'free':X.S.game==='gb'?'credit':'normal';
    if(!X.S.auth) return X.go('login');
    if(!X.S.verified) return X.go('verify');
    continueIntent();
  }
  function enter() {
    if(X.S.deletion) return X.go('account','deleting');
    if(!X.S.auth) {X.S.intent='return';X.S.returnTo='detail';return X.go('login');}
    if(!X.S.grants[X.S.game] && !X.S.freeGrants[X.S.game] && X.mode!=='owned') return X.go('run','denied');
    X.go('run');
  }
  const actions={
    home:()=>X.go('store'),
    trial:()=>{X.S.trial=true;X.go('run');},
    purchase, enter,
    boundary:()=>X.go('run','boundary'), 'resume-trial':()=>X.go('run'),
    mute:()=>{X.S.mute=!X.S.mute;render();}, expand:()=>{X.S.large=!X.S.large;render();},
    'retry-run':()=>{X.go('run');X.tell('仅模拟重新核对；没有真实游戏就绪证据。');},
    retry:()=>X.mode==='expired'?X.go('login'):X.go(X.route),
    filter:button=>{X.S.filter=button.dataset.value;X.go('store','normal',X.S.query);},
    'clear-search':()=>{X.S.query='';X.S.filter='all';X.go('store','normal','');},
    share:async()=>{const url=location.href;try{await navigator.clipboard.writeText(url);X.tell('已复制当前设计预览链接，包含筛选；没有向外发送消息。');}catch(_){X.tell(`可复制当前设计链接：${url}`);}},
    verify:()=>{X.S.auth=true;X.S.verified=true;continueIntent();},
    resend:()=>X.go('verify','sent'),
    'reset-password':()=>{X.S.auth=false;X.S.verified=false;X.go('reset','done');},
    'skip-import':()=>X.go('checkout',X.S.checkoutMode||'normal'),
    'import-local':()=>{if(!X.S.verified)return X.go('verify');X.S.imported=true;X.go('checkout',X.S.checkoutMode||'normal');X.tell('模拟已选择本机来源并保留替换前来源；没有上传真实云档。');},
    'import-cloud':()=>{X.S.imported=true;X.go('checkout',X.S.checkoutMode||'normal');},
    'check-import':()=>{X.go('import');X.tell('模拟查证完成；选择来源后再确认，不冒充真实导入。');},
    'refresh-quote':()=>{const mode=X.mode==='source'?'credit':'normal';X.go('checkout',mode);X.tell('模拟重新展示报价，仍需明确勾选确认；没有真实查价或扣款。');},
    'query-order':()=>{if(['paid','delivery','late'].includes(X.mode)){X.S.grants[X.S.game]=true;X.go('order','delivered');}else if(['normal','unknown','waiting'].includes(X.mode)){X.go('order','paid');}else{X.tell('保留已核实的关闭、失败或退款事实；其他结果需独立查证，不回写成付款成功。');}},
    'check-save':()=>{X.go('saves');X.tell('仅模拟核查保存状态，没有真实云存储或恢复结果。');},
    'login-library':()=>{X.S.intent='library';X.go('login');},
    'login-return':()=>{X.S.intent='return';X.S.returnTo=X.route;X.S.returnMode=X.mode;X.go('login');},
    logout:()=>{X.S.auth=false;X.S.verified=false;X.S.grants={};X.S.freeGrants={};X.S.orders={};X.go('store');},
    'change-email':()=>{X.S.auth=false;X.S.verified=false;X.go('account','changed');},
    'identify-delete':()=>X.go('deletion','impact'),
    'withdraw-delete':()=>{X.S.deletion=false;X.go('account');X.tell('模拟申请已撤回，后续操作仍需重新核对条件。');},
    'asset-spec':()=>X.tell('设计规格：封面3:2，建议1536×1024；截图保持原比例、0–8张；可访问替代文本，失败不伪造实机。编码/文件限制待架构核准。'),
    'ops-check':()=>X.tell('模拟核对：可信付款记录占位。当前没有调用真实支付或订单服务。'),
    'ops-delivery':()=>X.tell('模拟登记处理核查，保留当前现金事实；未修改真实权益。'),
    'review-cleanup':()=>X.tell('模拟记录责任角色和待复核项；未处理真实数据，不声称分类清理已完成。'),
    sample:()=>X.tell('组件反馈样例。'), none:()=>{}
  };
  app.addEventListener('click',event=>{
    const el=event.target.closest('[data-go],[data-action]');
    if(!el || el.disabled)return;
    if(el.dataset.game)X.S.game=el.dataset.game;
    if(el.dataset.go){event.preventDefault();X.go(el.dataset.go,el.dataset.mode||'normal');return;}
    actions[el.dataset.action]?.(el);
  });
  const length=value=>[...String(value).trim()].length;
  const valid=(value,min,max,label)=>{const n=length(value);if(n<min||n>max)throw Error(`${label}须为${min}–${max}个字符，当前${n}；已保留输入。`);};
  app.addEventListener('submit',event=>{
    event.preventDefault();
    const form=event.target;
    if(!form.reportValidity())return;
    const value=id=>form.querySelector(`#${id}`)?.value||'';
    try {
      switch(form.id){
        case 'search-form':valid(value('query'),0,80,'搜索关键词');X.S.query=value('query').trim();X.go('store','normal',X.S.query);break;
        case 'identity-form':if(form.querySelector('#nickname')){valid(value('nickname'),1,24,'昵称');X.S.nickname=value('nickname').trim();}X.S.auth=true;X.S.verified=false;if(X.S.intent==='library'){X.go('library');}else if(X.S.intent==='return'){continueIntent();}else X.go('verify');break;
        case 'recover-form':X.go('recover','sent');break;
        case 'checkout-form':{
          if(X.S.deletion){X.go('account','deleting');break;}
          if(!X.S.auth){X.S.intent='checkout';X.go('login');break;}
          if(!X.S.verified){X.go('verify');break;}
          if(X.S.grants[X.S.game] || X.S.freeGrants[X.S.game]){X.go('library');X.tell('已存在本作品覆盖来源，返回已有权益；不重复下单或授予。');break;}
          const m=X.mode,free=m==='free'||X.S.intent==='free',credit=['credit','zero'].includes(m);
          const due=free||m==='zero'?0:credit?1800:2800;
          X.S.orders[X.S.game]={due,credit:credit?(m==='zero'?2800:1000):0,kind:free?'free':m==='zero'?'zero':'paid'};
          if(free){X.S.freeGrants[X.S.game]=true;X.go('order','free');}else if(m==='zero'){X.S.grants[X.S.game]=true;X.go('order','zero');}else X.go('order','unknown');
          break;
        }
        case 'save-confirm-form':X.go('saves');X.tell('仅完成模拟确认；未读取、重开或恢复真实游戏数据。');break;
        case 'account-form':valid(value('nickname'),1,24,'昵称');X.S.nickname=value('nickname').trim();render();X.tell('演示昵称已更新，仅在当前页面会话内有效。');break;
        case 'delete-confirm-form':if(X.mode==='final'){X.S.auth=false;X.S.verified=false;X.S.deletion=false;X.S.grants={};X.S.freeGrants={};X.S.orders={};X.go('deletion','cleanup');}else{X.S.deletion=true;X.go('deletion','requested');}break;
        case 'support-form':valid(value('support-text'),1,1000,'必要说明');X.go('support','submitted');break;
        case 'game-form':valid(value('game-title'),1,80,'作品名');valid(value('game-summary'),1,160,'摘要');valid(value('game-body'),1,2000,'详情');valid(value('game-device'),1,160,'设备声明');valid(value('game-language'),1,160,'语言声明');X.tell('模拟草稿已检查并保留在当前表单，没有写入后台。');break;
        case 'version-form':valid(value('version-notes'),1,1000,'更新说明');X.tell('模拟版本说明已检查，真实接入验证仍未执行。');break;
        case 'product-form':{
          const price=Number(value('product-price'));if(!Number.isInteger(price)||price<0||price>999999)throw Error('金额须为0–999999的整数分。');
          const scopes=value('product-scopes').split(',').map(x=>x.trim());if(!scopes.length||scopes.length>1000||scopes.some(x=>!/^[\x21-\x7e]{1,128}$/.test(x))||new Set(scopes).size!==scopes.length)throw Error('内容映射须为1–1000个不重复ASCII标识，每个1–128字符；请修正后再保存。');
          valid(value('product-name'),1,80,'商品名');valid(value('product-promise'),1,2000,'商品承诺');X.tell('模拟商品已检查，无真实商品写入；历史已售承诺不得被修改覆盖。');break;
        }
        case 'publish-form':if(['normal','blocked'].includes(X.mode)){X.go('ops/publish','blocked');X.tell('接入等发布前置尚未有实证，当前阻止发布；可用状态选择器查看发布记录设计。');}else{X.tell('仅登记当前影响确认，不发布、暂停、回退或恢复真实作品。');}break;
        case 'ops-filter':X.go('ops/orders',value('order-filter')==='DEMO-0101'?'normal':'empty');break;
        case 'ops-support-form':valid(value('support-conclusion'),1,1000,'核实结论');if(Number(value('refund-amount'))>(X.mode==='upgrade'?1800:2800))throw Error('退款不得超过本次核实可退金额；升级仅退新增实付。');X.tell('模拟方案已检查，现金结果与撤权仍分别核实；未发起退款。');break;
        case 'report-filter':{
          const days=(Date.parse(value('date-end'))-Date.parse(value('date-start')))/86400000;
          if(!Number.isInteger(days)||days<1||days>366)throw Error('查询区间须为1–366日，止日不包含在内；请保留条件后修正。');
          X.tell(`已选择${value('date-start')}至${value('date-end')}（不含），Asia/Shanghai；下方仍是固定模拟样例，不返回真实查询。`);break;
        }
      }
    }catch(error){notice.setAttribute('role','alert');X.tell(error.message);}
  });
  pageSelect.addEventListener('change',()=>X.go(pageSelect.value));
  modeSelect.addEventListener('change',()=>X.go(X.route,modeSelect.value));
  actor.addEventListener('change',()=>{X.S.auth=actor.value!=='guest';X.S.verified=['verified','deleting'].includes(actor.value);X.S.deletion=actor.value==='deleting';if(!X.S.auth){X.S.grants={};X.S.freeGrants={};X.S.orders={};}render();});
  document.getElementById('demo-reset').addEventListener('click',()=>{X.S=X.initial();X.go('store');});
  window.addEventListener('hashchange',()=>readRoute());
  readRoute();
})();
