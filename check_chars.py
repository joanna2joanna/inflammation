#!/usr/bin/env python3
"""炎症系列字数自检 — 生成/修改 HTML 后跑一遍
用法：python3 check_chars.py issues/issue-XX.html"""

import re, sys, os

def check(field, text, max_n, min_n=0):
    n = len(text)
    ok = min_n <= n <= max_n if min_n else n <= max_n
    icon = "✅" if ok else "❌"
    lim = f"≤{max_n}" if not min_n else f"{min_n}-{max_n}"
    print(f"  {icon} {field}: [{text}]  {n}字  ({lim})")
    return ok

def main(path):
    with open(path) as f:
        html = f.read()

    n = re.search(r'issue-(\d+)', os.path.basename(path))
    num = n.group(1) if n else "?"
    print(f"========== #{num} 字数自检 ==========\n")

    ok = True

    # 钩子标题
    m = re.search(r'<h1>(.+?)</h1>', html)
    title = m.group(1) if m else ""
    ok &= check("钩子标题", title, 7)
    print()

    # 中医/西医概念
    concepts = re.findall(r'<div class="concept">(.+?)</div>', html)
    tcm_c = concepts[0] if len(concepts) > 0 else ""
    west_c = concepts[1] if len(concepts) > 1 else ""
    ok &= check("中医概念", tcm_c, 5)
    print()
    ok &= check("西医概念", west_c, 5)
    print()

    # 中医/西医描述
    descs = re.findall(r'<div class="desc">(.+?)</div>', html)
    tcm_pre, tcm_d1, tcm_d2 = "", "", ""
    west_pre, west_d1, west_d2 = "", "", ""
    if len(descs) > 0:
        raw = descs[0]
        # 注意: HTML 中是 <br> 不是 <br/>
        parts = re.split(r'<br\s*/?>', raw)
        tcm_d1 = parts[0].strip() if len(parts) > 0 else ""
        tcm_d2 = parts[1].strip() if len(parts) > 1 else ""
    if len(descs) > 1:
        raw = descs[1]
        parts = re.split(r'<br\s*/?>', raw)
        west_d1 = parts[0].strip() if len(parts) > 0 else ""
        west_d2 = parts[1].strip() if len(parts) > 1 else ""

    ok &= check("中医描述行1", tcm_d1, 11)
    ok &= check("中医描述行2", tcm_d2, 11)
    print()
    ok &= check("西医描述行1", west_d1, 11)
    ok &= check("西医描述行2", west_d2, 11)
    print()

    # what ×3
    whats = re.findall(r'<div class="what">(.+?)</div>', html)
    print("-- what --")
    for i, w in enumerate(whats, 1):
        ok &= check(f"what{i}", w, 20)
    print()

    # why ×3
    whys = re.findall(r'<div class="why">(.+?)</div>', html)
    print("-- why --")
    for i, w in enumerate(whys, 1):
        ok &= check(f"why{i}", w, 20)

    print(f"\n========== 结果 ==========")
    if ok:
        print("全部通过 ✅")
    else:
        print("⚠️  有超标的，修完重新跑")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 check_chars.py issues/issue-XX.html")
        sys.exit(2)
    main(sys.argv[1])
