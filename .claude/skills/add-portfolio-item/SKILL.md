---
name: add-portfolio-item
description: ポートフォリオに記事・ゲーム・LINEスタンプのカードを1枚追加する手順。「新しい記事を載せて」「ゲームを追加して」「スタンプを追加して」「サムネイルを更新して」と言われたときに使う。カードの書式、画像の置き方(CSPの制約)、件数の同期までを含む。
---

# カードを1枚追加する

`index.html` に `<a>` を1つ足すだけで、検索・絞り込み・タブ切り替えは**自動で効く**
（JSはDOMを直接見ているので、カードを増やしてもJSの編集は不要）。

ただし**件数表記の同期だけは手作業では絶対に合わない**ので、最後に必ずスクリプトを回す。

## 1. 画像を `img/` に置く

命名規則は `<種別>_<連番>_<公開日>_<スラッグ>.png`。

```
img/game_06_2026-08-28_typing-quotes.png
img/note_51_2026-08-28_....png
img/stamp_09_....png        ← スタンプだけ日付なし
```

**CSP が厳しいので外部URLの画像は表示できない。**

```
img-src 'self' data: https://assets.st-note.com https://masa0980-sudo.github.io
```

note のカバー画像以外は、**必ずダウンロードして `img/` に保存し、相対パスで参照する**。
外部URLを直に書くと、ローカルでは見えても本番で無言のまま表示されない。

ゲームのサムネイルは**そのゲームのタイトル画面のスクリーンショット**。
公開URL(`*.github.io`)にはこの環境から到達できないので、**ゲームのリポジトリを
ローカルで配信してPlaywrightで撮る**（`verify-in-browser` スキル参照）。

## 2. カードを足す

種別ごとに class が違う。**この class が件数の集計キーになっている**ので、勝手に変えないこと。

```html
<!-- 記事 -->
<a class="card reveal" href="..." target="_blank" rel="noopener noreferrer">

<!-- ゲーム -->
<a class="card reveal game-card" href="https://masa0980-sudo.github.io/<repo>/" target="_blank" rel="noopener noreferrer">
  <img class="card-thumb" loading="lazy" decoding="async" src="img/game_06_2026-08-28_typing-quotes.png" alt="名言タイピング キーアート">
  <div class="card-body">
    <span class="card-date">偉人の名言でタイピング・日英2モード</span>
    <p class="card-title">名言タイピング</p>
    <span class="card-link">🕹 プレイする</span>
  </div>
</a>

<!-- スタンプ（.stamp-card-wrap で包む） -->
<div class="stamp-card-wrap">
  <a class="card reveal stamp-card" href="https://line.me/S/sticker/..." ...>
```

外部リンクには `target="_blank" rel="noopener noreferrer"` を必ず付ける。

## 3. 件数を同期する（必須）

```bash
python3 -X utf8 sync_counts.py
```

カードの実数を数え直して、**SEO description・Twitter description・サイドバーの `nav-count`・
各セクションの `section-count`** をまとめて書き換える。

**これを飛ばした結果、過去に3回ずれた。**

- 記事数が「21のまま」「29のまま」残った（2回）
- ゲームを7本目まで増やしたとき、`section-count` は7に直したのに
  **サイドバーの `nav-count` が6のまま残った**（1回）

さらに媒体別（note / Brain / Zenn）の件数も、note 43 / Brain 2 / Zenn 1 = 46 なのに
記事総数が 50、という食い違いを起こしたことがある。

これらを受けて、スクリプトは記事・ゲーム・スタンプ・媒体別の**4系統すべて**を見る。
対象は `data-sync` 属性で名指ししているので、見た目のマークアップを変えても壊れない
（実際に媒体ナビを「記事」の下へ入れ子にする改修が入ったが、属性を保ったので動いている）。
**`data-sync` 属性を消さないこと。**

`.claude/scripts/check.sh` を使うと、同期して差分が出た場合にエラーで止まる（push前の関門）。

## 4. 確認してからコミットする

`verify-in-browser` スキルの手順でタブを開いて、カードが出ていること・
画像が表示されていること・検索に引っかかることを見る。

## やらないこと

- **`legacy/index.html` は更新しない。** サイドバー型に刷新する前の画面を凍結したアーカイブで、
  `noindex` 指定・`../img/` 参照・canonical は現行版、という状態のまま置いてある。
  新しいカードを足す先は**ルートの `index.html` だけ**。
- `sync_counts.py` の対象もルートの `index.html` だけなので、legacy 側が件数に混ざることはない。
