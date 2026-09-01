#!/usr/bin/env bash
# ローカルでこのサイトを配信するだけのヘルパー。
# ビルド不要の静的サイトなので、静的サーバーを立てれば本番と同じものが見られる。
#
# 使い方: .claude/scripts/serve.sh [port]  (デフォルト 8935)
set -euo pipefail

PORT="${1:-8935}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

cd "$ROOT"

# Windows には「実行しても何もせず正常終了する」python3 スタブが入っていることがある
# （Microsoft Store 版インストーラへの誘導）。バージョンが取れるものを本物とみなす。
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

echo "http://localhost:$PORT/ で配信します（Ctrl+C で停止）"
"$PY" -m http.server "$PORT"
