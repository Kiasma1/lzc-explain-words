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

| 单词 | 桌面截图 | 移动截图 |
| --- | --- | --- |
| `deinstitutionalization` | `1440×3101` | `1170×10164` |
| `floccinaucinihilipilification` | `1440×3101` | `1170×10431` |
| `honorificabilitudinitatibus` | `1440×3101` | `1170×10287` |
| `otorhinolaryngological` | `1440×3003` | `1170×9996` |
| `psychoneuroendocrinological` | `1440×3068` | `1170×10623` |
| `thyroparathyroidectomized` | `1440×3068` | `1170×10491` |

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
