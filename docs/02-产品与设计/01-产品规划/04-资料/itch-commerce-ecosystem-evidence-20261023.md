# itch.io 交易与创作者生态：研究证据（非已批准需求）

- **状态：阶段 1 首节点研究证据；不代表首期功能、产品需求或实施方案已获批准。**
- 访问日期：**2026-10-23，Asia/Shanghai**。下表每项日期均为实际查阅日期，不代表来源发布日期。
- 范围：交易、购买交付、下载权益、analytics、devlog、互动与评分、收藏与关注、jams、可选 Steam keys。品牌、发现、HTML5 与运行边界由主代理另行研究；本文不作这些方面的结论。
- 方法：通过 `web.run` 访问 itch.io 官方文档及官方更新公告；未登录、购买或发送消息，未读取项目旧文档。仅写入本文件。
- 证据口径：**已核实**表示公开官方来源明确记载，不代表实测后台或交易；**历史证据**保留官方发布日期，不能单独证明 2026 年全部细节仍相同；**未知**与**分析推断**另列。页面中第三方留言不作官方证据。

## 逐项能力与边界

每行的 S 编号对应后文的原始 URL、支持段落和短摘录；链接直接指向官方原页。相同来源可支持多项能力。

| 编号 | 状态与具体能力 | 官方原始 URL／支持段落 | 访问日期 | 限制与适用边界 |
| --- | --- | --- | --- | --- |
| C01 | **已核实：定价。** 项目可免费、最低价为 0 或正数的付费自愿加价，也可关闭付款。 | [S01 · Pricing options / Pay what you want pricing / Disabling payments](https://itch.io/docs/creators/pricing) | 2026-10-23 | 免费跳过付款下载，不自动取得项目所有权或 library 记录；官方另述以帐号领取赠送所有权的机制，不能一概等同所有免费项目。 |
| C02 | **已核实：两种收款模式。** 官方区分直接向创作者付款与由 itch.io 代收后 payout；页面说明相应支付渠道及退款、拒付责任差异。 | [S02 · Payment modes](https://itch.io/docs/creators/payments) | 2026-10-23 | 不据此认定任意地区、帐号或币种均可使用相同渠道；本次未验证具体创作者资格与实际结算。 |
| C03 | **已核实：购买与找回。** 可不注册购买；成功购买后获得下载页面，购买邮件包含访问链接；可通过购买所用邮箱请求重新发送。 | [S03 · After buying something… / Recovering purchases / Registering an account](https://itch.io/docs/buying/already-bought) | 2026-10-23 | 邮箱与下载链接承担找回职责；连接帐号是可选步骤，不能假定所有购买都已有帐号归属。 |
| C04 | **已核实：项目 download key。** key 是访问该项目下载页的唯一 URL，可来自购买或创作者赠送；页面包含当前文件及购买附加内容。 | [S04 · Download keys](https://itch.io/docs/creators/download-keys) | 2026-10-23 | 这是项目文件访问凭证；来源没有把它定义为通用游戏内部权益凭证。不要公开真实 key。 |
| C05 | **已核实：购买后的更新访问。** 一般 key 可继续取得创作者上传的更新，即使项目最低价后来提高。 | [S04 · Download keys；S01 · Individually priced files](https://itch.io/docs/creators/download-keys)；[S01 原页](https://itch.io/docs/creators/pricing) | 2026-10-23 | 单独定价文件有例外：若文件门槛提高至超过原付款额，可失去该文件访问权；不能承诺所有未来文件永久包含。 |
| C06 | **已核实：文件级价格门槛。** 可为特定上传文件设置高于项目最低价的门槛，用于 soundtrack、资源或其他附加文件。 | [S01 · Individually priced files](https://itch.io/docs/creators/pricing) | 2026-10-23 | 门槛作用于文件下载；不能据此认定平台提供游戏内 chapter／scene 解锁或网页运行付费门禁。 |
| C07 | **已核实：赠送与撤销 key。** 创作者可生成单个或批量 key，并查看 key 下载使用情况；单个 key 可撤销，批量 key 可按组撤销。 | [S04 · Generating / Single / Bulk download keys](https://itch.io/docs/creators/download-keys) | 2026-10-23 | 默认赠送 key 不附带外部 key，可另行启用；撤销影响平台下载访问，不能据此推断已下载副本会失效。 |
| C08 | **已核实：bundle 的延迟分配。** 购买 bundle 已取得其中各项目所有权；超过 15 个项目时，单项目 key 在购买者打开相应项目下载页时才分配。 | [S05 · Bundles and download keys](https://itch.io/docs/creators/bundles) | 2026-10-23 | 此时创作者初见的 claimed keys／owners 不等于 bundle 总销量；未领取单项目 key 不等于未购买。 |
| C09 | **已核实：下载页的失效情形。** 买家帮助页说明，退款、拒付或创作者撤销访问可能使原下载页不可用。 | [S03 · Download not available](https://itch.io/docs/buying/already-bought) | 2026-10-23 | 仅证明下载页访问可能被移除；不证明平台能撤回本地文件，也不替代完整退款政策。 |
| C10 | **已核实：可选 Steam 等外部 key。** 创作者可上传其控制的外部 key；通常在购买后由买家到下载页点击领取，成功分配的 key 会保留在该页。 | [S06 · Distributing / Claiming / Running out of keys](https://itch.io/docs/creators/other-keys) | 2026-10-23 | 免费下载不自动发 Steam key；库存耗尽时买家可能没有 key。可设最低领取价格；赠送下载 key、bundle 也有附带条件，不能宣传为购买必送。 |
| A01 | **已核实：基础项目统计。** 创作者介绍页明确列出访问、下载、购买统计，并说明 dashboard 的 analytics 可查看随时间变化的汇总。 | [S07 · Understanding your game’s analytics](https://itch.io/docs/creators/getting-started) | 2026-10-23 | 文档未在该段定义去重、机器人过滤、刷新延迟或游戏内部事件口径。 |
| A02 | **历史证据：更详细的 analytics。** 2018-05-10 官方公告展示时间筛选、曝光及 CTR、收藏来源流量、自定义跟踪链接、独立图表和 CSV／JSON 导出。 | [S08 · Impressions / Tracking links / …exporting graphs](https://itch.io/updates/updates-to-project-analytics-filtering-collections-impressions-and-more) | 2026-10-23 | 公告口径中，曝光只计 itch.io 浏览、搜索和 collection 页面；不含外部搜索、其他网站或直接访问。2018 年功能及口径未在 2026 年登录后台复验，不能直接承诺现行报表能力。 |
| E01 | **已核实，附历史补证：项目 devlog。** 当前关注文档列出新 devlog 进入关注流；2017-05-03 官方介绍将其定义为项目关联的开发／更新日志，并说明评论、点赞。 | [S09 · Enhanced devlogs](https://itch.io/updates/enhanced-devlogs-all-the-tools-you-need-to-make-a-beautiful-blog)；[S10 · Types of events](https://itch.io/docs/general/following) | 2026-10-23 | 2017 年编辑器、媒体能力与互动界面仅有历史证据；不能由 devlog 推断平台提供游戏内章节管理。 |
| E02 | **已核实：项目讨论。** 项目页可启用 message board 或评论区；创作者可配置互动渠道。 | [S11 · Interacting with your audience](https://itch.io/docs/creators/interact) | 2026-10-23 | 文档没有在此承诺私信、客服工单或完整社交系统；实际互动取决于项目设置。 |
| E03 | **已核实：玩家评分。** 官方把对玩过的游戏评分列为粉丝反馈渠道，可影响游戏排序。 | [S11 · Fans…rate the games…](https://itch.io/docs/creators/interact) | 2026-10-23 | 这里描述的是玩家反馈评分；不能将可见 rating 当作内容年龄评级或适龄认证。 |
| E04 | **已核实：收藏列表。** collection 用于组织游戏，官方说明其由用户维护、可写说明并分享／嵌入；公开 collection 可进入信息流。 | [S10 · Types of events / Collections](https://itch.io/docs/general/following) | 2026-10-23 | 收藏是组织与分发行为；该来源没有赋予收藏者购买或下载权益。 |
| E05 | **已核实：关注与信息流。** 可关注用户，无需对方批准；关注流可出现新项目、devlog、公开收藏和被关注者加入 jam 等事件。 | [S10 · Following users / Types of events / FAQ](https://itch.io/docs/general/following) | 2026-10-23 | 官方明确说明，新上传文件本身没有特别通知；应通过 devlog 传达更新。不能把关注视为所有事件必达通知。 |
| E06 | **已核实：jam 组织。** 用户可免费创建 jam，设置投稿期；可开放参加或由主办者控制投稿，也可选择 ranked／unranked。 | [S12 · Creating a new jam / Jam customization](https://itch.io/docs/creators/game-jams) | 2026-10-23 | jam 可用于比赛或集中展示；不是所有 jam 都有评分、排名或奖项。 |
| E07 | **已核实：jam 专用评分。** ranked jam 可配置评分维度、参与投票者和主排序维度；投稿期后评分，投稿者不能给自己的作品评分。 | [S12 · Jam customization / Judging and rating](https://itch.io/docs/creators/game-jams) | 2026-10-23 | jam 分数不影响项目主站的 community star rating；作品可选择退出评分。也不能将 jam 评分当内容年龄评级。 |

## 官方源与支持段落

以下为上表的定位凭据。引号内为短原文摘录，其余为对应段落的中文转述；每源原文摘录控制在 25 个英文词以内。访问日期均为 **2026-10-23（Asia/Shanghai）**。

**S01 — Pricing**

- 原始 URL：<https://itch.io/docs/creators/pricing>
- 支持段落：`Pricing options`、`Pay what you want pricing`、`Individually priced files`、`Disabling payments`。说明最低价、0 元跳过下载、付费取得所有权及文件单独定价。
- 原文定位：“only has access to the files they downloaded”；文件价格上调时另述“may lose access”。
- 限制：更新访问的一般说明必须连同文件门槛例外引用；不能把文件门槛解释成运行门禁。

**S02 — Accepting Payments and Getting Paid**

- 原始 URL：<https://itch.io/docs/creators/payments>
- 支持段落：`Payment modes` 区分直接收款与 itch.io 代收；`Comparing payment modes` 表列渠道、退款和拒付处理差异。
- 原文定位：“Direct to you”；“Collected by itch.io”。
- 限制：这是平台文档中的模式说明，本次没有验证任何具体帐号的可用性、税务处理或到账时间。

**S03 — Accessing your purchased files**

- 原始 URL：<https://itch.io/docs/buying/already-bought>
- 支持段落：`After buying something…` 说明付款后页面及邮件；`Recovering purchases` 说明邮箱找回；`Registering an account` 说明可不注册购买；`Download not available` 说明退款、拒付、撤销访问等情形。
- 原文定位：“You don’t have to register to buy things on itch.io”。
- 限制：不能从页面访问状态进一步推断本地副本或游戏内部权益；本文没有核查完整退款申请规则。

**S04 — Download keys**

- 原始 URL：<https://itch.io/docs/creators/download-keys>
- 支持段落：开头定义 key 的项目下载访问用途；`Single download key` 说明 tracker、撤销及默认不附外部 key；`Bulk download keys` 说明批量和按组撤销。
- 原文定位：“A download key is a special URL that gives someone access to the download page for a game”。
- 限制：默认赠送 key 不等同付费购买记录；对未来文件的访问还受 S01 的单独定价规则约束。

**S05 — Bundles**

- 原始 URL：<https://itch.io/docs/creators/bundles>
- 支持段落：`Bundles and download keys` 说明 bundle 所有权、超过 15 个项目的延迟 key 分配，以及统计中 owners 随 key 领取而增长。
- 原文定位：“if the bundle contains more than 15 projects”。
- 限制：bundle 购买、项目 key 分配和创作者看到的 owner 数量是不同环节，不能直接互换计数。

**S06 — Distributing Steam keys**

- 原始 URL：<https://itch.io/docs/creators/other-keys>
- 支持段落：`Distributing / Claiming / Running out of keys` 说明上传库存、买家领取和耗尽情形；`Setting a minimum price`、`Download keys and Steam keys`、`Steam keys and bundles` 列出附带条件。
- 原文定位：“Someone who downloads your game for free will not get access to a Steam key”。
- 限制：是否提供、库存、最低领取金额及 bundle 设置均会影响结果；不能将 itch.io 的 download key 与 Steam 激活 key 混用。

**S07 — Getting started**

- 原始 URL：<https://itch.io/docs/creators/getting-started>
- 支持段落：`Understanding your game’s analytics` 说明项目页统计访问、下载与购买，dashboard 可看时间维度汇总。
- 原文定位：“how many times your game is being viewed, downloaded, and purchased”。
- 限制：该段没有提供完整指标字典或游戏内行为采集说明。

**S08 — Updates to project analytics: filtering, collections, impressions, and more**

- 原始 URL：<https://itch.io/updates/updates-to-project-analytics-filtering-collections-impressions-and-more>
- 官方发布日期：**2018-05-10**。
- 支持段落：`Impressions` 明确曝光范围及 CTR；`Tracking links`、`Individual graphs`、`Comparison mode…exporting graphs` 展示跟踪、图表与导出。
- 原文定位：“Just the browse, search, and collection pages count towards impressions”。
- 限制：来源是历史发布公告；不能省略年份，或将其中 UI、格式和计数定义无条件当作 2026 年现状。

**S09 — Enhanced devlogs: All the tools you need to make a beautiful blog**

- 原始 URL：<https://itch.io/updates/enhanced-devlogs-all-the-tools-you-need-to-make-a-beautiful-blog>
- 官方发布日期：**2017-05-03**。
- 支持段落：开头定义项目关联 devlog；`Integrated with the itch.io community` 说明关注流分发；`Discuss and like posts` 说明评论、点赞。
- 原文定位：“Every post you create can be discussed with comments. Readers can also like your posts”。
- 限制：当前关注流中的 devlog 事件另有 S10 补证；编辑器及具体互动细节保留历史证据标签。

**S10 — Following users**

- 原始 URL：<https://itch.io/docs/general/following>
- 支持段落：`Types of events` 列 devlog、公开 collection、jam 参加等；`Collections` 说明整理和分享；`FAQ` 说明无需批准及文件更新通知边界。
- 原文定位：“there’s no special notification when new files are uploaded”。
- 限制：关注流事件不等同通知必达承诺，也不产生购买或下载权益。

**S11 — Interacting with your audience**

- 原始 URL：<https://itch.io/docs/creators/interact>
- 支持段落：正文说明项目页可启用 message board 或 comments；后段说明玩家评分及其对排序的影响。
- 原文定位：“Fans of your games can also rate the games they’ve played”。
- 限制：段落谈论交流与玩家反馈，没有提供内容年龄评级证明。

**S12 — Hosting a game jam**

- 原始 URL：<https://itch.io/docs/creators/game-jams>
- 支持段落：`Jam customization` 列投稿、评分权限、ranked／unranked；`Judging and rating` 说明评分时期、不得自评和退出评分。
- 原文定位：“will not affect its main rating on itch.io (the community’s star rating)”。
- 限制：jam 评分与主站评分分开；本次没有验证具体 jam 的规则配置或投票结果。

## 未知／本次不能核实

1. **游戏内部权益与进度：** 本次来源未提供 download key 对 chapter／scene、道具、游戏内部帐号权益或跨设备云存档的通用官方承诺。不能据文件交付能力认定支持，也不能据此断言平台绝不支持某种开发者自建实现。
2. **网页运行付费门禁：** 文件定价、购买记录、download key 均不足以证明浏览器运行前存在收费门禁；此问题留给主代理的 HTML5／运行研究，本文不作结论。
3. **2026 年 analytics 完整规格：** 未登录实测，未核实当前导出字段、去重／反作弊、统计延迟、实时性、用户级身份、游戏内事件或转化漏斗。2018 年公告是带日期的证据，不能替代现行后台验收。
4. **真实交易与库存：** 未下单、退款、领取 key 或执行创作者 payout；无法确认特定项目的实际价格、支付渠道、邮件到达、Steam 库存及交付成功率。
5. **退款与结算完整规则：** 已核实退款／拒付可能影响下载访问及收款模式存在责任差异；未系统核查退款申请条件、法域差异、时限、全部费用或帐号资格，不据此给出政策结论。

## 分析推断（用于理解证据，不是需求）

- **交易链应分开理解：** 购买所有权、单项目 key 分配、文件下载和可选外部 key 领取分别有独立条件；大型 bundle 的延迟 key 分配尤其说明这些状态不能直接等同。（依据 S01、S04、S05、S06）
- **analytics 不能直接代表玩家体验：** 访问、下载和购买属于平台页面／交付层面的统计证据；没有游戏内部事件口径，就不能据此得出章节完成、留存或云存档成功等结论。（依据 S07、S08 及本次证据范围）
- **生态入口与权益应分开引用：** devlog、评论、评分、collection、关注及 jam 说明传播与参与机制；这些文档未将互动行为定义为购买授权。它们可作为研究对象，不构成首期功能获批。（依据 S09–S12）
