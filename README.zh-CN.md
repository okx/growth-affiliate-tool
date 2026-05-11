# OKX Growth Affiliate Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[English](README.md) | [中文](README.zh-CN.md)

一个远端 MCP（Model Context Protocol）端点，让 AI agent 能用自然语言查询 OKX Affiliate 后台
的业绩、邀请人、邀请链接、子联盟等数据，无需手动拼 API。

> **端点：** `https://www.okx.com/api/v1/mcp/growth-affiliate-mcp`
> **传输：** Streamable HTTP
> **认证：** OAuth 2.0（每个用户独立授权，由 OKX 托管）

## 接入后可以做什么

直接问你的 agent：
- *「看下我近 30 天的 affiliate 业绩」*
- *「本季度佣金前 10 的邀请人是谁？」*
- *「列出我所有邀请链接，按交易者数排序」*
- *「子联盟 `XYZ` 本月表现如何？」*

Agent 自动选工具、执行、用人话回答。

## 快速开始

对应你的客户端，按下面表格找到安装指南。每个指南都是一条命令加 4 步 OAuth 流程。

| 客户端                          | 原生 MCP OAuth | 安装指南                                                     |
| ------------------------------- | :------------: | ------------------------------------------------------------ |
| **Claude Code**（CLI）          | ✅             | [`docs/install/claude-code.md`](docs/install/claude-code.md) |
| **Codex CLI**                   | ✅             | [`docs/install/codex.md`](docs/install/codex.md)             |
| **Hermes**                      | ✅             | [`docs/install/hermes.md`](docs/install/hermes.md)           |
| **Cursor**                      | ✅             | [`docs/install/cursor.md`](docs/install/cursor.md)           |
| **通用 MCP 客户端**             | ✅             | [`docs/install/generic.md`](docs/install/generic.md)         |
| **OpenClaw**                    | ❌（用 skill） | [`docs/install/openclaw.md`](docs/install/openclaw.md)       |

> **OpenClaw 用户请注意：** OpenClaw 内建的 MCP runtime 还不支持 OKX 的非标准 OAuth（必填
> `resource` 参数 + 非 discovery 的 DCR 端点）。在上游支持之前，OpenClaw 用户通过本仓库自带
> 的 skill 安装：[`skills/openclaw-affiliate-mcp/`](skills/openclaw-affiliate-mcp/) —— 一个
> 专门引导 agent 完成 OAuth 流程的 skill pack。

## 授权范围

连接时 OKX 会问你授予哪些权限。**这个 MCP 只需要读权限**，所以推荐默认只勾选
**Live Trading → Read-only**：

| Scope                 | 推荐 | 用途                                                  |
| --------------------- | :--: | ----------------------------------------------------- |
| `live:read`           | ✅   | 下面所有读取工具（业绩/邀请人/链接/子联盟）           |
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
| 5  | `okx-affiliate-sub-affiliate-list`    | MLRS 网络中的子联盟（生涯数据）                    |
| 6  | `okx-affiliate-co-inviter-list`       | 你被列为共同邀请人的渠道                           |

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

## 前置条件

- 一个已开通 **Affiliate** 的 OKX 账号
- 上面表格中的任一**客户端**（或其他 MCP 兼容 agent）
- 浏览器，用于完成一次性 OAuth 授权

仅此而已 —— 不需要安装 SDK，也不需要本地起 server。MCP 由 OKX 托管。

## 授权

[MIT](LICENSE)

## 联系

问题或需求：请在本 repo 提 issue。
