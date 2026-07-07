#!/bin/bash
# 炎症系列字数自检 — 每次生成/修改 HTML 后跑一遍
# 用法：bash check_chars.sh issues/issue-XX.html

set -euo pipefail

HTML="$1"
if [ ! -f "$HTML" ]; then
  echo "❌ 文件不存在: $HTML"
  exit 1
fi

N=$(basename "$HTML" .html | sed 's/issue-//')
PASS=0
FAIL=0

check() {
  local field="$1" line="$2" max="$3"
  local len=${#line}
  if [ "$len" -gt "$max" ]; then
    echo "  ❌ $field: [$line]  ${len}字 > 上限${max}"
    FAIL=$((FAIL + 1))
  else
    echo "  ✅ $field: [$line]  ${len}字"
    PASS=$((PASS + 1))
  fi
}

echo "========== #${N} 字数自检 =========="
echo ""

# 钩子标题
TITLE=$(grep -oP '<h1>\K[^<]+' "$HTML")
check "钩子标题" "$TITLE" 7
echo ""

# 中医概念
TCM_C=$(grep 'tcm-col' -A3 "$HTML" | grep -oP '<div class="concept">\K[^<]+')
check "中医概念" "$TCM_C" 5   # 提示用，6字及以上必须换行
echo ""

# 中医描述
TCM_DESC_LINE=$(grep 'tcm-col' -A4 "$HTML" | grep -oP '<div class="desc">\K.*?(?=</div>)')
TCM_D1=$(echo "$TCM_DESC_LINE" | sed 's/<br>.*//')
TCM_D2=$(echo "$TCM_DESC_LINE" | sed 's/.*<br>//')
check "中医描述行1" "$TCM_D1" 11
check "中医描述行2" "$TCM_D2" 11
echo ""

# 西医概念
WEST_C=$(grep 'west-col' -A3 "$HTML" | grep -oP '<div class="concept">\K[^<]+')
check "西医概念" "$WEST_C" 5
echo ""

# 西医描述
WEST_DESC_LINE=$(grep 'west-col' -A4 "$HTML" | grep -oP '<div class="desc">\K.*?(?=</div>)')
WEST_D1=$(echo "$WEST_DESC_LINE" | sed 's/<br>.*//')
WEST_D2=$(echo "$WEST_DESC_LINE" | sed 's/.*<br>//')
check "西医描述行1" "$WEST_D1" 11
check "西医描述行2" "$WEST_D2" 11
echo ""

# what ×3
echo "-- what --"
i=1
while IFS= read -r w; do
  check "what$i" "$w" 20
  i=$((i + 1))
done < <(grep -oP '<div class="what">\K[^<]+' "$HTML")
echo ""

# why ×3
echo "-- why --"
i=1
while IFS= read -r w; do
  check "why$i" "$w" 20
  i=$((i + 1))
done < <(grep -oP '<div class="why">\K[^<]+' "$HTML")

echo ""
echo "========== 结果: ${PASS}✅ / ${FAIL}❌ =========="
if [ "$FAIL" -gt 0 ]; then
  echo "⚠️  有超标的，修完重新跑"
  exit 1
else
  echo "全部通过 ✅"
fi
