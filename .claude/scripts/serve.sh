#!/usr/bin/env bash
# ローカルでこのサイトを配信するだけのヘルパー。
# ビルド不要の静的サイトなので、静的サーバーを立てれば本番と同じものが見られる。
#
# 使い方: .claude/scripts/serve.sh [port]  (デフォルト 8935)
set -euo pipefail

PORT="${1:-8935}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

cd "$ROOT"
python3 -m http.server "$PORT"
