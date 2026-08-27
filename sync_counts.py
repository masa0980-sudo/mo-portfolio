#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_counts.py

index.html 内の記事数表記（SEO description・Twitter description・
ヒーロー統計バッジ・各セクションの section-count）を、実際のカード数
から自動算出して同期する。

新しい記事カードを手で追加した後、このスクリプトを実行するだけで
6箇所すべてが実数に揃う。過去に「21のまま」「29のまま」と2度、
手動更新を忘れて古い数字が残るバグが発生したための対策。

外部ライブラリ不要（標準ライブラリのみ）。
実行: python -X utf8 sync_counts.py
"""
import re
import sys
from pathlib import Path

# このスクリプト自身と同じフォルダの index.html を対象にする
# （リポジトリをどこへ移動しても壊れないよう絶対パスは書かない）
TARGET = Path(__file__).resolve().parent / "index.html"

CARD_RE = re.compile(r'<a class="card reveal"')
SECTION_RE = re.compile(r'<section class="section[^"]*">.*?</section>', re.DOTALL)
SECTION_COUNT_RE = re.compile(r'<span class="section-count">\d+ articles?</span>')

DESC_RE = re.compile(r'(公開した)\d+(本のAI学習記事)')
# 媒体名は note.com 単独から「note.com・Brain・Zenn」へ増える可能性があるため、
# 媒体名そのものは固定せず「〜の N記事をまとめた」の形だけを見る。
# （媒体名をハードコードしていたせいで、Zenn/Brain 追加時に不一致になった）
TWITTER_RE = re.compile(r'([^、。]{0,40}の)\d+(記事をまとめた)')
STATNUM_RE = re.compile(r'(<span class="stat-num">)\d+(</span>\s*<span class="stat-label">公開記事数)')


def main():
    if not TARGET.exists():
        sys.stderr.write(f"ERROR: {TARGET} が見つかりません\n")
        sys.exit(1)

    html = TARGET.read_text(encoding="utf-8")
    total = len(CARD_RE.findall(html))
    changes = []

    def fix_section(m):
        section = m.group(0)
        n = len(CARD_RE.findall(section))

        def fix_count(cm):
            old = cm.group(0)
            unit = "article" if n == 1 else "articles"
            new = f'<span class="section-count">{n} {unit}</span>'
            if old != new:
                changes.append(f"section-count: {old} -> {new}")
            return new

        return SECTION_COUNT_RE.sub(fix_count, section)

    new_html = SECTION_RE.sub(fix_section, html)

    def sync_total(pattern: re.Pattern, label: str):
        nonlocal new_html

        def repl(m):
            old = m.group(0)
            new = f"{m.group(1)}{total}{m.group(2)}"
            if old != new:
                changes.append(f"{label}: {old} -> {new}")
            return new

        new_html = pattern.sub(repl, new_html)

    sync_total(DESC_RE, "description")
    sync_total(TWITTER_RE, "twitter")
    sync_total(STATNUM_RE, "stat-num")

    if new_html == html:
        print(f"OK: 変更なし（既に同期済み・総記事数 {total}件）")
        return

    TARGET.write_text(new_html, encoding="utf-8")
    print(f"OK: 総記事数 {total}件 に同期しました（{len(changes)}箇所を更新）")
    for c in changes:
        print("  " + c)


if __name__ == "__main__":
    main()
