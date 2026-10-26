# 官方来源与适用范围

核对日期：2026-10-26。执行时再次核对当前文档、云地域及目标客户端版本，不据历史页面保证未来规则。

- [阿里云：ICP filing and DNS resolution](https://www.alibabacloud.com/help/en/dns/icp-and-dns)：大陆/境外托管与备案、DNS 的区别。本文只作接入路线判断，不代替对具体服务类型的监管认定。
- [Caddy Automatic HTTPS](https://caddyserver.com/docs/automatic-https)：ACME、TLS-ALPN、持久化与自动续期。
- [Caddy TLS directive](https://caddyserver.com/docs/caddyfile/directives/tls)：issuer、关闭 HTTP challenge 等语法。
- [Caddy Global options](https://caddyserver.com/docs/caddyfile/options)：关闭管理 API、HTTP 重定向、协议配置。
- [MCP Streamable HTTP（2025-06-18 固定版本）](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports)：初始化、HTTP 请求、Origin 与会话语义。选择固定参考版不表示它是当前最新协议；部署以客户端/SDK支持版本为准。
- [MCP 官方 TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)：选择匹配版本，不自行重写协议栈。
- [Codex Skills](https://learn.chatgpt.com/docs/build-skills)：技能发现与安装位置，客户端版本差异需实测。

来源说明：本 skill 的决策规则和候选配置为本次独立创作，以真实操作经验为背景，用合成材料重新组织。没有复制原 MCP 应用、公司项目代码、数据库 schema、云账号截图、客户数据或原始日志；链接不表示复制第三方源代码或许可证。
