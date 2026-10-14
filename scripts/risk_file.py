#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
risk_file.py — ISO 14971 风险管理文件生成器
============================================
按 ISO 14971:2019（+ ISO/TR 24971 应用指南）生成风险管理文件骨架：
  危害登记（hazard / sequence of events / hazardous situation / harm）
  5×5 风险矩阵（概率 P1–P5 × 严重度 S1–S5）与可接受性准则
  风险控制措施跟踪（措施 / 状态 / 残余 P,S）
  剩余风险 + 受益-风险结论汇总

诚实边界：可接受性准则由制造商自行定义并在文件中声明，
本工具默认准则仅为示例起点（ISO 14971 要求「风险可接受性准则」成文）。
"""
from __future__ import annotations
import argparse
import json
import os
import sys

DB_FILE = "risk_register.json"

# 概率 P1–P5 / 严重度 S1–S5（ISO 14971 术语：probability of occurrence of harm）
PROB = {
    "P1": "频繁（frequent）",
    "P2": "很可能（probable）",
    "P3": "偶尔（occasional）",
    "P4": "很少（remote）",
    "P5": "不可能（improbable）",
}
SEV = {
    "S1": "可忽略（negligible）",
    "S2": "轻微（minor）",
    "S3": "中度（moderate）",
    "S4": "严重（serious）",
    "S5": "灾难性（catastrophic，死亡/永久损害）",
}

# 默认可接受性准则（示例）：乘积 ≥ 15 → 不可接受（必须控制）
def default_criteria(pn: int, sn: int) -> str:
    score = pn * sn
    if score >= 15:
        return "不可接受（intolerable）→ 必须风险控制"
    if score >= 8:
        return "合理可行降低（ALARP）→ 控制并复评"
    return "可接受（acceptable）→ 记录并监视"


def risk_level(pn: int, sn: int) -> str:
    score = pn * sn
    if score >= 15:
        return "高"
    if score >= 8:
        return "中"
    return "低"


def load_db(repo_root: str) -> dict:
    p = os.path.join(repo_root, DB_FILE)
    if os.path.isfile(p):
        try:
            with open(p, encoding="utf-8") as f:
                db = json.load(f)
        except (ValueError, OSError) as e:
            raise ValueError(f"{DB_FILE} 不是合法 JSON 风险台账: {e}")
        if not isinstance(db, dict) or not isinstance(db.get("risks", []), list):
            raise ValueError(f"{DB_FILE} 结构非法：应为 {{\"risks\": [...]}}")
        return db
    return {"risks": []}


def save_db(repo_root: str, db: dict) -> None:
    json.dump(db, open(os.path.join(repo_root, DB_FILE), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)


def add_risk(repo_root: str, hazard: str, pn: int, sn: int,
             situation: str = "", harm: str = "") -> dict:
    if not (1 <= pn <= 5 and 1 <= sn <= 5):
        raise ValueError("P/S 须为 1–5")
    db = load_db(repo_root)
    # 2026-10-12 复审修复：原 rid=R-{len+1} 在有条目缺口（删过条目）时会撞号；
    # 改为取现有最大编号 +1。
    nums = [int(r["id"][2:]) for r in db["risks"]
            if str(r.get("id", "")).startswith("R-") and r["id"][2:].isdigit()]
    rid = f"R-{(max(nums) + 1) if nums else 1:03d}"
    row = {
        "id": rid, "hazard": hazard, "situation": situation, "harm": harm,
        "P": pn, "S": sn,
        "level": risk_level(pn, sn),
        "criteria": default_criteria(pn, sn),
        "controls": [], "residual_P": None, "residual_S": None,
    }
    db["risks"].append(row)
    save_db(repo_root, db)
    return row


def add_control(repo_root: str, rid: str, measure: str,
                rp: int | None = None, rs: int | None = None) -> dict:
    db = load_db(repo_root)
    for r in db["risks"]:
        if r["id"] == rid:
            r["controls"].append({"measure": measure, "status": "planned"})
            if rp and rs:
                r["residual_P"], r["residual_S"] = rp, rs
            save_db(repo_root, db)
            return r
    raise KeyError(f"未找到风险 {rid}")


def render_report(repo_root: str) -> str:
    db = load_db(repo_root)
    lines = ["# 风险管理文件（ISO 14971 骨架）", "",
             "> 由 risk_file.py 生成；可接受性准则为示例默认值，制造商须成文声明自己的准则。",
             "", "## 1. 风险可接受性准则（示例）", "",
             "| 概率\\严重度 | S1 | S2 | S3 | S4 | S5 |",
             "|---|---|---|---|---|---|"]
    for pn in range(1, 6):
        row = [f"P{pn}"]
        for sn in range(1, 6):
            row.append(risk_level(pn, sn))
        lines.append("| " + " | ".join(row) + " |")
    lines += ["", "## 2. 风险分析（P×S 矩阵）", "",
              "| ID | 危害 | 危险处境 | 伤害 | P | S | 初始等级 | 准则判定 |",
              "|---|---|---|---|---|---|---|---|"]
    for r in db["risks"]:
        lines.append(f"| {r['id']} | {r['hazard']} | {r.get('situation','')} | "
                     f"{r.get('harm','')} | P{r['P']} | S{r['S']} | {r['level']} | {r['criteria']} |")
    lines += ["", "## 3. 风险控制措施与剩余风险", "",
              "| ID | 措施 | 残余 P/S | 残余等级 |", "|---|---|---|---|"]
    for r in db["risks"]:
        for c in r["controls"]:
            rp, rs = r.get("residual_P"), r.get("residual_S")
            lv = risk_level(rp, rs) if rp and rs else "待复评"
            lines.append(f"| {r['id']} | {c['measure']} | "
                         f"{'P'+str(rp)+'/S'+str(rs) if rp and rs else '—'} | {lv} |")
    high = [r for r in db["risks"] if r["level"] == "高"]
    lines += ["", "## 4. 综合剩余风险与受益-风险结论", "",
              f"- 高风险项：{len(high)} 项（{', '.join(r['id'] for r in high) or '无'}）",
              "- 结论须由风险管理委员会评审形成；本表仅汇总输入。", ""]
    return "\n".join(lines)


def _demo() -> int:
    print("ISO 14971 风险管理文件生成器 · 演示（不落盘）\n")
    print("风险可接受性准则（示例）：P×S ≥15 不可接受；≥8 ALARP；<8 可接受\n")
    print(f"{'ID':6}{'危害':28}{'P':3}{'S':3}{'等级':6}判定")
    demo = [("植入物断裂", 3, 5), ("标签语种缺失", 2, 3), ("无菌屏障破损", 2, 5)]
    for i, (h, p, s) in enumerate(demo, 1):
        print(f"R-{i:03d}  {h:28}P{p:<2}S{s:<2}{risk_level(p, s):6}{default_criteria(p, s)}")
    print("\n[demo] 落盘用法: python scripts/risk_file.py add --hazard '植入物断裂' --p 3 --s 5")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="ISO 14971 风险管理文件生成器")
    ap.add_argument("--demo", action="store_true", help="跑内置演示")
    ap.add_argument("--selftest", action="store_true", help="跑内置自测（断言 + 负对照 + xfail）")
    sub = ap.add_subparsers(dest="cmd")
    a = sub.add_parser("add", help="登记危害")
    a.add_argument("--hazard", required=True)
    a.add_argument("--p", type=int, required=True, choices=range(1, 6))
    a.add_argument("--s", type=int, required=True, choices=range(1, 6))
    a.add_argument("--situation", default="")
    a.add_argument("--harm", default="")
    c = sub.add_parser("control", help="加控制措施")
    c.add_argument("--id", required=True)
    c.add_argument("--measure", required=True)
    c.add_argument("--rp", type=int, choices=range(1, 6))
    c.add_argument("--rs", type=int, choices=range(1, 6))
    ap.add_argument("--report", action="store_true", help="输出风险管理文件 Markdown")
    args = ap.parse_args()
    if getattr(args, "selftest", False):
        return _selftest()
    root = os.getcwd()

    if args.demo:
        return _demo()
    try:
        if args.cmd == "add":
            r = add_risk(root, args.hazard, args.p, args.s, args.situation, args.harm)
            print(f"[added] {r['id']} {r['hazard']} P{r['P']}×S{r['S']} → {r['level']}（{r['criteria']}）")
            return 0
        if args.cmd == "control":
            r = add_control(root, args.id, args.measure, args.rp, args.rs)
            print(f"[control] {r['id']} 措施已记录（{len(r['controls'])} 项）")
            return 0
        if args.report:
            print(render_report(root))
            return 0
    except KeyError as e:
        msg = e.args[0] if e.args else "未知风险条目"
        print(f"[error] {msg}；先用 add 登记，或 --report 查看现有条目。", file=sys.stderr)
        return 2
    except ValueError as e:
        print(f"[error] {e}", file=sys.stderr)
        return 2
    ap.print_help()
    return 2


# ==================== 内置自测（--selftest） ====================
# 由 conformance 补丁于 2026-10-14 生成（生成器 v2）。
# 特性：端到端 CLI 调用 + 内容断言 + 负对照 + xfail（已知缺陷显式标注，不掩盖）。
_SELFTEST_CASES = [(['--demo'], 0, ['P', 'S'], [], None), (['--report'], 0, ['风险'], [], None), (['control', '--id', 'R-999', '--measure', 'x'], 2, [], [], None), (['add', '--hazard', 'x', '--p', '9', '--s', '1'], 2, [], [], None)]


def _selftest() -> int:
    import os as _os
    import subprocess as _sp
    _here = _os.path.dirname(_os.path.abspath(__file__))
    # 仓库根：脚本位于 <repo>/scripts/ 时取上一级；否则取脚本所在目录
    _root = _os.path.dirname(_here) if _os.path.basename(_here) == "scripts" else _here
    _script = _os.path.abspath(__file__)
    _fail, _xfail, _n = [], [], 0
    for _case in _SELFTEST_CASES:
        _args, _rc, _must, _mustnot = _case[0], _case[1], _case[2], _case[3]
        _reason = _case[4] if len(_case) > 4 else None
        _n += 1
        _p = _sp.run([sys.executable, _script] + _args, capture_output=True, cwd=_root)
        _out = _p.stdout.decode("utf-8", "replace")
        _bad = []
        if _p.returncode != _rc:
            _bad.append(f"rc={_p.returncode} 期望 {_rc}")
        for _m in _must:
            if _m not in _out:
                _bad.append(f"输出缺少 {_m!r}")
        for _m in _mustnot:
            if _m in _out:
                _bad.append(f"输出含禁止内容 {_m!r}")
        if _rc == 0 and not _out.strip():
            _bad.append("rc=0 但输出为空（假绿）")
        if _bad:
            if _reason:
                _xfail.append(f"xfail args={_args}：{'；'.join(_bad)} ← 已知缺陷：{_reason}")
            else:
                _fail.append(f"args={_args}：{'；'.join(_bad)}")
    # 通用负对照：未知参数必须非零
    _n += 1
    _p = _sp.run([sys.executable, _script, "--__nonexistent_flag__"], capture_output=True, cwd=_root)
    if _p.returncode == 0:
        _fail.append("负对照失败：未知参数竟返回 0")
    for _x in _xfail:
        print("[selftest][xfail] " + _x)
    if _fail:
        print(f"[selftest] FAILED {len(_fail)}/{_n}")
        for _f in _fail:
            print("  - " + _f)
        return 1
    print(f"[selftest] PASS {_n - len(_xfail)}/{_n}（含负对照；xfail {len(_xfail)} 项为已知缺陷）")
    return 0


if __name__ == "__main__":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    raise SystemExit(main())
