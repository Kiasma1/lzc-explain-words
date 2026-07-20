# 极限压力测试复现指南

这个仓库现在已经把 Mermaid 运行时本地化，并提供了可复现的截图压测链路。
为减小当前检出后的 Skill 体积，生成证据由 Git 忽略。Git 历史仍包含旧产物；不需要历史时请使用 README 中的浅克隆安装方式。先安装移动端验证所需的浏览器，再从仓库根目录运行套件：

```bash
npm exec --yes --package=playwright -- playwright install webkit
python3 scripts/run_extreme_stress_test.py
```

## 验证约定

- 超长标题与超长音标在页面中仍能自动换行，没有横向溢出。
- Mermaid 从仓库内置的 `assets/vendor/mermaid.min.js` 渲染，不再依赖 CDN。
- 桌面端截图使用 Playwright Chromium + `chrome` channel。
- 移动端截图使用 Playwright WebKit + `iPhone 14` 设备预设。

## 输入与本地产物

- 输入集：`examples/extreme-stress/input.json`
- HTML：`examples/extreme-stress/results/html`
- 截图：`examples/extreme-stress/results/screenshots`
- 机器可读摘要：`examples/extreme-stress/results/summary.json`

视口尺寸和运行元数据以本次生成的 `summary.json` 为准。这些本地产物可随时删除并重新生成。
