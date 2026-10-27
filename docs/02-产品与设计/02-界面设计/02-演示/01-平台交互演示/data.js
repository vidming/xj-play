(() => {
  const common = { loading: '加载中', error: '读取失败', denied: '无权限', expired: '身份失效' };
  const route = (id, label, wf, states, release = 'V0.1') => ({ id, label, wf, release, states: { normal: '默认', ...states } });
  const routes = [
    route('store', '商店 / 搜索', 'WF-01', { empty: '无匹配作品', ...common, missing: '404', maintenance: '维护中' }),
    route('detail', '游戏详情', 'WF-02', { owned: '已拥有', free: '完整免费样例', noTrial: '无试玩', stopped: '普通停售', paused: '安全暂停', device: '设备不兼容', image: '封面缺失', ...common }),
    route('login', '登录 / 注册', 'WF-03/07', { register: '注册', invalid: '身份核验失败', limited: '操作受限', ...common }),
    route('verify', '邮箱验证', 'WF-03/07', { sent: '邮件已发出', limited: '重发受限', used: '链接已用', stale: '链接过期', error: '邮件未发出' }),
    route('recover', '找回密码', 'WF-07', { sent: '统一发送反馈', limited: '发送受限', error: '邮件未发出' }),
    route('reset', '设置新密码', 'WF-07', { stale: '链接过期', used: '链接已用', done: '重置完成' }),
    route('import', '游客进度导入', 'WF-04/05', { conflict: '本机与云档冲突', changed: '另一端已更新', incompatible: '版本不兼容', unknown: '导入结果待查', third: '第三来源暂缓', oversize: '超过1MiB' }),
    route('checkout', '购买 / 升级确认', 'WF-03', { credit: '章节抵扣·V0.2', zero: '零补款·V0.2', scene: '场景商品·V0.3', changed: '报价已变化', stale: '报价已过期', source: '来源退款待查', free: '免费领取', ...common }),
    route('order', '订单与交付结果', 'WF-03', { waiting: '待付款', unknown: '付款待核实', paid: '已收款待交付', delivery: '交付异常', delivered: '权益已交付', cancelled: '未付关闭', late: '关单后晚到账', failed: '明确付款失败', zero: '零补款升级', free: '免费授予', refund: '退款成功撤权异常', ...common }),
    route('library', '我的游戏 / 订单', 'WF-04', { empty: '尚未拥有', recent: '试玩记录', stopped: '停售但可继续', paused: '安全暂停', ...common }),
    route('run', '平台运行外壳', 'WF-05', { boundary: '试玩付费边界', loading: '等待游戏就绪', timeout: '启动结果待查', crash: '运行异常', denied: '范围不允许', device: '设备不兼容', unsupported: '未声明存档', paused: '运行暂停', expired: '身份失效' }),
    route('saves', '进度与恢复', 'WF-04/05', { conflict: '双来源冲突', third: '第三来源暂缓', oversize: '存档超限', incompatible: '版本不兼容', unknown: '保存结果待查', restore: '恢复确认', restart: '重开确认', unsupported: '不支持云档', ...common }),
    route('account', '账号设置', 'WF-07', { email: '变更邮箱', emailFailed: '新邮箱验证失败', changed: '会话已撤销', deleting: '注销申请中', ...common }),
    route('deletion', '注销与分类清理', 'WF-07', { impact: '影响二次确认', requested: '已申请可撤回', blocked: '在途事项待核对', final: '玩家最终确认', cleanup: '分类处理中', overdue: '清理超期', done: '分类处理结果', ...common }),
    route('support', '订单售后与进度', 'WF-03/07', { submitted: '已受理', evidence: '补充必要资料', plan: '人工方案', rejected: '有理由的结论', unknown: '退款待核实', refunded: '已退撤权异常', upgrade: '仅退升级补款·V0.2', overdue: '人工目标超期', ...common }),
    route('help', '帮助 / 规则 / 服务公告', 'WF-07', { privacy: '隐私与分类保留', purchase: '购买退款规则', pause: '暂停与恢复公告', termination: '计划终止公告', ...common }),
    route('components', '设计系统样例', '全局', {}),
    route('ops/games', '后台 / 作品列表', 'WF-06', { empty: '暂无作品', ...common }),
    route('ops/editor', '后台 / 作品资料', 'WF-06', { invalid: '字段缺项', conflict: '并发编辑', ...common }),
    route('ops/versions', '后台 / 版本与接入', 'WF-06', { failed: '接入检查不通过', incompatible: '存档不兼容', ...common }),
    route('ops/products', '后台 / 商品与范围', 'WF-06', { duplicate: '重复映射', promised: '已售承诺保护', test: '测试商品', ...common }),
    route('ops/publish', '后台 / 审核发布', 'WF-06', { blocked: '缺项不可发布', published: '模拟发布记录', stopped: '普通停售', paused: '安全暂停', restore: '恢复前核对', rollback: '回退确认', ...common }),
    route('ops/preview', '后台 / 受控预览', 'WF-06', { denied: '无权预览', test: '测试与正式隔离' }),
    route('ops/orders', '后台 / 订单列表', 'WF-06', { empty: '无匹配订单', ...common }),
    route('ops/order', '后台 / 订单权益查证', 'WF-06/08', { unknown: '付款结果未知', refunded: '退款成功撤权异常', upgrade: '升级原来源保留', ...common }),
    route('ops/support', '后台 / 售后处理', 'WF-06/08', { evidence: '待补资料', upgrade: '仅退升级补款', original: '原单关联升级', unknown: '退款结果未知', overdue: '响应/更新超期', rejected: '拒绝理由', ...common }),
    route('ops/finance', '后台 / 金额核对', 'WF-08', { negative: '跨期退款负净收', known: '费用已核对', empty: '无现金事实', ...common }),
    route('ops/analytics', '后台 / 运营分析', 'WF-06', { empty: '无样本', delayed: '覆盖期缺失', ...common }),
    route('ops/accounts', '后台 / 账号与清理', 'WF-06/07', { overdue: '清理超期', retained: '受限保留', ...common }),
    route('ops/audit', '后台 / 操作与运行记录', 'WF-06', { security: '隔离异常', ...common }),
    route('ops/recovery', '后台 / 服务与恢复状态', 'WF-06', { failed: '恢复核对失败', deletion: '先重放删除/撤权', ...common })
  ];
  const initial = () => ({ auth: false, verified: false, grants: {}, freeGrants: {}, trial: false, imported: false, nickname: '示例玩家', game: 'ga', query: '', filter: 'all', intent: 'detail', mute: true, large: false, deletion: false, note: '', orders: {}, quoteReviewed: false });
  const X = window.XJ = { routes, S: initial(), initial, image: '../../01-资产/01-概念图/telephone-concept.png', route: 'store', mode: 'normal' };
  X.esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  X.money = value => `¥${(value / 100).toFixed(2)}`;
  X.title = () => X.S.game === 'gb' ? '未命名调查游戏' : '第七位来电者';
  X.link = (text, to, kind = '', mode = '', extra = '') => `<a class="${kind ? `button ${kind}` : ''}" href="#/${to}${mode ? `?state=${mode}` : ''}" data-go="${to}" ${mode ? `data-mode="${mode}"` : ''} ${extra}>${text}</a>`;
  X.btn = (text, action, kind = '', extra = '') => `<button type="button" class="button ${kind}" data-action="${action}" ${extra}>${text}</button>`;
  X.status = (title, body, kind = '') => `<div class="status ${kind}" role="status"><strong>${title}</strong><p>${body}</p></div>`;
  X.facts = rows => `<dl class="key-values">${rows.map(([a, b]) => `<div><dt>${a}</dt><dd>${b}</dd></div>`).join('')}</dl>`;
  X.table = (caption, heads, rows) => `<div class="table-wrap" role="region" aria-label="${caption}，窄屏可横向查看" tabindex="0"><table><caption>${caption}</caption><thead><tr>${heads.map(h => `<th scope="col">${h}</th>`).join('')}</tr></thead><tbody>${rows.map(r => `<tr>${r.map(c => `<td>${c}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
  X.field = (label, id, value = '', extra = '', type = 'text') => `<label class="field" for="${id}"><span>${label}</span><input id="${id}" name="${id}" type="${type}" value="${X.esc(value)}" ${extra}></label>`;
  X.check = (text, id = 'confirm') => `<label class="check"><input id="${id}" name="${id}" type="checkbox" required><span>${text}</span></label>`;
  X.page = (title, body, narrow = false) => `<main id="main" class="container ${narrow ? 'narrow' : ''}" tabindex="-1"><div class="breadcrumb">${X.link('发现游戏', 'store')}<span>/</span><span>${title}</span></div><h1>${title}</h1>${body}</main>`;
})();
