# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Claude Code 活用ライター MO のポートフォリオサイト。記事・LINEスタンプ・ゲーム・掲示板への
導線を1ページにまとめてある。**ビルドステップ・依存パッケージ・テストフレームワークは無い**
（意図的にそうしている。増やさないこと）。

公開URL: https://masa0980-sudo.github.io/mo-portfolio/

```
index.html        # サイト本体。HTML/CSS/JS 全部入り
legacy/index.html # 刷新前の旧デザイン(凍結。更新しない)
img/              # カード画像。すべてローカルに置く
sync_counts.py    # 件数表記をカードの実数に同期する
.nojekyll
```

## Commands

```bash
python3 -X utf8 sync_counts.py   # 件数表記の同期(カードを増やしたら必須)

.claude/scripts/serve.sh 8935    # ローカル配信
.claude/scripts/check.sh         # push前の関門(件数がずれていたらエラーで止まる)
```

デプロイは `main` への push だけ。GitHub 内蔵の `pages build and deployment` が走る
（自前のワークフローファイルは無い）。**別途デプロイコマンドはない。**

## Architecture

`index.html` 1枚に収まっている。JSは末尾の `<script>` にIIFEで並んでいる。

| 関数 | 役割 |
|---|---|
| `initScrollReveal` | スクロールで `.reveal` を出す。`prefers-reduced-motion` なら即表示 |
| `initTabGroup(...)` | タブ切替。**親タブ(記事/スタンプ/ゲーム/掲示板)と媒体サブタブで共用** |
| `initMediaVisibility` | 媒体サブタブは記事タブ専用なので、他タブでは隠す |
| `initFilter` | 検索と絞り込み |
| `initMenu` | 900px以下のサイドバードロワー |

**`initFilter` はカードのDOMを直接読んで判定している。**
そのため**カードを1枚足してもJSの編集は不要**。これは意図した設計なので、
カード追加のたびにJSへ配列を足すような書き方に変えないこと。

### 件数表記は手で書き換えない

件数は **SEO description / Twitter description / サイドバーの `nav-count` / 各セクションの
`section-count`** の4系統に散っている。手で合わせようとすると必ずどこかが残る。

実際に3回ずれた。記事数が「21のまま」「29のまま」（2回）、
ゲームを7本目まで増やしたときに `section-count` は7に直したのに
**サイドバーの `nav-count` が6のまま残った**（1回）。

```bash
python3 -X utf8 sync_counts.py
```

カードの実数から算出して全箇所を書き換える。集計はカードの class で見分けている。

| 種別 | class | 同期先の目印 |
|---|---|---|
| 記事 | `card reveal`（追加クラス無し） | `data-sync="articles"` |
| ゲーム | `card reveal game-card` | `data-sync="games"` |
| スタンプ | `card reveal stamp-card` | `data-sync="stamps"` |
| 媒体別 | 記事カードを `subtab-panel` 単位で数える | `data-sync="media-note\|media-brain\|media-zenn"` |

媒体別の合計が記事総数と食い違ったときも `WARN:` で知らせる（実際に
note 43 / Brain 2 / Zenn 1 = 46 なのに総数 50、という不一致が起きたことがある）。

**この class と `data-sync` 属性は集計キーなので変えない・消さない。**
`re.sub` は当たらなくても黙って何もしないため、対象が見つからないときは
スクリプトが `WARN:` を出すようにしてある。**この警告を無視しないこと。**

### CSP が厳しい

```
default-src 'self'; img-src 'self' data: https://assets.st-note.com https://masa0980-sudo.github.io;
connect-src 'none'; object-src 'none'; frame-ancestors 'none'
```

- **画像は原則ローカル (`img/`) に置く。** 外部URLを直に書くと、ローカルでは見えても
  本番で無言のまま表示されない（Brain / Zenn のカバー画像もこの理由でローカルに保存した）。
- `connect-src 'none'` なので fetch/XHR は動かない。外部データが要る話が出たら、まずここを見る。
- Google Fonts のために `fonts.googleapis.com` / `fonts.gstatic.com` だけ例外を開けてある。

### `legacy/` は凍結

サイドバー型へ刷新する前の画面を残したアーカイブ。`noindex` 指定、画像は複製せず `../img/` を参照、
canonical は現行版を指す。**新しいカードを足す先はルートの `index.html` だけ**で、
legacy は更新しない。`sync_counts.py` の対象もルートの `index.html` だけ。

## 注意点

- **このサンドボックスからは `*.github.io` に到達できない。** 公開URLでの表示確認は不可能なので、
  ローカルで確認したうえで**「公開URLでの実表示は未確認」と明示する**こと。
  到達できなかったことを、確認できたことにしない。
- ゲームのサムネイルは公開URLからは撮れない。**そのゲームのリポジトリをローカルで配信して撮る。**
- **Actions API のジョブ状態は数分古いまま返ることがある。** 進んでいないように見えても
  すぐに cancel / rerun せず、数分待って取り直す。最終判断は `get_job_logs` の実ログ
  （`Evaluated environment url: ...` が出ていれば成功）。

## `.claude` の中身

| 場所 | 用途 |
|---|---|
| `skills/add-portfolio-item/` | 記事・ゲーム・スタンプのカードを1枚足す手順 |
| `skills/verify-in-browser/` | ローカル配信〜Playwrightでの確認、サムネイルの撮り方 |
| `scripts/serve.sh` | ローカル配信 |
| `scripts/check.sh` | push前の関門（件数がずれていたらエラー） |
| `settings.json` | 定型コマンドの許可設定 |
