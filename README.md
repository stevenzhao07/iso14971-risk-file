# iso14971-risk-file

> **门户 / Portal:** [LGD Hub · 生态超市入口](https://zhaoxinghua09-cell.github.io/lgd-hub/) ｜ LGD 生态（Lifecycle Governance Doctrine）

> **Contributed by [@stevenzhao07](https://github.com/stevenzhao07) · Independent researcher · Pure technical input, no commercial promotion.**

按 ISO 14971:2019（+ ISO/TR 24971 应用指南）生成风险管理文件骨架：危害登记表、5×5 概率×严重度风险矩阵、可接受性准则、风险控制措施跟踪、剩余风险与受益-风险分析。把「风险管理贯穿生命周期」落成一条命令。

这是 MedXpert 把"医疗 AI 信任"方法论工程化落地的可插拔模块之一——把抽象的合规要求变成一条可重复运行的命令或参考实现。方法论四要素（白话版）：**治理守护者 XCGS** ＝ 为 AI 留下可核验的治理证据；**立法者 A³ Laws** ＝ 给自主系统划权限 / 监督 / 追责三条硬边界；**护照官 AI 护照** ＝ 为模型签发可追溯的身份凭证；**人机共存** ＝ 明确人类与 AI 的分工与兜底。

---

## 可插拔模块契约（lgd-skeleton/1.0）

本仓库是一个 **`lgd-skeleton/1.0` 可插拔模块**：

- **一切即插件**：仅依赖声明式 `module.json`，零配置；
- **按需装（lazy）**：仅 triggers 命中时加载；
- **可嵌套（nested）**：可被 `medical-ai-toolkit` 总入口路由发现；
- **扩展点**：`plugins/`(新增风险源类别：在 HAZARD_CATEGORIES 加一行。)。

机器可发现入口：`AGENTS.md` · `CLAUDE.md` · `llms.txt`。

## 特性

- 风险矩阵：概率 P1–P5 × 严重度 S1–S5，可接受性准则可配置（默认按 ISO 14971 精神）
- 危害登记：add/list 子命令维护危害-处境-伤害三联表
- 控制跟踪：每条风险的控制措施、实施状态、残余 P/S 复评
- 受益-风险结论段自动汇总（不替代评审委员会判定）

**上游投稿目标**：OpenRegulatory/templates

## 内容说明

风险准则（什么算可接受）由制造商自行定义并在文件中声明——本工具默认准则仅为示例起点。ISO/TR 24971 为应用指南，不是标准本体。

## 免责声明

> 品牌状态限定：**MedXpert**（未申请实体注册、未申请商标注册，仅作来源标识）。本仓库由个人以独立研究者（Independent researcher）身份维护，不代表任何机构。

本工具仅提供结构化模板与计算能力，**不构成法规建议、临床建议或产品合规结论**。具体产品的注册、临床评价、灭菌验证、风险分析、软件分级等决策，须由合资格人员依据目标辖区（NMPA / FDA / EU MDR / PMDA）最新法规文本作出；条款与限值以官方发布文本为准。使用本工具产生的一切后果由使用者自行承担。

## 使用

```bash
python scripts/risk_file.py --demo
python scripts/risk_file.py add --hazard '植入物断裂' --p 3 --s 5
```

## 快速开始（30 秒）

```bash
git clone https://github.com/stevenzhao07/iso14971-risk-file.git && cd iso14971-risk-file
python scripts/risk_file.py --demo
```

> 想参与或遇到问题？[提 Issue](https://github.com/stevenzhao07/iso14971-risk-file/issues) · 完整《AI 参与指南》见 [medical-ai-toolkit](https://github.com/stevenzhao07/medical-ai-toolkit)。

## 路由（总入口）

本模块由 **[medical-ai-toolkit](https://github.com/stevenzhao07/medical-ai-toolkit)** 作为 `lgd-skeleton/1.0` 总入口自动路由发现。

## 关联模块

- [design-controls-toolkit](https://github.com/stevenzhao07/design-controls-toolkit)
- [iec62304-software](https://github.com/stevenzhao07/iec62304-software)
- [pms-vigilance](https://github.com/stevenzhao07/pms-vigilance)

## 许可

Apache-2.0 — 见 [LICENSE](./LICENSE)。

## 关联（方法论来源）

- 理念溯源：个人专家关于医疗 AI 信任与治理的公开方法论（个人观点，不构成标准）
- 同账号系列：见 `medical-ai-toolkit` 导航
