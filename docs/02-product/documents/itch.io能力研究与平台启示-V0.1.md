# itch.io 能力研究与间隙PLAY 的产品启示

- 版本：V0.1
- 调研日期：2026-10-23（Asia/Shanghai）
- 状态：首节点研究已按证据与限制接受，见[当前有效决策](../../03-架构/决策/当前有效决策.md)；所有平台启示仍为分析建议，不是批准的首期需求。
- 范围：发现、项目页、运行与分发、交易与访问、发布运营、分析和生态；不做技术选型。
- 方法：核对公开官方页面与文档；未登录、付款、上传、领取 key、调用认证 API 或测试创作者后台。
- 来源：主代理核对发现与运行，research 后台代理核对交易和生态；[交易生态详细证据](../sources/itch-commerce-ecosystem-evidence-20261023.md)。
- 日期解释：调研日期是实际访问日期，不是来源发布日期；历史公告另外标记。页面当前可访问，不证明全部说明仍与生产行为逐项一致。

## 1. 主要结论

1. itch.io 可以参考为“可发现的作品目录、可配置项目页、不同的运行/文件分发、交易访问与创作者生态”的组合，不能压缩成一种游戏界面。依据 R01、R02、R03、R05。
2. 类型、题材、运行形式、输入方式、单次体验长度与可访问性是不同维度；把“文字互动”直接等同一种页面或玩法会丢失这些区别。前半句是 R01 的页面事实，后半句是分析推断。
3. HTML5 嵌入运行、可购买下载、文件价格门槛和项目购买访问是不同能力。HTML5 官方指南目前描述嵌入游戏收款为打赏，出售访问需切换下载类项目；不能把一般商店收款能力当作现成网页收费运行机制。依据 R03、T01、T04。
4. 官方有项目所有权查询、下载 key 与授权凭据等机制，但本次资料没有证明统一的游戏内章节/场景权益、剧情引擎或跨设备云存档服务。依据 R06、T04；这是证据边界，不是断言所有外部游戏都不可能自建。
5. 间隙PLAY 可借鉴清晰的作品信息与平台/作品分离思路，仍须自行确认交易、接入和运营范围；不能直接认领“itch.io 有完整方案，照搬即可”。

## 2. 证据分类

| 标记 | 含义 |
| --- | --- |
| 页面观察 | 访问公开页面能看到的入口和信息，不证明点击后的所有逻辑 |
| 官方文档 | 官方明确描述的能力，不是本轮生产实测 |
| 历史公告 | 已知发布年份的官方记录；现行细节仍需验证 |
| 分析推断 | 根据资料得出的产品解释或建议，与事实分开 |
| 未证实 | 没有足够证据支持，不能写成有或没有的确定结论 |

## 3. 发现与作品展示

| 编号 | 已核实能力 | 依据与定位 | 对间隙PLAY 的启示（待确认） | 边界 |
| --- | --- | --- | --- | --- |
| D01 | 游戏浏览页有搜索、筛选、排序、标签和游戏卡片 | R01 `/games` 页面观察 | 研究玩家如何从目录缩小候选，再进入详情 | 不推断搜索算法、个性化能力或运营权重 |
| D02 | 可按运行平台、价格、发布时间、类型筛选 | R01 Filter results | 把设备、价格和内容类型分开研究 | 不预设首期要实现所有筛选项 |
| D03 | 可按输入方式、单次体验长度、多人及可访问性特征筛选 | R01 对应分组 | 对文字互动作品，也应研究实际操作方式和体验投入 | 时长是特征，不代表所有作品必须短篇 |
| D04 | HTML5/可下载、试玩、Steam key 等可作为独立发现条件 | R01 Type、Misc | 区分玩法与交付形式，避免把网页运行等同全部游戏 | Steam key 不是 Steam 客户端或发行接入方案 |
| D05 | 有 Popular、New & Popular、Top sellers、Top rated、Most Recent 等排序 | R01 Sort by | 研究“推荐、热度、销量、评分、新发布”分别代表什么 | 没有取得算法公式，不能假设等于真实销量排序或转化最优 |
| D06 | 项目创建包含分类、标签、上传文件、说明和可见性设置 | R02 Basic information、Tagging、Publishing | 游戏信息与游戏程序是不同对象，可分别维护 | 不据此批准创作者自助入驻 |
| D07 | 项目页可配置布局、字体/颜色、图像、说明、截图与购买/下载区域 | R05 页面设计各节 | 商店信息可统一解释，作品仍可表达自己的风格 | 项目页自定义不同于游戏运行代码，不批准任意 CSS 接入 |
| D08 | 质量指南要求相关标签与分类，公开页并不自动等于进入发现索引 | R04 indexed/discovery、tags 与公开发布说明 | “能访问、可售、可被发现”需要区分 | 不是采用 itch.io 审核规则，也不推定其审核时限 |

研究没有将列表结果总数、热榜作品、页面排列或题材比例作为稳定市场统计；页面数据动态变化，不能据此推导目标市场规模。

## 4. 运行、分发与更新

| 编号 | 已核实能力 | 依据与定位 | 产品意义 | 不能据此推出 |
| --- | --- | --- | --- | --- |
| Rn01 | 可上传自包含 HTML，或带入口文件的 ZIP 资源包，由平台托管并在项目页内嵌运行 | R03 Getting started、ZIP/HTML file | 完整网页程序可以作为作品接入资产，不一定是结构化剧情数据 | 本平台已经选择 ZIP、iframe 或某种托管架构 |
| Rn02 | 可选页面内显示、点击后全屏启动，并有点击运行等嵌入配置 | R03 Embed options | 启动外壳与游戏自身页面可以分离 | 每个游戏都必须采用同一游戏页面 |
| Rn03 | HTML5 指南单独说明移动浏览器适配与 Mobile Friendly 标记 | R03 Support for Mobile HTML5 Games | 作品是否适配移动浏览器应单独验证 | 标记即兼容所有设备，或已经具备原生 App/小程序 |
| Rn04 | 指南允许来自不同引擎的网页导出，并列出相应引擎示例 | R03 Game Engine Detection | 可在不同游戏程序之上提供商店服务 | 平台提供统一引擎、编辑器或剧情格式 |
| Rn05 | 文件上传和更新在同一项目页管理，免费 demo 文件可与付费文件同页存在 | R02 Uploads、Updating your project | 作品、版本和可体验文件需要分开理解 | 付费文件等同已完成游戏内章节解锁 |
| Rn06 | 浏览器运行存在文件、路径、容量及外部资源等约束 | R03 ZIP requirements、Common pitfalls | 接入要有可检查的约束，不能只说“任意网页即插即用” | 把对标限制原样定为本平台技术规范 |
| Rn07 | HTML5 嵌入的收款在该指南中描述为打赏；出售访问的说明转向 Downloadable 项目类型 | R03 Can I take payments… | 浏览运行与购买交付必须单独论证 | 公开内嵌页天然有可信购买门禁，或下载付费可直接作为章节计费 |
| Rn08 | API 参考列有 profile、owned keys、purchases、ownership、collections，并区分凭据及 scope | R06 Authentication、Reference | 身份授权和访问查询可以是平台能力，但职责应明确 | API 列表即完整游戏接入 SDK、云存档或游戏内权益服务 |

本节没有验证隔离安全性、异常恢复、缓存/CDN 策略、回调可靠性或版本兼容，也没有比较本平台的具体架构方案。

## 5. 交易、访问与找回

以下 T 编号对应第 9 节官方源；逐段证据见配套交易生态研究。

| 编号 | 已核实能力 | 官方依据 | 对间隙PLAY 的研究启示 | 限制 |
| --- | --- | --- | --- | --- |
| C01 | 支持免费、最低价与自愿加价，并可关闭付款 | T01 Pricing | 先研究商业对象与玩家理解，再决定收费形式 | 不默认复制自愿定价、打赏或虚拟币 |
| C02 | 区分直接向创作者付款和 itch.io 代收后结算 | T02 Payment modes | 供给与收款主体会影响业务责任 | 未研究本项目适用法域、渠道资格、税务及成本，不提供选型结论 |
| C03 | 购买可不先注册，下载页与购买邮箱用于访问和找回；可关联账号 | T03 Buying、Recovering、Registering | “购买、身份归属和找回”是需明确的不同环节 | 不代表本项目应采用游客购买 |
| C04 | 项目 download key 用于访问下载页，可来自购买或赠送 | T04 Download keys | 文件交付凭证与游戏内授权不可混淆 | 不等于通用游戏会话、章节或云存档凭证 |
| C05 | 文件可单独设价格门槛，后续文件与已购访问存在例外条件 | T01、T04 | 权益范围及版本升级规则必须解释清楚 | 不承诺所有后续内容永久免费 |
| C06 | 可生成与撤销单个/批量赠送 key | T04 Single/Bulk keys | 需研究赠送、购买、撤销等概念是否适用于本平台 | 撤销下载访问不能证明已下载文件会失效 |
| C07 | bundle 购买与单项目 key 分配可发生在不同时间 | T05 Bundles and download keys | 购买、领取、下载不应混成一个状态或一个统计数 | 不批准首期 bundle 或多商品购物车 |
| C08 | 退款、拒付或撤销访问可能导致下载页不可用 | T03 Download not available | 需在后续业务方案明确权益变化与反馈 | 未系统研究完整退款政策，不能据此定本平台规则 |
| C09 | Steam 等外部 key 可选，买家领取受库存、金额及项目设置影响 | T06 Distributing/Claiming keys | 发行渠道权益与平台自身购买访问是不同概念 | 不能当作 Steam 平台客户端、统一容器或购买必送 |

## 6. 运营分析与创作者生态

| 编号 | 已核实内容 | 官方依据 | 研究结论及限制 |
| --- | --- | --- | --- |
| O01 | 创作者文档描述项目访问、下载、购买统计和 dashboard 时间趋势 | R02/T07 Analytics | 是页面与交付层数据，不证明游戏内章节完成、留存或存档成功 |
| O02 | 2018-05-10 公告描述曝光、CTR、来源、自定义跟踪及导出 | T08 历史公告 | 带年份的功能记录，未登录核实当前字段、去重和实时性 |
| O03 | 关注流包括新项目、devlog、公开 collection 等事件 | T10 Following | 内容更新与文件上传并不自动产生完全相同的通知 |
| O04 | 项目可启用评论或 message board，并接受玩家评分 | T11 Interacting | 玩家反馈评分不是适龄评级；社交入口不是本平台首期必需 |
| O05 | collection 可组织作品并用于分享/发现 | T10 Collections | 收藏行为不自动获得购买或下载权益 |
| O06 | game jam 支持投稿与可配置评分/排名，jam 评分与主站评分分开 | T12 Hosting a game jam | 可作为生态研究，但不同评分与访问机制需要区分；不批准首期赛事系统 |

这些能力说明成熟生态由多种机制叠加形成，不能据此要求初期平台一次做完社交、活动、分账和复杂营销。

## 7. 描述性路径与项目判断

下表是对标能力的归纳，不是间隙PLAY 已确认的用户流程或信息架构。

| 对标情境 | 可确认的机制 | 仍不清楚或未实测 |
| --- | --- | --- |
| 玩家找作品 | 搜索/筛选/排序 → 项目页查看信息 | 推荐质量、个性化、排序公式和真实发现转化 |
| 玩家玩 HTML5 | 项目页 → 载入托管网页代码 → 页面内或全屏运行 | 游戏内身份/购买检查、存档恢复及实际异常表现 |
| 玩家购买下载 | 付款 → 下载页/邮件访问 → 可关联账号 → 取回文件 | 特定地区付款、邮件送达、退款全流程 |
| 创作者更新 | 维护项目与文件 → 可发布 devlog → 关注流传播 | 审核时延、所有版本回滚语义和通知必达 |
| 买家取外部 key | 购买与项目下载页 → 满足条件时领取 | 库存、平台外激活状态及特定作品附送条件 |

### 7.1 可以借鉴、仍待拆解的方向

- 以作品元信息帮助玩家决策，而不是用平台品牌统一游戏玩法。
- 把可见性、发现、体验、购买、访问和数据恢复分别说明。
- 对同一作品的不同文件、试玩和后续内容解释清楚，不以模拟提示代替真实交付。
- 允许游戏保有自己的页面和规则，同时研究哪些通用能力必须由平台可信地提供。

### 7.2 不直接移植的部分

- 不直接移植 itch.io 的收款渠道、结算、规则、资源限制和 API。
- 不复制其全量分类、生态功能、运营组织或页面皮肤。
- 不默认自助上传、社区、jam、bundle、赠送 key 或 Steam key 进入首期。
- 不把其通用商店能力当作本项目章节/场景交易、云存档和游戏接入的完整现成答案。

### 7.3 需要独立论证的缺口

与本项目任务书直接相关、但本次来源未给出可照搬完整答案的事项：付费网页运行、场景/章节映射、平台与游戏可信身份、存档责任与冲突、版本兼容、安全隔离、运行失败处理及游戏内事件。

这不是当前架构设计任务。后续产品阶段应先定义需要解决的体验和业务规则，经确认再由架构阶段比较实现。

## 8. 可信度与限制

- 来源均为 itch.io 官方页面或官方公告，不使用第三方文章推定机制。
- 主代理 6 个页面响应为 HTTP 200；标题、最终地址、访问日期和响应哈希见[来源元信息](../sources/itch-primary-sources-20261023.json)。
- 交易生态研究另列 12 条官方来源，其中 getting-started 与主代理重复；合计 17 个不同官方 URL。它们不是 17 个独立利益来源，而是同一平台的一手说明。
- 未登录观察商家后台，未完成真人购买、上传、退款、游戏启动或 SDK 接入测试。
- 研究未证明目标用户规模、竞争优劣、可持续供给、收入或首期投入产出，不提供虚构指标。
- 未核实平台没有的能力，只能说这些来源尚未证明。未把公告发布日期当作访问日期，也未用历史公告直接证明 2026 年后台全部规格。

## 9. 官方来源索引

每个来源的访问日期均为 2026-10-23（Asia/Shanghai），除注明历史日期外，发布日期未核实。源 R 与交易证据内部 S 编号分别使用，不混用。

| ID | 官方页面 | 支持章节 |
| --- | --- | --- |
| R01 | [Top games](https://itch.io/games) | Filter results、Sort by、项目卡片 |
| R02 | [Your first itch.io page](https://itch.io/docs/creators/getting-started) | Basic information、Uploads、Tagging、Publishing、Updating、Analytics |
| R03 | [Uploading HTML5 games](https://itch.io/docs/creators/html5) | Getting started、Embed options、Payments、Mobile、Common pitfalls |
| R04 | [Content creator quality guidelines](https://itch.io/docs/creators/quality-guidelines) | Discovery index、分类与相关标签、发布和质量边界 |
| R05 | [Designing your page](https://itch.io/docs/creators/design) | 布局、说明、颜色字体、购买/下载区域、Mobile pages |
| R06 | [Serverside API reference](https://itch.io/docs/api/serverside) | Authentication、Scopes、Reference |
| T01 | [Pricing](https://itch.io/docs/creators/pricing) | Pricing options、Individually priced files |
| T02 | [Accepting Payments and Getting Paid](https://itch.io/docs/creators/payments) | Payment modes、Comparing modes |
| T03 | [Accessing your purchased files](https://itch.io/docs/buying/already-bought) | Buying、Recovering purchases、Registering、Unavailable |
| T04 | [Download keys](https://itch.io/docs/creators/download-keys) | Download keys、Single、Bulk |
| T05 | [Bundles](https://itch.io/docs/creators/bundles) | Bundles and download keys |
| T06 | [Distributing Steam keys](https://itch.io/docs/creators/other-keys) | Distributing、Claiming、Minimum price、Inventory |
| T07 | 与 R02 相同 | Understanding your game's analytics |
| T08 | [Updates to project analytics](https://itch.io/updates/updates-to-project-analytics-filtering-collections-impressions-and-more) | 2018-05-10 历史公告 |
| T09 | [Enhanced devlogs](https://itch.io/updates/enhanced-devlogs-all-the-tools-you-need-to-make-a-beautiful-blog) | 2017-05-03 历史公告，devlog 与互动 |
| T10 | [Following users](https://itch.io/docs/general/following) | Types of events、Collections、FAQ |
| T11 | [Interacting with your audience](https://itch.io/docs/creators/interact) | Message board、Comments、Ratings |
| T12 | [Hosting a game jam](https://itch.io/docs/creators/game-jams) | Customization、Judging and rating |

## 10. 提交与后续边界

本稿供确认研究覆盖和产品方向，不是一张已排优先级的功能清单。推荐把“发现与表达清晰、交易访问边界明确、游戏保持独立”带入下一项产品推演；具体角色、首期闭环及功能取舍须再提交确认。
