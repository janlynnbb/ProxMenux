# ProxMenux Stable v1.2.6 简体中文本地化

本分支基于官方 Stable 标签 `v1.2.6`（提交 `5b41cbfbe8bddcb7e2f1a597812765255fdba448`），只新增 `zh-CN` 语言目录及语言注册，不修改英文源键或菜单业务逻辑。

## 包含内容

- CLI/TUI：`lang/zh-CN.json`，提供主菜单、VM/LXC、存储、网络、PCI/GPU/IOMMU/SR-IOV、备份恢复、监控、通知、设置和确认/错误提示等核心中文条目；其余已接入 `translate()` 的字符串安全回退为英语原文。
- 安装器：标准安装器、Beta 安装器和运行时“Change Language”菜单均加入 `zh-CN / 简体中文`。
- Monitor WebUI：`AppImage/messages/zh-CN/common.json`、类型化语言注册、消息目录注册以及浏览器 `zh-CN` / `zh-Hans` / `zh` 自动识别。
- 回退：CLI 缺失项维持英语原文；Monitor 按 `zh-CN → en → key` 回退。语言包不在用户主机运行时联网翻译。

## 应用补丁

在干净的官方 `v1.2.6` 检出目录中执行：

```bash
git apply --check proxmenux-v1.2.6-zh-CN.patch
git apply proxmenux-v1.2.6-zh-CN.patch
```

然后按官方文档运行安装器。安装菜单选择 `zh-CN / 简体中文`，已安装系统可在 `Settings → Change Language` 中切换。Monitor 会根据浏览器偏好自动选择简体中文，也可在 Monitor Settings 中手动选择。

## 在线安装本分支

在 **PVE 宿主机的 Shell 或 SSH** 中以 `root` 执行。该命令固定从本分支克隆代码，不会改写 GitHub 的 `main` 分支：

```bash
PROXMENUX_REPO_URL='https://github.com/janlynnbb/ProxMenux.git' \
PROXMENUX_REPO_BRANCH='zh-cn-localization' \
bash -c "$(curl -fsSL https://raw.githubusercontent.com/janlynnbb/ProxMenux/zh-cn-localization/install_proxmenux.sh)"
```

完成后输入 `menu` 启动；安装器中选择 `zh-CN / 简体中文`。升级同一中文分支时，重复上面的命令即可。不要在安装后的菜单中切换到 Beta/Develop 发布通道，否则会回到上游渠道。

## 可重复验证

```bash
python3 tools/validate_zh_cn.py
bash -n install_proxmenux.sh install_proxmenux_beta.sh scripts/menus/config_menu.sh
git diff --check
(cd AppImage && npm ci --legacy-peer-deps && npm run build)
```

`npm ci` 需要 `--legacy-peer-deps`，原因是官方锁定的 `vaul@0.9.9` 声明 React 18 peer dependency，而当前锁文件解析 React 19；此选项没有改动项目依赖。

## 已知限制与未覆盖项

语言键缺失清单、英语回退/通用术语清单由 `tools/validate_zh_cn.py` 生成至 `reports/zh-CN-validation.json` 和 `reports/zh-CN-english-fallback.md`。缺失项将安全显示英语原文；其中包含协议名、产品名、路径、单位、命令和部分上游硬编码文本，不能简单等同于漏译。

少量上游 shell 脚本仍直接调用 `dialog` / `whiptail` 或直接 `echo` 文本，未经过 `translate()`。为保持此本地化提交小且可上游合并，本提交未将其批量重构；建议上游后续把这些字符串逐步接入现有 `translate()` 包装器。静态扫描结果和具体文件范围见 `reports/zh-CN-uncovered-hardcoded-strings.md`。

未在本隔离环境上安装或启动 Proxmox VE，也未连接任何用户 PVE；因此没有做真实宿主机安装、systemd 服务或硬件操作验证。
