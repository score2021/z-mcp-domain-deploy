# z-mcp-domain-deploy

把已有主机上的自建 MCP 接到可信 HTTPS 域名：分清实名、ICP备案、DNS、TLS 与实际 MCP 可用性，避免多买跳板机或通过放宽安全策略“跑通”。面向负责自建 MCP、客户接入测试和云部署的开发/测试人员。

## 成果展示

[合成案例的实际 CLI 产物](example-plan.md)展示“境外现有主机＋仅443＋本机管理”的接入方案与分层验收。来源与运行状态见该文件；示意域名和文档网段不能真实签发证书。此仓库不包含原项目实现或实际部署标识。

本 skill 包含离线候选配置生成器；**它不会自动注册域名、申请证书或改云防火墙**。真实实施由使用者的 Agent 按当前权限、环境与授权执行。

## 安装（终端）

依赖：Git、POSIX shell；生成配置/运行脚本测试需 Python 3.10+。实际部署另外需要已有 MCP 服务、受控主机、域名 DNS 权限和适用版本的 Caddy。无需绑定某个云账号或付费模型。

```sh
git clone https://github.com/score2021/z-mcp-domain-deploy.git
cd z-mcp-domain-deploy
sh ./install.sh
```

安装到 `~/.agents/skills/z-mcp-domain-deploy/`，复制必要资源与许可证，遇到已存在目录、文件或断链立即停止，不覆盖。`z-` 是个人检索前缀，不是官方要求。重新打开 Codex 会话后使用 `$z-mcp-domain-deploy`；未实测的其他客户端只提供兼容格式，不保证自动发现。

## 样例

前置条件：已安装本 skill；以下材料全部合成，无需真实 DNS、云账户或密码。这是对话输入，会在当前工作目录生成一份方案和候选配置，不联系示意域名、不变更云资源。

```text
$z-mcp-domain-deploy 请为自建 MCP 出一份可实施方案并生成 Caddy 候选配置。
材料：我已注册并实名 example.com；现有新加坡 Linux 主机，文档示意 IP 为 203.0.113.10。
MCP 已在回环18140运行，Streamable HTTP、Bearer鉴权；管理回环18141。
希望使用 mcp.example.com，公网只允许新增TCP443，不开放80、匿名工具、管理接口；已有共享防火墙和其他服务。
这些域名/IP仅作材料，不访问它们；不运行ACME、不改DNS/防火墙、不购买资源、不读取凭据。
请将地域/ICP备案判断、实施顺序、验收与回滚写到 plan.md；离线生成 Caddyfile.candidate。
```

预期：区分域名实名和 ICP；评估境外直接接入；说明443-only适用前提；保护原服务及共享防火墙；产出候选文件并明确没有真实上线。实际展示不保证模型逐字复现。

只排查时可给出错误文本、已脱敏 DNS/TLS 状态、服务端口和地域，让 Agent 先判断错误发生在哪一层；无需上传域名实名证件或控制台原始截图。

## 流程与边界

- 先确认真实入口/后端地域和客户端约束；“只是测试”不自动免除大陆接入要求。
- 优先复用已有合适主机。仅端口443的 Caddy 配方使用 TLS-ALPN-01；前置 TLS 终止、泛域名等情况需换验证路径。
- 先默认可信 TLS，再协议初始化/发现/只读调用、鉴权/隔离，最后平台联调；GET 405不等于 MCP 故障。
- 真实模型、Sandbox、对象存储、写入故障测试仍按当前授权/预算；不得据本 skill 自动扩权。
- 输出凭据位置，不输出凭据；不用真实业务代码/日志/截图作为公开示例。

## 本地检查

```sh
python3 test_render.py
python3 render-caddy.py --domain mcp.example.com --backend-port 18140 --out ./Caddyfile.candidate
# 在目标 Caddy 已安装且候选未覆盖现有配置时执行：
# caddy validate --config ./Caddyfile.candidate --adapter caddyfile
```

重复生成同一路径会拒绝覆盖。单元检查覆盖主机名/端口与文件边界；不能代替 ACME、网络、鉴权或业务验收。正式发布的客户端实测结果在 `example-plan.md`；本次发布流程不会重新改动真实云部署。

目录：SKILL.md 为入口；domain-and-icp.md、https-and-mcp.md、sources.md 按需读取；Caddyfile.template 与 render-caddy.py 为离线生成器；install.sh 安装；test_render.py、cases.json 和 example-plan.md 用于复验/展示。

许可证：MIT，仅覆盖本仓库原创内容；第三方资料只链接。依据与适用版本见 [sources.md](sources.md)。
