---
name: add-portfolio-item
description: ポートフォリオに記事・ゲーム・LINEスタンプ・YouTube動画のカードを1枚追加する手順。「新しい記事を載せて」「ゲームを追加して」「スタンプを追加して」「動画を追加して」「サムネイルを更新して」と言われたときに使う。カードの書式、画像の置き方(CSPの制約)、件数の同期までを含む。
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
`*.github.io` への直接アクセス（`urllib` や Playwright の `page.goto`）は
セッションによって届くこともあれば届かないこともある。まず直接
`page.goto('https://masa0980-sudo.github.io/<repo>/')` で撮ってみて、
繋がらない場合だけ**ゲームのリポジトリをローカルで配信して撮る**
（`verify-in-browser` スキル参照）フォールバックに切り替える。

YouTube動画のサムネイルは `https://i3.ytimg.com/vi/<video_id>/maxresdefault.jpg`
（無ければ `hqdefault.jpg`）をそのままダウンロードする。Shorts動画は縦動画+左右ぼかしの
16:9構図になっているので `.video-card .card-thumb { object-position: center; }` を通す
だけでよい（他の種別に合わせて `object-position` を種別ごとに上書きしている箇所を見る）。

## 2. カードを足す

種別ごとに class が違う。**この class が件数の集計キーになっている**ので、勝手に変えないこと。

```html
<!-- 記事（note.comの場合は3.5節のdata-magazine属性も参照） -->
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

<!-- 動画（YouTube） -->
<a class="card reveal video-card" href="https://www.youtube.com/shorts/<動画ID>" target="_blank" rel="noopener noreferrer">
  <img class="card-thumb" loading="lazy" decoding="async" src="img/youtube_01_2026-09-03_<動画ID>.jpg" alt="<動画タイトル> サムネイル">
  <div class="card-body">
    <span class="card-date">YYYY-MM-DD</span>
    <p class="card-title"><動画タイトル></p>
    <span class="card-link">YouTube で見る</span>
  </div>
</a>
```

外部リンクには `target="_blank" rel="noopener noreferrer"` を必ず付ける。

**動画・記事に限らず、外部リンクを足す前に実データで裏取りする。** ユーザーから渡された
URLをそのまま信用しない。実際に「動画1本のURL」と「チャンネルのURL」を混同しかけたことが
あり、チャンネルの**RSSフィード**（`https://www.youtube.com/feeds/videos.xml?channel_id=<ID>`）
で動画ID・タイトル・公開日・チャンネル名を確認してから使った。JS描画されたYouTubeのHTMLを
`WebFetch`や正規表現で読もうとしても、実データではなくUIの固定文言（「キーボード
ショートカット」等）を拾ってしまい信用できない。**RSSフィードなら確実**。

### note記事には data-magazine 属性が必須（2026-09-05〜）

noteタブは「🕒 時系列 / 🗂 マガジン別 / 💎 有料記事」の3モードを切り替えられる作りになっている
（`initNoteView`、記事タブ内・note媒体パネルのみ）。マガジン別モードはカードの
`data-magazine="<マガジンkey>"` 属性を見て絞り込むので、**新しいnote記事を足すときは
このマガジンkeyの特定も同時に必要**。飛ばすと「時系列」には出るが「マガジン別」の
どのチップを選んでも出てこない、という見た目に気づきにくい抜けになる。

マガジンkeyは記事本文APIの `belonging_magazine_keys` で取れる。

```bash
curl -s "https://note.com/api/v3/notes/<記事key>" | python -c "
import json,sys
print(json.load(sys.stdin)['data']['belonging_magazine_keys'])
"
```

**複数マガジンに所属することがある**（実績: 55記事中6記事）。その場合は
`data-magazine="key1 key2"` のように半角スペース区切りで両方書く。

**マガジンに1つも属さない記事もある**（新規記事をまだどのマガジンにも入れていない場合）。
その場合は `data-magazine` 属性自体を付けない（空文字にしない）。時系列モードには出るが、
マガジン別モードのどのチップにも出ない状態になる——これは正しい挙動。

**返ってくるkeyの中に、7マガジン一覧（`note.com/api/v2/creators/mo0980/contents?kind=magazine`）
に存在しない古いkeyが混ざることがある**（実績: 5個）。過去にリネーム・統合されたマガジンの
残骸と見られ、必ず生きているマガジンのkeyと一緒に出てくる。**7マガジン一覧に無いkeyは無視し、
一覧にある方だけを使う**。

現在の7マガジンとkeyの対応（サイドバー実装時点、`index.html` の `.magazine-chip` 参照）:

| マガジン名 | key |
|---|---|
| Claude Code 実践ラボ | `mea086c047f4f` |
| Claude 最新モデル追跡 | `m9ed6b4fd14c1` |
| AIニュース・セキュリティ | `mcfbd7faa8d47` |
| AIで作って売る（実践） | `me39434a23b8c` |
| Claude Code はじめの一歩 | `mfa775ffb29da` |
| Claude Codeでゲームを作ってみた | `mc8ba0eb364d8` |
| AIで遊ぼう編 | `m585ab7bd6a87` |

新しいマガジンを note.com 側で作った場合は、`.note-magazine-chips` 内に
`<button class="magazine-chip" data-magazine-target="<key>">名前<span class="magazine-chip-count">件数</span></button>`
を1行足す（`sync_counts.py` は関与しないので手作業。件数はチップの表示用の目安であり、
実際の絞り込みは `data-magazine` 属性の一致で行われるため多少ズレても実害はない）。

## 3. 件数を同期する（必須）

```bash
python -X utf8 sync_counts.py
# または: .claude/scripts/check.sh   ← push前の関門。同期して差分が出たらエラーで止まる
```

**`python3` ではなく `python` を使う。** Windows には実行しても何もせず exit 0 で
返るだけの `python3` スタブ（Microsoft Store 版インストーラへの誘導）が入っていることがある。
`command -v python3` も終了コードも通ってしまうため、気づかずに「同期したつもり」で
古い数字が残る事故が起きた。`.claude/scripts/check.sh` は `python3 → python → py` の順に
実際に動くものを探すよう直してあるので、迷ったらこちらを使う。

カードの実数を数え直して、**SEO description・Twitter description・サイドバーの `nav-count`・
各セクションの `section-count`** をまとめて書き換える。

**これを飛ばした結果、過去に3回ずれた。**

- 記事数が「21のまま」「29のまま」残った（2回）
- ゲームを7本目まで増やしたとき、`section-count` は7に直したのに
  **サイドバーの `nav-count` が6のまま残った**（1回）

さらに媒体別（note / Brain / Zenn）の件数も、note 43 / Brain 2 / Zenn 1 = 46 なのに
記事総数が 50、という食い違いを起こしたことがある。

これらを受けて、スクリプトは**記事・ゲーム・スタンプ・動画・媒体別の5系統すべて**を見る
（`KINDS` 辞書に1行足すだけで種別が増やせる作りにしてあり、動画追加時もこれで対応した）。
対象は `data-sync` 属性で名指ししているので、見た目のマークアップを変えても壊れない
（実際に媒体ナビを「記事」の下へ入れ子にする改修が入ったが、属性を保ったので動いている）。
**`data-sync` 属性を消さないこと。**

新しい種別を増やすときは `<a class="card reveal ○○-card">` の形でクラスを付け、
`sync_counts.py` の `KINDS` にエントリを1行足すだけでよい。JS側の変更は不要。

## 4. 確認してからコミットする

`verify-in-browser` スキルの手順でタブを開いて、カードが出ていること・
画像が表示されていること・検索に引っかかることを見る。

## やらないこと

- **`legacy/index.html` は更新しない。** サイドバー型に刷新する前の画面を凍結したアーカイブで、
  `noindex` 指定・`../img/` 参照・canonical は現行版、という状態のまま置いてある。
  新しいカードを足す先は**ルートの `index.html` だけ**。
- `sync_counts.py` の対象もルートの `index.html` だけなので、legacy 側が件数に混ざることはない。
