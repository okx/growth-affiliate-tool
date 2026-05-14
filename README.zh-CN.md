# OKX Growth Affiliate Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[English](README.md) | [中文](README.zh-CN.md)

OKX 节点 MCP（Model Context Protocol），让 AI agent 能用自然语言查询 OKX 节点后台的
返佣数据、邀请人、邀请链接、子节点等数据。

<p align="center">
  <img src="docs/videos/affiliatemcp-promo-zh.gif" alt="60 秒宣传演示" width="720"/>
</p>

> **端点：** `https://www.okx.com/api/v1/mcp/growth-affiliate-mcp`
> **传输：** Streamable HTTP
> **认证：** OAuth 2.0（每个用户独立授权，由 OKX 托管）

## 使用示例

用自然语言提问，agent 自动选工具、调 MCP、用人话回答（以下 UID 与数字仅示意）：

```
你    ❯ 看下昨日数据

Agent ❯ 📊 佣金 $350（比 7 日均值低 30%）。成交 $3.5M。新邀 6 人。
        Top 3：UID …A1B2  $91  VIP2
               UID …C3D4  $50  VIP1
               UID …E5F6  $28  Regular  ← 该升 VIP1
        ⚠️ 3 人今日入金 $1.8K 但 0 交易，今天就要救。
```

```
你    ❯ 这周该联系谁？

Agent ❯ 🎯 33 个候选，4 个优先级：
        🔥 新邀明星（加入 <7 天已产出）：     UID …N1P2、…Q3R4
        🐋 Regular 做着鲸鱼量 → 推 VIP1：     UID …S5T6、…U7V8、…W9X0
        ⚠️ 大额入金未激活：                    UID …Y1Z2（$10K 闲置 8 天）
        🆕 KYC 完成但未入金：                  本周 13 个
```

```
你    ❯ 哪些鲸鱼在流失？

Agent ❯ ⚠️ 生涯前 50 用户里只有 23 个还在活跃。
        🔴 已套现：  UID …K1L2（生涯 $104K / 已提走 $10M 入金的 95%）
        🟡 资金还在：UID …M3N4（生涯 $26K / 94% 仍在平台）← 最易挽回
        🟠 渐进衰退：UID …P5Q6（生涯 $18K / 近 30 天 0 成交）
        风险 LTV 合计：$208K（≈ 节点 12 个月佣金的 46%）。
```

## 快速开始

对应你的客户端，按下面表格找到安装指南。每个指南都是一条命令加 4 步 OAuth 流程。

| 客户端                          | 原生 MCP OAuth | 安装指南                                                     |
| ------------------------------- | :------------: | ------------------------------------------------------------ |
| **Claude Code**（CLI）          | ✅             | [`docs/install/claude-code.md`](docs/install/claude-code.md) |
| **Codex CLI**                   | ✅             | [`docs/install/codex.md`](docs/install/codex.md)             |
| **Hermes Agent**                | ❌（用 skill） | [`docs/install/hermes.md`](docs/install/hermes.md)           |
| **OpenClaw**                    | ❌（用 skill） | [`docs/install/openclaw.md`](docs/install/openclaw.md)       |

> **Hermes / OpenClaw 用户请注意：** 这两个客户端内建的 MCP runtime 都还不支持 OKX 的非标准
> OAuth（必填 `resource` 参数 + 非 discovery 的 DCR 端点）。在上游支持之前，它们通过本仓库自
> 带的 skill 安装：[`skills/hermes-affiliate-mcp/`](skills/hermes-affiliate-mcp/) 和
> [`skills/openclaw-affiliate-mcp/`](skills/openclaw-affiliate-mcp/) —— 引导 agent 完成
> OAuth 流程的 skill pack。

## 授权范围

连接时 OKX 会问你授予哪些权限。**这个 MCP 只需要读权限**，所以推荐默认只勾选
**Live Trading → Read-only**：

| Scope                 | 推荐 | 用途                                                  |
| --------------------- | :--: | ----------------------------------------------------- |
| `live:read`           | ✅   | 下面所有读取工具（业绩/邀请人/链接/子节点）           |
| `live:trade`          | ❌   | 下单/改单/撤单 —— 本 MCP 不用                         |
| `live:earn`           | ❌   | Earn 申购 —— 本 MCP 不用                              |
| `live:asset_transfer` | ❌   | 资金划转 —— 本 MCP 不用                               |
| `demo:*`              | ❌   | 模拟盘 —— 本 MCP 不用                                 |

之后想加 scope 重新跑 `/mcp`（或你 agent 的等效命令）即可。

## 工具一览

| #  | 工具名                                | 用途                                              |
| -- | ------------------------------------- | ------------------------------------------------- |
| 1  | `okx-affiliate-performance-summary`   | 聚合业绩指标——邀请人/入金/交易量/佣金，按现货/合约/BSC 拆分 |
| 2  | `okx-affiliate-invitee-list`          | 邀请人分页列表，含入金、交易、KYC                  |
| 3  | `okx-affiliate-invitee-detail`        | 按 UID 查单个邀请人详情                            |
| 4  | `okx-affiliate-link-list`             | 邀请链接 + 佣金比例 + 累计数据（含 24 小时佣金）   |
| 5  | `okx-affiliate-sub-affiliate-list`    | MLRS 网络中的子节点（生涯数据）                    |
| 6  | `okx-affiliate-co-inviter-list`       | 助力人分析                                         |

完整参数和返回字段 → [`docs/tools-reference.md`](docs/tools-reference.md)。

## 文档

| 文档                                                           | 内容                                                |
| -------------------------------------------------------------- | --------------------------------------------------- |
| [工具参考](docs/tools-reference.md)                            | 每个工具的所有参数和返回字段                        |
| [使用示例](docs/usage-examples.md)                             | 自然语言提问示例                                    |
| [`periodType` 速查表](docs/period-type.md)                     | 8 种时间窗口代码                                    |
| [FAQ](docs/faq.md)                                             | Token 过期、400 错误、scope 不匹配、常见坑          |
| [Agent 安装引导](INSTALL.md)                                   | 给 AI agent 端到端读的决策树                        |
| [Skill 索引](skills/README.md)                                 | 给需要自定义 OAuth 处理的 runtime 用的 skill 列表    |
| [**使用场景**](examples/README.md)                             | 常见分析任务的 skill 包（日报、流失救援、潜力用户等）|

## 前置条件

- 一个已开通 **Affiliate** 的 OKX 账号
- 上面表格中的任一**客户端**（或其他 MCP 兼容 agent）
- 浏览器，用于完成一次性 OAuth 授权

仅此而已 —— 不需要安装 SDK，也不需要本地起 server。MCP 由 OKX 托管。

## 授权

[MIT](LICENSE)

## 联系

问题或需求：请在本 repo 提 issue。
