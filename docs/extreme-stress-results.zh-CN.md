# 极限压力测试结果

这个仓库现在已经把 Mermaid 运行时本地化，并提供了可复现的截图压测链路。
最新一轮极限压测基于 `examples/extreme-stress/input.json`，执行命令为：

```bash
python3 scripts/run_extreme_stress_test.py
```

## 本轮验证内容

- 超长标题与超长音标在页面中仍能自动换行，没有横向溢出。
- Mermaid 从仓库内置的 `assets/vendor/mermaid.min.js` 渲染，不再依赖 CDN。
- 桌面端截图使用 Playwright Chromium + `chrome` channel。
- 移动端截图使用 Playwright WebKit + `iPhone 14` 设备预设。

## 最新结果摘要

尺寸以 `examples/extreme-stress/results/summary.json` 为准（与文档不一致时以 JSON 为真源）。

| 单词 | 桌面截图 | 移动截图 |
| --- | --- | --- |
| `deinstitutionalization` | `1440×3792` | `1170×13251` |
| `floccinaucinihilipilification` | `1440×4110` | `1170×14307` |
| `honorificabilitudinitatibus` | `1440×4073` | `1170×14013` |
| `otorhinolaryngological` | `1440×3617` | `1170×13086` |
| `psychoneuroendocrinological` | `1440×3683` | `1170×13944` |
| `thyroparathyroidectomized` | `1440×3683` | `1170×13740` |

桌面 channel：`chrome`；移动设备：`iPhone 14`。

## 示例截图

### 桌面端

![Desktop stress sample](../examples/extreme-stress/results/screenshots/desktop/word_card_floccinaucinihilipilification.png)

### 移动端

![Mobile stress sample](../examples/extreme-stress/results/screenshots/mobile/word_card_floccinaucinihilipilification.mobile.png)

## 产物位置

- 输入集：`examples/extreme-stress/input.json`
- HTML：`examples/extreme-stress/results/html`
- 截图：`examples/extreme-stress/results/screenshots`
- 机器可读摘要：`examples/extreme-stress/results/summary.json`
