#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把新一期卡片插入 review.html 索引页。

用法：
  python3 update_review.py <期号> <分类名或key> [新分类名]

  分类名/key：皮肤与屏障(skin) 关节、肌肉与筋膜(joint) 大脑与神经(brain)
              消化与代谢(gut) 免疫与过敏(immune) 五官(face) 激素与情绪(hormone)
              吃对厨房(food) 肠道菌群(microbe) 呼吸与运动(move)
  若分类不存在：自动新建章节（加配色、图例链接、新章节块），直接传新分类名即可。
"""
import os, re, sys, io

BASE = os.path.dirname(os.path.abspath(__file__))
REVIEW = os.path.join(BASE, "review.html")

CATS = [
    ("skin",    "皮肤与屏障",       "--skin"),
    ("joint",   "关节、肌肉与筋膜", "--joint"),
    ("brain",   "大脑与神经",       "--brain"),
    ("gut",     "消化与代谢",       "--gut"),
    ("immune",  "免疫与过敏",       "--immune"),
    ("face",    "五官",             "--face"),
    ("hormone", "激素与情绪",       "--hormone"),
    ("food",    "吃对厨房",         "--food"),
    ("microbe", "肠道菌群",         "--microbe"),
    ("move",    "呼吸与运动",       "--move"),
]
NAME_TO_KEY = {name: key for key, name, _ in CATS}
KEY_TO_NAME = {key: name for key, name, _ in CATS}
KEY_TO_VAR  = {key: var  for key, _, var  in CATS}
# 新分类备用配色（避开已用色）
NEW_COLORS = ["#C97B84", "#7FA8C7", "#B59A7A", "#8FBFA8", "#C7A7B0", "#A8C77E"]

def extract_title_hook(issue_num):
    path = os.path.join(BASE, "issues", f"issue-{issue_num:02d}.html")
    html = io.open(path, encoding="utf-8").read()
    title = re.search(r"<h1>(.*?)</h1>", html, re.S).group(1).strip()
    m = re.search(r'<p class="(?:hook|flip)">(.*?)</p>', html, re.S)
    hook = re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else ""
    if not hook:
        raise SystemExit(f"issue-{issue_num} 未找到 .hook/.flip，请检查卡片结构")
    return title, hook

def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    num = int(sys.argv[1])
    cat_arg = sys.argv[2].strip()
    new_name = sys.argv[3].strip() if len(sys.argv) > 3 else None

    title, hook = extract_title_hook(num)
    with io.open(REVIEW, encoding="utf-8") as f:
        html = f.read()

    # 幂等：该期已在索引里就停
    if f"href=\"issues/issue-{num:02d}.html\"" in html:
        raise SystemExit(f"第{num}期已在 review.html 中，无需重复插入")

    # 解析分类
    key = cat_arg if cat_arg in KEY_TO_VAR else NAME_TO_KEY.get(cat_arg)
    if key is None:
        # 新建分类（第 3 参数省略时用第 2 参数作为新分类名）
        new_name = new_name or cat_arg
        used_vars = set(KEY_TO_VAR.values())
        color = next((c for c in NEW_COLORS if c not in used_vars), "#C77E8A")
        var = f"--cat{len(CATS)+1}"
        CATS.append((f"cat{len(CATS)+1}", new_name, var))
        KEY_TO_NAME[CATS[-1][0]] = new_name
        KEY_TO_VAR[CATS[-1][0]] = var
        key = CATS[-1][0]
        # :root 加配色
        html = html.replace("; --food:#E09A5A;",
                            f"; --food:#E09A5A; {var}:{color};")
        # 图例加链接（皮肤注释前的 </div> 是图例闭合，插到它前面）
        legend_start = html.index('  <div class="legend">')
        cm = re.search(r'  </div>\n\n  <!-- 皮肤与屏障 -->', html[legend_start:])
        pos = legend_start + cm.start()
        new_link = (f'    <a href="#cat-{key}"><span class="dot" '
                    f'style="background:var({var})"></span>{new_name}</a>')
        html = html[:pos] + new_link + "\n" + html[pos:]
        # 新章节块（footer 前）
        new_section = (f'\n  <!-- {new_name} -->\n  <div class="cat" id="cat-{key}">\n'
                       f'    <div class="cat-header"><span class="dot" style="background:var({var})"></span>'
                       f'<h2>{new_name}</h2><span class="count">1 期</span></div>\n'
                       f'    <div class="grid">\n'
                       f'      <a class="card" style="border-left-color:var({var})" '
                       f'href="issues/issue-{num:02d}.html"><div class="num">#{num}</div>'
                       f'<div class="title">{title}</div><div class="hook">{hook}</div></a>\n'
                       f'    </div>\n  </div>\n')
        html = html.replace('<div class="footer">', new_section + '<div class="footer">', 1)
        # 全页总数 +1
        html = update_total(html)
        with io.open(REVIEW, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"已新建分类「{new_name}」并插入第{num}期（#{num} {title}）")
        return

    name, var = KEY_TO_NAME[key], KEY_TO_VAR[key]
    # 定位该分类 grid
    m = re.search(r'<div class="cat" id="cat-%s">\s*'
                  r'(<div class="cat-header">.*?</div>)\s*'
                  r'<div class="grid">' % key, html, re.S)
    if not m:
        raise SystemExit(f"review.html 找不到分类 cat-{key}")
    header = m.group(1)
    new_card = (f'      <a class="card" style="border-left-color:var({var})" '
                f'href="issues/issue-{num:02d}.html"><div class="num">#{num}</div>'
                f'<div class="title">{title}</div><div class="hook">{hook}</div></a>')
    # 插到 grid 最顶部（从新到旧）
    insert_at = m.end()
    html = html[:insert_at] + "\n" + new_card + html[insert_at:]
    # 更新该分类计数
    cnt = int(re.search(r'class="count">(\d+) 期</span>', header).group(1)) + 1
    html = html.replace(header, re.sub(r'class="count">\d+ 期</span>',
                                       f'class="count">{cnt} 期</span>', header))
    # 全页总数 +1
    html = update_total(html)
    with io.open(REVIEW, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"已把第{num}期（#{num} {title}）插入「{name}」，该分类现{cnt}期")

def update_total(html):
    def bump(mo):
        return mo.group(0).replace(mo.group(1), str(int(mo.group(1)) + 1))
    html = re.sub(r'<title>养生笔记 · (\d+)期分类索引</title>', bump, html)
    html = re.sub(r'<p class="sub">(\d+) 期 · 按主题分类复习</p>', bump, html)
    return html

if __name__ == "__main__":
    main()
