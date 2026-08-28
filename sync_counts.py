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
# サイドバーのナビに出す件数。data-sync 属性で対象を名指しするので、
# 見た目のマークアップを変えても壊れない。
# （旧ヒーローの stat-num / stat-label はサイドバー化で廃止した。
#   件数の表示場所はここ1箇所に集約してある）
NAVCOUNT_RE = re.compile(r'(<span class="nav-count" data-sync="articles">)\d+(</span>)')


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

    missing = []

    def sync_total(pattern: re.Pattern, label: str):
        nonlocal new_html

        def repl(m):
            old = m.group(0)
            new = f"{m.group(1)}{total}{m.group(2)}"
            if old != new:
                changes.append(f"{label}: {old} -> {new}")
            return new

        new_html, n = pattern.subn(repl, new_html)
        # 1件も当たらないのは「同期したつもりで古い数字が残る」状態。
        # re.sub は黙って何もしないので、ここで気づけるようにする。
        if n == 0:
            missing.append(label)

    sync_total(DESC_RE, "description")
    sync_total(TWITTER_RE, "twitter")
    sync_total(NAVCOUNT_RE, "nav-count")

    if missing:
        sys.stderr.write(
            "WARN: 同期対象が見つかりませんでした: "
            + ", ".join(missing)
            + "\n      index.html の該当箇所を消したか、書式を変えた可能性があります。\n"
        )

    if new_html == html:
        print(f"OK: 変更なし（既に同期済み・総記事数 {total}件）")
        return

    TARGET.write_text(new_html, encoding="utf-8")
    print(f"OK: 総記事数 {total}件 に同期しました（{len(changes)}箇所を更新）")
    for c in changes:
        print("  " + c)


if __name__ == "__main__":
    main()
