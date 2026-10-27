# Frontend

前端工程目录。

## 目录

| 目录 | 说明 | 来源 |
|---|---|---|
| `yudao-ui-admin-vue3/` | 管理后台（Vue3 + Vite + element-plus + TypeScript） | https://gitee.com/yudaocode/yudao-ui-admin-vue3 ，分支 `master` |

> 小程序端（`yudao-mall-uniapp`）已按业务要求移除。

## 启动

见 [前后端项目启动规则.md](../docs/10-项目规则/前后端项目启动规则.md)。

```bash
cd yudao-ui-admin-vue3
corepack pnpm@10 install    # 必须 pnpm 10，全局 pnpm 8 会降级 lockfile
corepack pnpm@10 dev        # 端口 5173
```

访问 http://127.0.0.1:5173 ，账号 `admin / admin123`，租户「芋道源码」。

⚠️ 端口与自动开浏览器由未跟踪的本地覆盖层 `.env.env.local` 控制（`VITE_PORT=5173`、`VITE_OPEN=false`），重新 clone 后需重建。
