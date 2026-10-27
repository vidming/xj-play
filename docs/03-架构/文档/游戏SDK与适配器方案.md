# 游戏 SDK 与适配器方案

更新：2026-10-26。阶段3设计草案，未实现、未运行验证、未整体验收。本文按对象持续更新，不新增逐轮副本。

依据：[当前有效决策](../决策/当前有效决策.md)、[游戏接入与可信链路](游戏接入与可信业务链路候选-V0.1.md)、[接口契约边界](接口接入契约阅读与验证边界-V0.1.md)。机器可读源：[OpenAPI](../资料/平台OpenAPI-V0.1.json)、[消息桥](../资料/游戏消息桥Schema-V0.1.json)、[Manifest](../资料/游戏Manifest-Schema-V0.1.json)。

SD1已实际确认本文的细化方向；当前仍为架构规格，未实现或验收真实协议。对象存储已按OSF1选择SeaweedFS社区架构方向，精确版本引用和S3适配在后端内部完成，不能将存储凭据或可绕过当前权益的读取链接加入游戏SDK；底层产品改变不应改变游戏侧协议。

SD2将平台与各独立游戏的表/表数据统一放入当前MCP所连`xj_play`，按平台和游戏登记前缀区分。SDK仍只调用白名单平台能力，不增加SQL或数据库凭据接口；玩法专有数据由该游戏可信服务管理，不能直写平台订单或权益。同库权限、跨服务事务及删除恢复边界见[恢复规格7.3](部署资源与恢复规格.md#73-平台与每个独立游戏的同库归属)。

## 1. 职责与交付边界

薄 SDK 提供握手、白名单 RPC、资源读取、错误分类和清理；游戏可自行按相同协议适配，不绑定 Vue、Nuxt 或统一剧情引擎。宿主代理持有平台会话、显示交易与覆盖确认、调用可信 API；后端决定身份、权益、资源和存档归属。SDK 的返回值、游戏存档和事件都不能产生付款事实。

G-A 是独立故事交互前端；G-B 是独立线索、链接及仿真网页前端。二者是后续完整作品的接入目标，本轮不设计完整玩法、不制作游戏、不将测试片段算作完整交付。若游戏后来需要实时生成或私有第三方服务，另声明游戏自己的服务与成本，平台不把这些能力强加给所有作品。

后续 SDK 交付至少包括与具体框架无关的核心协议层、可选类型声明、宿主代理、资源加载适配说明、测试夹具及版本兼容表；当前只有这些边界的设计。

## 2. 通道与调用状态

运行顺序为 `LOADING → HELLO → INIT → CONNECTED → READY → CLOSED`。宿主验证准确来源、当前 frame 和固定游戏版本后，才为该次 run 建立 MessagePort；INIT 带 channelId 与最小 Run，不带平台长期令牌、邮箱或 Cookie。旧端口不得因重新握手而继续可用。

每个调用使用本端口内唯一 requestId；宿主从绑定上下文取得 runId 和主体，忽略游戏传入的身份。回复须同时匹配端口、协议、channelId、requestId 和 method。未知方法/错误形状明确拒绝，不尝试转换为任意平台 URL。capabilities 只缩小白名单，不能扩张服务端权限。

当前机器契约仅支持 `protocolVersion=1.0`。Manifest 中的 `max=1.x` 只是兼容声明，不能让尚无 Schema 的未来 minor 自动生效。未来 minor 须发布对应契约及双方兼容表；major 不兼容拒绝启动。未声明 save 能力的游戏仍可运行，不能因此暴露云档接口。

runtime.ready 表示游戏自己的初始化及必要试玩资源读取完成，不等于 iframe load。业务操作超时后，付款和存档先查原业务/operation；只读资源传输可以丢弃后重新鉴权读取，不凭重试赋予新权限。

## 3. 17 个 RPC 与可信 API 的映射

下表路径均以 `/app-api/xj/v1` 为前缀；宿主填写固定 runId，游戏不能指定其他 run。

| RPC | 宿主的可信操作 | 转换与限制 |
| --- | --- | --- |
| context.get | GET `/runs/{runId}/context` | 刷新最小上下文与固定版本资源索引 |
| access.check | POST `/runs/{runId}/access/check` | key 属于本作品；查询结果不代替资源鉴权 |
| resources.read | POST `/runs/{runId}/resources/read` | HTTP 二进制转换为本通道受控传输 |
| purchase.request | POST `/purchase-intents` | 宿主补 runId、绑定主体，显示平台商品确认；不自动下单 |
| purchase.status | GET `/purchase-intents/{intentId}` | 仅本主体与绑定作品的意图；回跳后仍核权益 |
| save.describe | GET `/runs/{runId}/save` | 仅已验证账号，返回元数据，不隐式下载来源 |
| save.read | POST `/runs/{runId}/save/read` | 核对来源和 expectedRevision，游戏解释 payload |
| save.write | POST `/runs/{runId}/save-operations` | action=WRITE；CAS 与稳定操作键 |
| save.import | POST `/runs/{runId}/save-operations` | action=IMPORT；宿主确认后提交 |
| save.restore | POST `/runs/{runId}/save-operations` | action=RESTORE；宿主确认来源后提交 |
| save.restart | POST `/runs/{runId}/save-operations` | action=RESTART；宿主确认后提交 |
| save.operation | GET `/save-operations/{operationId}` | 查同次可信操作；不生成新覆盖 |
| save.restoreConfirm | POST `/save-operations/{operationId}/restore-confirm` | 游戏只报告读档兼容，不提升为授权 |
| events.report | POST `/runs/{runId}/events` | 仅游戏可上报的白名单，服务端补 run/version/subject |
| runtime.ready | POST `/runs/{runId}/ready` | 服务端核验后改变运行状态 |
| runtime.exit | POST `/runs/{runId}/exit` | 清理通道及临时资源；退出不表示云档保存 |
| platform.return | POST `/runs/{runId}/exit`，随后宿主导航 | 仅平台登记的返回位置，无任意跨站 URL |

RPC requestId 只关联通信；持久 operationId 与 HTTP Idempotency-Key 独立关联真实动作，宿主保持重试关系。游戏不能用换 requestId 绕过持久防重。错误码沿用 OpenAPI；传输中断另用下节控制帧，不把传输失败伪装成订单失败。

HTTP的202不自动成为所有RPC的通用回复。当前仅存档提交显式允许202，数据仍为SaveOperation，宿主映射为原方法结果并按id查同次操作。资源HTTP只能返回二进制或错误；不存在未定义的资源异步operation查询。

## 4. 从游戏逻辑路径到平台资源

游戏构建引用 Manifest 的逻辑路径，例如 `content/r001.bin`。发布验证器完成安全归一化、唯一性和摘要核验后，为受控资源分配 resourceId。服务端的 Run.resourceIndex 仅包含该 run 固定版本的受控 `path → resourceId` 映射，随 INIT 和 context.get 返回；公开资源继续从已审核的公开包加载。

游戏适配器可以提供 `readByPath(path)` 这样的本地便捷函数：精确匹配索引，取 resourceId，再调用现有 resources.read；它不是新增的第18个 RPC。找不到路径时停止并报告版本/资源错误，禁止 fallback 到公共同名文件、任意 URL 或其他游戏索引。

索引不是秘密，也不是权益列表。即使未解锁内容，其不透明路径/编号也可能被看到；不得在路径中放谜底、剧情摘要或隐藏结局名称。资源正文是否可读仍由服务端按当前主体、run、版本、资源索引、发布状态和所需全部 contentKey 重核。索引应只输出必要字段，不能输出私有桶名、实际对象地址和签名 URL。

版本被固定后，resourceIndex 不跨版本合并；发布新版本、退出或换账号需新 run。服务端拒绝把另一个版本 resourceId 拼到本 run 请求中。Schema 只约束形状，路径唯一性、编码绕过、符号链接和实际归属由发布/运行验证器负责。

购买返回采用已确认RT1。宿主调用`POST /runs`时只可附带可选`intentId`，服务端核验当前主体、原意图、游戏、访问与版本后，才在`Run.resume`交付受控位置；客户端不得直接指定或覆盖`resumeHandle`。`RunResume.state=AVAILABLE`时位置、固定版本与到期时间绑定当次run；`UNAVAILABLE`时用明确原因且不携带位置。位置不授权，未获准内容仍由访问和资源检查拒绝。契约已调整但未运行验证，不得声称购买后恢复已可用。详见[接入链路6.1](游戏接入与可信业务链路候选-V0.1.md#61-购买返回契约rt1已确认)。

## 5. 二进制传输与内存边界

以下是拟采用的确定流程；具体数值额度仍待资源与性能验证。17个业务 RPC 不增加，传输使用专门控制帧。

1. resources.read 的成功回复先给 `ResourceTransfer`：resourceId、审核 MIME、总 byteLength、完整 sha256、transferId、chunkBytes、chunkCount。这里的成功只表示受理传输，SDK 对游戏的读取 Promise 尚未完成。
2. 宿主在同一 MessagePort 顺序发送原生消息 `{header, buffer}`，buffer 为独占 ArrayBuffer 并使用 transfer list。header 按 `ResourceChunkHeader` 校验，包含 protocolVersion、channelId、requestId、transferId、resourceId、chunkIndex、byteOffset、byteLength、final。
3. 从 index=0、offset=0 连续无重叠覆盖。`chunkCount=max(1,ceil(totalBytes/chunkBytes))`；普通非末块长度等于 chunkBytes，末块补足剩余长度。零字节资源仍有1个长度0、final=true的块，并核验空内容摘要。
4. 每个 transfer 最多1个未确认块。接收方完成非末块校验和有界暂存后，发 RESOURCE_ACK / CONTINUE 确认该 index；宿主收到后才能发下一块。末块完整长度和摘要通过后回 COMPLETE，并向游戏交付结果；失败发 CANCEL，宿主清理并尽力回 RESOURCE_ABORT。不能把仅收到 final 当作完整验证。
5. 接收者核对真实 ArrayBuffer 类型及字节数、当前通道与请求、连续 index/offset、末块位置、总长和完整摘要。RESOURCE_ACK 与 RESOURCE_ABORT 是纯 JSON 根消息；原生 `{header,buffer}` 不属于 JSON 根 Schema，只验证其中 header 的 JSON 形状。重复/越序/未知 transfer、错误摘要均中止并释放。
6. 资源读取在元数据前失败，走原 RPC 错误回复；元数据后源读取失败、超时或撤权，走 RESOURCE_ABORT。取消、frame 重载、端口关闭、换账号、run 撤销时拒绝未完成 Promise、释放所有缓冲及 ObjectURL；已交付给浏览器的字节不能保证收回。

宿主与 SDK 必须先配置并验证：单资源最大字节、单块最大字节、同时传输数、全局在途/已缓冲字节、整体与 ACK 超时；缺配置不开放资源能力。内存预算计入组装副本、摘要处理和 Blob 保留，不能只计算当前分块大小。拒绝超过 JS 安全整数的尺寸；在分配内存前检查预算。全局并发受控不等于全部文件可一次性预取。

HTTP 来源也需有界读取/背压；不能先把整个未知资源读成巨大 ArrayBuffer 再声称已经限流。完整摘要必须来自已审核发布索引，不能信游戏提供的摘要。可采用有界组装后核摘要；若以后需流式大媒体，则另设计受控分段协议，当前不默认为已支持任意尺寸视频。超时后重新读资源必须重新鉴权，不能续用已失效 run。

## 6. 两种独立前端的适配

| 对象 | G-A 故事主线交互 | G-B 线索/链接/仿真网页探索 |
| --- | --- | --- |
| 页面 | 游戏自己决定角色、选择、对话与结局页面 | 游戏自己决定虚构站点、路由、线索与推理页面 |
| 收费映射 | 故事/章节/场景 key 对应游戏自己的内容分区 | 调查区域或档案集合 key，可跨多页；URL不成为扣费依据 |
| 试玩 | 公开试玩内容＋试玩 run 允许资源 | 允许探索的试玩区域＋明确的内容边界 |
| 资源 | 公共引擎解析受控数据；图片/音频经受控读取生成 Blob | 仿真页面由公共引擎及受控模板数据组合，链接由游戏路由适配 |
| 进度 | 游戏自有格式记录选择等，平台只保存不透明 payload | 游戏自有格式记录发现与解谜状态；不能凭本地“已解锁”授予资源 |
| 购买返回 | 游戏给不透明 resumeHandle，平台核权益后重开上下文 | 返回原调查位置；跳转/刷新/重进不重复计费 |

动态 HTML、富文本和链接由游戏按审核规则安全渲染，不直接把受控文字当作任意可执行脚本。相对图片、CSS url、音频、模块 import 和 fetch 不会被协议自动改写；每个游戏需明确资源适配。Blob 使用结束就撤销 ObjectURL，切换作品/账号统一清理；不向 Service Worker 或公开缓存保存付费包。

首批两例推荐公共引擎＋受控内容数据。将整份付费 JavaScript 模块改成 Blob 并不自动解决相对 import、CSP 和代码泄露；若确需受控模块，另做专门适配与审核，不能承诺任意网页零改动即可接入收费。

## 7. 覆盖确认与存档结果

游戏传 `confirmed:true` 仅表达动作意图。IMPORT、RESTORE、RESTART 和冲突替换前，由平台宿主显示账号、作品、动作及来源/目标说明，绑定当前主体、run、action、baseRevision、format及 payload 摘要或 sourceBlobId。玩家同意之前不向服务端提交覆盖；取消应返回明确未提交。

确认期间换账号、run失效、来源改变或revision变化，都使原确认失效；不能重新包装请求后复用旧同意。服务端仍验证本人归属、生命周期、格式、大小、CAS与持久防重，confirmed不是安全凭据。本轮没有添加或虚称已实现服务端确认令牌。

普通 WRITE 沿用已确认自动保存规则，不因每次RPC都弹框；冲突解决、导入、恢复及重开保持明确确认。读出存档只说明字节已取得，游戏完成自身兼容校验后用 save.restoreConfirm 报告，不能用“有返回值”代替恢复成功。

## 8. 后续验证条件

必须覆盖：跨账号/游戏/版本 resourceId、漏索引与重复路径、零长度/多块/错误摘要/越序、伪造 ACK、超预算与中途断开、确认后切账号、CAS冲突、未知付款与购买返回、停售与暂停差异、退款后读取、完整游戏双类型接入。

“我的游戏”采用已确认CL1：`LibraryItem.continue`只返回是否可继续、保存状态、适用版本、最近活动时间与访问状态，不返回原始存档payload、完整剧情位置或可当作权益的handle。摘要不能证明读档成功；继续能力必须在进入新run后按当前权益和存档接口重新核验。详见[接入链路6.2](游戏接入与可信业务链路候选-V0.1.md#62-我的游戏--继续游玩契约cl1已确认)。

本轮只运行静态契约和代表性 JSON 样本检查；未执行真实 MessagePort、内存压测、网络中断、用户确认、身份隔离、付款或存档事务。以上要求在完整架构验收后纳入实施计划，不能写成已经通过。
