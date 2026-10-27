# MinIO开源版本与能力核查

核查日期：2026-10-25，Asia/Shanghai。状态：阶段3一手资料与固定源码核查；产品未选定，未下载制品、安装、构建、连接存储或执行故障测试。

状态更新：2026-10-26；用户已实际确认OS1比较，完成的对比与产品建议见[对象存储候选对比](对象存储候选对比.md)。下列来源事实保留原实际读取日期。

关联：[当前有效决策](../01-决策/当前有效决策.md)、[开源组件与对象存储适配方案](../03-文档/开源组件与对象存储适配方案.md)、[部署资源与恢复规格](../03-文档/部署资源与恢复规格.md)。

## 1. 本轮结论

用户要求MinIO优先、其他组件尽量开源。可以继续评估MinIO社区源码，但不能沿用“仍有官方社区维护和持续预编译发布”的假设：官方仓库页面显示2026-04-25已归档只读；当前README明确停止维护，社区版仅源码分发，历史二进制不再维护。[S1][S2]

README推荐的AIStor Free具有不同的产品和许可入口，不能只因“Free”就认定其为同一AGPL社区服务器或自动替换。当前没有选用AIStor，也没有采购或开通任何产品。[S2]

用户已接受OS1：保持开源优先，按本项目私有对象、精确版本清理、恢复与维护要求比较MinIO社区源码和SeaweedFS，然后再确认最终产品。当前产品选项和影响集中见候选对比第6节。本报告不是最终选型批准。

## 2. 维护与分发事实

| 核查对象 | 2026-10-25实际返回 | 对本项目的含义 |
| --- | --- | --- |
| 官方仓库HTML | HTTP200；归档通知日期2026-04-25；页面当前提交为`7aac2a2c5b7c882e68c1ce017d8256be2feea27f` | 该提交只作为本次可追溯源码读点，不是已批准生产基线 |
| 官方仓库API | HTTP200；`archived=true`、`pushed_at=2026-04-24T17:54:39Z` | 与只读状态相符；不能推导未来安全维护 |
| README | 固定提交HTTP200；停止维护、Source-Only Distribution及历史二进制不再更新的说明仍在 | 不把历史镜像或`latest`当作维护承诺 |
| releases/latest | HTTP200，跳转至`RELEASE.2025-10-15T17-29-55Z`；页面发布时间2025-10-16T19:33:51Z | 标签时间与发布时刻分别记录；该历史发布不是当前维护版本 |
| 固定提交go.mod | `go 1.24.0`，`toolchain go1.24.8` | 仅是该源码声明，未认定此工具链仍适合未来安全构建 |
| 固定提交Dockerfile | 第1行`FROM minio/minio:latest` | 仍有未固定基础镜像；不能直接把此Dockerfile称为可复现、纯源码构建链 |

上述固定提交README、go.mod、LICENSE、Dockerfile及本轮所读3份服务端源码均HTTP200。以下指纹仅识别被读取文件，不代表完整源码、依赖或镜像已审计：

| 固定提交文件 | SHA-256 |
| --- | --- |
| README.md | `aae99b6e35489bb26bfba4290ac567861d123230d1831562b6aee8c1363aead3` |
| go.mod | `673f06144e90bc045f0a20050d2874c52e551be5bfbd70dff6e76b66da0db702` |
| LICENSE | `0d96a4ff68ad6d4b6f1f30f713b18d5184912ba8dd389f86aa7710db079abcb0` |
| Dockerfile | `1a442cc56fe7367a1663345a82d8abe92855573759835aea6cfbee738582f2ef` |

来源：[S1][S2][S3][S4][S5][S6]。没有执行README中的安装或构建命令。

## 3. 许可与SDK边界

社区服务器固定提交LICENSE为AGPL-3.0；官方COMPLIANCE.md要求结合应用实际使用方式判断适用义务。本轮仅识别许可材料，没有作出“闭源平台必须全部开源”或“独立部署即无任何义务”的判断。后续选定制品时，需保留许可、修改及对应源码材料，并结合实际组合和分发方式完成核对。[S4][S7]

既有Java底座声明AWS SDK for Java v2 S3 `2.55.5`，该固定版本主项目LICENSE.txt为Apache-2.0；这与MinIO服务器的AGPL许可分别记录。服务器产品不要求平台再引入MinIO Java SDK。本轮未遍历完整依赖树或所有子组件许可，主项目许可不能代替最终制品清单。[S8] 本地源码依据见当前适配方案第2节。

软件许可成本、主机磁盘、网络、独立备份和安全维护工时分别核算；停更源码可获取不等于有免费维护，也不证明总成本为零。

## 4. 能力证据与验证缺口

以下只支持继续设计与后续验证，不是运行通过记录。不得把AIStor商业文档中的功能直接归入本次社区源码。

| 本项目需要 | 一手证据 | 仍需验证 |
| --- | --- | --- |
| S3接入 | 社区README声明S3兼容；既有Java S3客户端支持endpoint及路径式访问 | 特定服务器、SDK、签名、错误映射、长度及超时组合 |
| 私有版本读取 | 固定源码`cmd/object-handlers.go`含版本引用及版本响应头，`cmd/bucket-versioning-handler.go:123`有读取桶版本配置处理器 | 私有策略、版本绑定、无权限拒绝、撤权后停止；游戏不拿存储URL绕过服务端 |
| 条件写与版本参数 | 固定AWS SDK 2.55.5服务模型存在`IfMatch/IfNoneMatch/ChecksumSHA256`及`VersionId/Range`；社区源码也有对应条件分支 | 并发、读写法定数不足、响应丢失、重试后查证；字段存在不能证明故障语义正确 |
| 精确删除与个人数据消退 | 对象处理源码存在版本相关路径 | 删除标记与实际旧版本清理区分；数据库引用、备份窗口及7日/30日规则共同验收 |
| 恢复与独立限制记录 | 本轮没有运行证据 | 独立故障域、连续记录覆盖、重放、缺口阻断、RPO15分钟/RTO4小时演练 |

历史issue21603报告读法定数不足时条件PUT语义问题，目前已关闭；PR21653页面标明2025-10-24T04:05:31Z合并，对应提交`18f97e70b19db6b2940ae8a1b14c4665d2eeca36`。[S9][S10] 不能把该历史问题写成“所有当前MinIO均未修复”，也不能仅凭PR合并就说候选源码、历史标签或镜像均含修复。上述历史发布的时间早于该合并；精确候选的包含关系与有效代码路径仍需核实。没有因此启用独立限制日志的CAS能力。

## 5. 后续研究与实施门禁

本轮交付的是官方事实、固定源码读点及适配缺口。没有冻结生产版本、批准自维护责任或替换产品。

OS1比较已完成，当前等待最终产品选择。若继续MinIO社区方向，精确源码、安全修复及构建维护责任仍须落实，不能以本报告替代生产验收；若选择SeaweedFS，其已知限制及验证门禁按候选对比处理。

最终产品方向明确后，仍需在同一物理模型和数据字典补齐存储引用信息，在后续获准实施时验证真实行为。不能以静态源码核查替代编译、存储兼容或恢复验收。

## 6. 一手来源

除明确注明的API限流外，本轮以下页面/源码均已通过只读HTTPS访问；不调用真实存储服务。临时抓取内容不另建逐轮归档。

- [S1] [官方仓库与归档通知](https://github.com/minio/minio)、[官方仓库API](https://api.github.com/repos/minio/minio)。
- [S2] [固定提交README](https://raw.githubusercontent.com/minio/minio/7aac2a2c5b7c882e68c1ce017d8256be2feea27f/README.md)。
- [S3] [官方最新发布跳转入口](https://github.com/minio/minio/releases/latest)。
- [S4] [固定提交LICENSE](https://raw.githubusercontent.com/minio/minio/7aac2a2c5b7c882e68c1ce017d8256be2feea27f/LICENSE)。
- [S5] [固定提交go.mod](https://raw.githubusercontent.com/minio/minio/7aac2a2c5b7c882e68c1ce017d8256be2feea27f/go.mod)。
- [S6] [固定提交Dockerfile](https://raw.githubusercontent.com/minio/minio/7aac2a2c5b7c882e68c1ce017d8256be2feea27f/Dockerfile)。
- [S7] [官方COMPLIANCE.md](https://raw.githubusercontent.com/minio/minio/master/COMPLIANCE.md)。
- [S8] [AWS SDK 2.55.5许可](https://raw.githubusercontent.com/aws/aws-sdk-java-v2/2.55.5/LICENSE.txt)、[S3固定服务模型](https://raw.githubusercontent.com/aws/aws-sdk-java-v2/2.55.5/services/s3/src/main/resources/codegen-resources/service-2.json)。
- [S9] [官方issue21603](https://github.com/minio/minio/issues/21603)、[issue API](https://api.github.com/repos/minio/minio/issues/21603)。时间线API返回403，未据此声称取得合并结果。
- [S10] [官方PR21653](https://github.com/minio/minio/pull/21653)。
- [S11] 固定源码：[对象处理](https://raw.githubusercontent.com/minio/minio/7aac2a2c5b7c882e68c1ce017d8256be2feea27f/cmd/object-handlers.go)、[桶版本配置](https://raw.githubusercontent.com/minio/minio/7aac2a2c5b7c882e68c1ce017d8256be2feea27f/cmd/bucket-versioning-handler.go)、[分片及条件处理](https://raw.githubusercontent.com/minio/minio/7aac2a2c5b7c882e68c1ce017d8256be2feea27f/cmd/erasure-multipart.go)。

SeaweedFS当前有限证据和限制集中见[适配方案第8节](../03-文档/开源组件与对象存储适配方案.md#8-社区维护变化后的当前决策)，尚无其与本项目的兼容性结论。
