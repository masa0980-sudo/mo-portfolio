#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_counts.py

index.html 内の件数表記（SEO description・Twitter description・
サイドバーの nav-count・各セクションの section-count）を、実際のカード数
から自動算出して同期する。

記事・ゲーム・スタンプのカードを手で追加した後、このスクリプトを実行する
だけで全箇所が実数に揃う。過去に「21のまま」「29のまま」と2度、さらに
ゲームを7本目まで増やしたときにサイドバーだけ6のまま残る、と計3度、
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

# カードの種類は class で見分ける。記事カードだけは追加クラスが付かないので、
# 閉じ引用符まで含めてマッチさせ、game-card / stamp-card を巻き込まないようにしている。
CARD_RE = re.compile(r'<a class="card reveal"')
GAME_CARD_RE = re.compile(r'<a class="card reveal game-card"')
STAMP_CARD_RE = re.compile(r'<a class="card reveal stamp-card"')

# 種類ごとの (カードの正規表現, 単数形, 複数形)。
# section-count の単位と data-sync のキーを、この1箇所から決めている。
KINDS = {
    "articles": (CARD_RE, "article", "articles"),
    "games": (GAME_CARD_RE, "game", "games"),
    "stamps": (STAMP_CARD_RE, "stamp", "stamps"),
}

# 記事タブの中の媒体別パネル。パネル同士は兄弟要素なので、開始タグで区切って
# それぞれのチャンクに含まれる記事カードを数える。
# （末尾のチャンクはゲーム/スタンプのパネルまで含むが、そちらのカードには
#   game-card / stamp-card が付いていて CARD_RE に当たらないので混ざらない）
SUBTAB_RE = re.compile(r'<div class="subtab-panel" data-subtab="([a-z]+)"')

SECTION_RE = re.compile(r'<section class="section[^"]*">.*?</section>', re.DOTALL)
SECTION_COUNT_RE = re.compile(
    r'<span class="section-count">\d+ (?:articles?|games?|stamps?)</span>'
)

DESC_RE = re.compile(r'(公開した)\d+(本のAI学習記事)')
# 媒体名は note.com 単独から「note.com・Brain・Zenn」へ増える可能性があるため、
# 媒体名そのものは固定せず「〜の N記事をまとめた」の形だけを見る。
# （媒体名をハードコードしていたせいで、Zenn/Brain 追加時に不一致になった）
TWITTER_RE = re.compile(r'([^、。]{0,40}の)\d+(記事をまとめた)')
# サイドバーのナビに出す件数。data-sync 属性で対象を名指しするので、
# 見た目のマークアップを変えても壊れない。
# （旧ヒーローの stat-num / stat-label はサイドバー化で廃止した）
def navcount_re(kind: str) -> re.Pattern:
    return re.compile(r'(<span class="nav-count" data-sync="%s">)\d+(</span>)' % kind)


def main():
    if not TARGET.exists():
        sys.stderr.write(f"ERROR: {TARGET} が見つかりません\n")
        sys.exit(1)

    html = TARGET.read_text(encoding="utf-8")
    totals = {kind: len(rx.findall(html)) for kind, (rx, _, _) in KINDS.items()}
    total = totals["articles"]

    # 媒体別(note / Brain / Zenn)の件数。合計は articles と一致するはず。
    parts = SUBTAB_RE.split(html)
    media = {
        parts[i]: len(CARD_RE.findall(parts[i + 1]))
        for i in range(1, len(parts) - 1, 2)
    }
    if media and sum(media.values()) != total:
        sys.stderr.write(
            f"WARN: 媒体別の合計({sum(media.values())})が記事総数({total})と一致しません: {media}\n"
        )
    changes = []

    def fix_section(m):
        section = m.group(0)
        # そのセクションに実際に入っているカードの種類で単位を決める。
        # セクションの見出し文言に依存しないので、見出しを変えても壊れない。
        for kind, (rx, one, many) in KINDS.items():
            n = len(rx.findall(section))
            if n:
                break
        else:
            return section

        def fix_count(cm):
            old = cm.group(0)
            unit = one if n == 1 else many
            new = f'<span class="section-count">{n} {unit}</span>'
            if old != new:
                changes.append(f"section-count: {old} -> {new}")
            return new

        return SECTION_COUNT_RE.sub(fix_count, section)

    new_html = SECTION_RE.sub(fix_section, html)

    missing = []

    def sync_total(pattern: re.Pattern, label: str, value: int):
        nonlocal new_html

        def repl(m):
            old = m.group(0)
            new = f"{m.group(1)}{value}{m.group(2)}"
            if old != new:
                changes.append(f"{label}: {old} -> {new}")
            return new

        new_html, n = pattern.subn(repl, new_html)
        # 1件も当たらないのは「同期したつもりで古い数字が残る」状態。
        # re.sub は黙って何もしないので、ここで気づけるようにする。
        if n == 0:
            missing.append(label)

    # SEO文言は記事数だけを指しているので articles を渡す
    sync_total(DESC_RE, "description", total)
    sync_total(TWITTER_RE, "twitter", total)
    for kind in KINDS:
        sync_total(navcount_re(kind), f"nav-count[{kind}]", totals[kind])
    for name, n in media.items():
        sync_total(navcount_re(f"media-{name}"), f"nav-count[media-{name}]", n)

    if missing:
        sys.stderr.write(
            "WARN: 同期対象が見つかりませんでした: "
            + ", ".join(missing)
            + "\n      index.html の該当箇所を消したか、書式を変えた可能性があります。\n"
        )

    summary = "・".join(f"{k} {v}件" for k, v in totals.items())
    if media:
        summary += "（媒体別 " + "/".join(f"{k} {v}" for k, v in media.items()) + "）"

    if new_html == html:
        print(f"OK: 変更なし（既に同期済み・{summary}）")
        return

    TARGET.write_text(new_html, encoding="utf-8")
    print(f"OK: {summary} に同期しました（{len(changes)}箇所を更新）")
    for c in changes:
        print("  " + c)


if __name__ == "__main__":
    main()
