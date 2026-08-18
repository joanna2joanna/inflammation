---
name: inflammation
description: [旧版存档·已废弃] 中医/西医双栏格式，仅供查看历史做法
---

> ⚠️ **旧版存档，已废弃，勿用于新卡片。**
> 本文档记录的是「中医/西医双栏」旧格式，已不再使用，只留作参考。
> **做新卡片请用全局 skill**：`~/.claude/skills/inflammation/SKILL.md`（why-card 最新格式，含确认后自动上传网页索引流程）。

当用户提供主题时：

1. 确定 8 个字段：
   钩子标题 ≤7字，单行
   副标题钩子 认知翻转，揭示症状背后的炎症原因
   中医概念 4-5字，单行
   中医描述 2行白话，每行≤11字
   西医概念 4-5字，单行
   西医描述 2行白话，每行≤11字
   卡片标题
   行动×3 what≤20字 + why≤20字

   对齐：双栏概念同行数（1行），描述同行数（2行）。概念76px字号，5字可容6字必换行。

2. 复制 `issues/issue-01.html`，替换内容，CSS 不动。

3. 截图：`NODE_PATH=/Users/joanna/.workbuddy/binaries/node/workspace/node_modules node screenshot.js issues/issue-XX.html issues/issue-XX.png`

4. 更新 README 选题表（追加 `| N | 标题 | 钩子 | ✅ |`）。

5. 更新网页索引 `review.html`，把新卡插到对应分类最顶部（从新到旧）：
   `python3 update_review.py <期号> <分类名>`
   分类名：皮肤与屏障 / 关节、肌肉与筋膜 / 大脑与神经 / 消化与代谢 / 免疫与过敏 / 五官 / 激素与情绪 / 吃对厨房 / 肠道菌群 / 呼吸与运动。
   主题都不搭就开新分类：`python3 update_review.py <期号> <新分类名>`。
   脚本自动：插卡到分类顶部、更新该分类期数、更新全页期数（标题+副标题）；新分类自动加配色、图例链接、新章节。

  用户确认后自动上传：`cd /Users/joanna/Projects/inflammation && git add -A && git commit -m "第N期：标题" && git push`（Pages 自动部署到 https://joanna2joanna.github.io/inflammation/ ）

口吻：李大妈大白话，不堆术语。口语化不等于俗套话，避用粗俗直白词。钩子要有认知翻转，每条行动解释 why。
