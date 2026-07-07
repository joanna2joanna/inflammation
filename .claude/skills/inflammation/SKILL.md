---
name: inflammation
description: 制作「李大妈的生活化抗炎笔记」小红书贴图
---

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

4. 更新 README 选题表。

口吻：李大妈大白话，不堆术语。口语化不等于俗套话，避用粗俗直白词。钩子要有认知翻转，每条行动解释 why。
