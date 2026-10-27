# Backend

后端工程目录。

## 目录

| 目录 | 说明 | 来源 |
|---|---|---|
| `yudao-boot-mini/` | 芋道 Spring Boot 单体版（精简版），实际在用的后端 | https://gitee.com/yudaocode/yudao-boot-mini ，分支 `master-jdk17` |

## 技术栈

- JDK 17、Spring Boot 3.5.15、Maven 聚合工程（`cn.iocoder.boot:yudao`，`revision=2026.09-SNAPSHOT`）
- MyBatis-Plus + Druid（多数据源）、Redis（Redisson）、Quartz
- 已启用模块：`yudao-module-system`、`yudao-module-infra`
- 未启用（根 pom 中注释）：member / bpm / report / mp / pay / mall / crm / erp / iot / mes / wms / hrm / fms / pms / oa / im / ai

## 启动

见 [前后端项目启动规则.md](../docs/10-项目规则/前后端项目启动规则.md)。启动模块：`yudao-boot-mini/yudao-server`，主类 `cn.iocoder.yudao.server.YudaoServerApplication`，端口 `48080`。
