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

BEFORE="$(mktemp)"
trap 'rm -f "$BEFORE"' EXIT
cp index.html "$BEFORE"

echo "▶ 件数表記の同期"
python3 -X utf8 sync_counts.py

if ! cmp -s "$BEFORE" index.html; then
  echo
  echo "✗ 件数がずれていたので index.html を書き換えた。差分を確認してコミットに含めること:"
  diff -u "$BEFORE" index.html | grep -E '^[+-]' | grep -v '^[+-][+-]' || true
  exit 1
fi

echo
echo "✓ 件数表記はカードの実数と一致している"
