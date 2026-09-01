#!/usr/bin/env bash
# push前のチェック。件数表記がカードの実数とずれていないかを見る。
#
# sync_counts.py は「ずれていたら直す」スクリプトなので、
# ここでは実行したうえで **今この実行で書き換えが起きたらエラーにする**。
# 直った状態をコミットに含めてほしいので、黙って通さない。
#
# 判定に git diff を使わないのは、コミット前の作業差分（カードを足した分など）と
# 「件数がずれていた」を区別できないため。実行前後のファイルを直接比べる。
#
# 使い方: .claude/scripts/check.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

# Windows には「実行しても何もせず正常終了する」python3 スタブ
# （Microsoft Store 版インストーラへの誘導）が入っていることがある。
# exit 0 で返るので呼び出し側はエラーに気づけない。実際にこれで
# check.sh が黙って素通りしていた。バージョンが取れるものを本物とみなす。
PY=""
for c in python3 python py; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys' >/dev/null 2>&1; then
    PY="$c"; break
  fi
done
if [ -z "$PY" ]; then
  echo "✗ Python が見つかりません（python3 / python / py のいずれも動きません）" >&2
  exit 1
fi

BEFORE="$(mktemp)"
trap 'rm -f "$BEFORE"' EXIT
cp index.html "$BEFORE"

echo "▶ 件数表記の同期"
"$PY" -X utf8 sync_counts.py

if ! cmp -s "$BEFORE" index.html; then
  echo
  echo "✗ 件数がずれていたので index.html を書き換えた。差分を確認してコミットに含めること:"
  diff -u "$BEFORE" index.html | grep -E '^[+-]' | grep -v '^[+-][+-]' || true
  exit 1
fi

echo
echo "✓ 件数表記はカードの実数と一致している"
