# 现有主机部署与 MCP 验收配方

这是候选步骤，不是一键改云端脚本。先核对主机与授权，按环境替换用户、路径及端口。

## 1. 现状与 DNS

读取现有服务及 `ss -ltn`，检查 TCP443 是否占用，记录原防火墙绑定/规则。已有 Caddy 监听时应做站点级审查，不启动第二个抢端口的实例。

权威 NS 核对后，在域名管理器新增测试子域名的 A。只在 IPv6 真正可达时发布 AAAA；同时检查 CAA 是否允许所选 CA。等待权威与客户端解析一致，不承诺固定传播时长。

```sh
dig +short NS example.com
dig +short A mcp.example.com
dig +short AAAA mcp.example.com
dig +short CAA example.com
```

example.com 以及文档网段均为示意，不能用于真实 ACME 签发。注册商无需与云主机供应商相同。证书域名会出现在公开证书透明度记录中，避免把内部名称用于公网签发。

## 2. 后端与边缘

MCP 应用使用官方 SDK，服务回环监听。客户端凭据和管理凭据分开，服务端按凭据建立用户身份，不相信用户自报 tenant_id；校验 Host/Origin（含合理处理无 Origin 的非浏览器客户端）、参数/请求大小，按业务启用速率限制。不向工具暴露任意宿主 shell 或生产管理能力。

下载 Caddy 时从官方源选适合 OS/架构的固定版本，核对发布校验和的**算法和精确资产名**，有签名时按官方验证。不要把 128 位十六进制 SHA512 摘要拿来运行 sha256sum 后当网络故障；校验失败不执行。配方不固定某次历史版本。

```sh
python3 render-caddy.py --domain mcp.example.com --backend-port 18140 --out ./Caddyfile.candidate
caddy validate --config ./Caddyfile.candidate --adapter caddyfile
```

`render-caddy.py` 仅生成单站点候选配置，不修改现有配置、不启动进程、不会申请证书。需要 systemd 时按实际已有用户创建独立 unit，指定准确二进制/工作目录、Restart、资源限额；仅 Caddy 授予绑定低端口所需能力。应用监听回环；管理端口不代理公网。

为 ACME 账号及证书设置服务用户可写的持久私有目录（目录 700 / 文件 600），配置 XDG_DATA_HOME / XDG_CONFIG_HOME 或部署方式对应存储。服务初始化及升级不要删除这些目录。新建仅绑定目标主机的防火墙，在原已授权规则上最小增加 TCP443，不为此批量改共享规则。

443-only 模板显式禁用 HTTP 重定向与 HTTP-01，仅转发 `/mcp/v1`、`/healthz`，其余 404。上游需自身鉴权；模板不实现 Bearer 校验。代理不缓存 MCP、不静默丢弃 Authorization、不跟随跳转给别的域名发送令牌。`flush_interval -1` 适合需要及时传递事件的场景，仍应实测长流与超时；模板的 30s 头部超时不是所有业务默认。

TLS-ALPN-01 需要 CA 连接实际公网443并抵达签发组件，前面已有 L7 TLS 终止时此条件可能不成立。不要通过无界重签碰限流；必要时改为获授权的 DNS-01，并保护最小 DNS API 凭据。泛域名不使用 TLS-ALPN-01。

## 3. 逐层验收

健康检查使用默认 TLS 信任：

```sh
curl --fail --show-error --max-time 15 https://mcp.example.com/healthz
```

用客户端运行时/系统信任检查 SAN、链、有效期和 SNI；必要时 `openssl s_client` 配合主机名验证和失败退出（不同系统参数有差异）。不得将 `curl -k`、关闭 Node 证书验证或浏览器强行继续计为通过。

协议验收使用客户端兼容的官方 MCP SDK；不要只用健康检查。概念顺序：initialize → notifications/initialized → tools/list → 一次只读 tools/call。HTTP Accept 同时允许 application/json 与 text/event-stream；若服务下发 Mcp-Session-Id，后续携带它。GET 可返回405；不同版本与状态管理方式以协商结果为准。

凭据从私有文件/密钥库在进程内注入，不放 URL、命令行参数、输出、截图。分别验证缺失/错误身份被拒，正确身份成功，A/B 不越权。静态 Bearer 是本配方的受控测试方式，不宣称已实现完整 MCP OAuth 授权规范；需要 OAuth 的客户端另行实现。

应用联调再验证：平台凭据库中的 URL 绑定、Session 选择、工具 effect/审批、只读结果、错误可见、重试/幂等，以及响应丢失的 unknown 不重派发。客户端可能要求 DNS/HTTPS/public IP/443/不跳转；这是该平台的 egress 策略，应实测，不删 SSRF 策略来适配服务。

## 4. 清理、续期与报告

清理本轮合成记录、临时 schema，保留操作 ID、审计和故障证据。隔离资格通过与真实模型/环境通过分别记录。服务若交付持续使用则保留，未获停机授权不停止其他项目。

列出仅针对新服务的 `systemctl status/stop/start` 或等价命令、私有配置路径、DNS/防火墙回滚对象。证书自动续期依赖域名、443、CA 出口和持久存储；配置启用不等于真实续期周期已验证。持续运行仍消耗现有主机/网络资源，不宣传“绝对零费用”。
