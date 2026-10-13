# AGENTS.md · iso14971-risk-file

> 机器可发现入口（AI 编码代理 / Codex / Claude / Cursor）。单一事实源：本文件。

## 这是什么
按 ISO 14971:2019（+ ISO/TR 24971 应用指南）生成风险管理文件骨架：危害登记表、5×5 概率×严重度风险矩阵、可接受性准则、风险控制措施跟踪、剩余风险与受益-风险分析。把「风险管理贯穿生命周期」落成一条命令。

## 运行
```bash
python scripts/risk_file.py --demo
python scripts/risk_file.py --help
```

## 扩展契约（lgd-skeleton/1.0）
- **一切即插件**：仅依赖声明式 `module.json`，零配置。
- **按需装（lazy）**：仅 triggers 命中时加载。
- **可嵌套（nested）**：可被 `medical-ai-toolkit` 总入口路由。
- **扩展点**：`plugins/`(新增风险源类别：在 HAZARD_CATEGORIES 加一行。)

## 红线
纯技术贡献，不含商业营销；MedXpert 仅作为贡献者署名（@stevenzhao07）。
