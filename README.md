# 補助金ガイド（GitHub Pages 版）

Googleサイトで運用していた「補助金ガイド」を静的サイトとして移行したものです。

## 構成

```
build.py                      ページ生成スクリプト（ページ追加・並び替え）
content/*.html                各ページの本文（編集するのはここ）
docs/                         自動生成される公開用ファイル（直接編集しない）
docs/assets/img/              画像置き場
.github/workflows/deploy.yml  自動ビルドの設定
```

## 編集の流れ

1. `content/<slug>.html` を開いて本文を書き換える
2. 変更を commit して push
3. GitHub Actions が自動でビルドし、サイトに反映される

ヘッダー・サイドバー・前後ナビ・フッターは `build.py` が全ページに自動で付けるので、
本文以外を触る必要はありません。

## サイドバーの表示名を短くする

長いページ名はサイドバーで折り返して読みにくくなります。`build.py` の
`NAV_SHORT` に短い名前を書くと、サイドバーだけその名前で表示されます
（ページ内の見出しは元のままです）。

```python
NAV_SHORT = {
    "tejun-inv-chusho-pc1-pos1": "中小企業｜PC○ POS○",
}
```

サイドバーは現在見ているセクションだけが開きます。20項目を常時出さないので、
今どこにいるかが分かりやすくなります。

## 本文で使えるパーツ

```html
<p class="lead">導入文。少し大きめのグレーで表示されます。</p>

<ol class="steps">
  <li><h3>ステップ名</h3><p>説明。</p></li>
</ol>

<ul class="cards">
  <li><a href="xxx.html">リンク名<span class="note">補足</span></a></li>
</ul>

<div class="callout">
  <strong>見出し</strong>
  <p>注意書き。</p>
</div>

<figure>
  <img src="assets/img/sample.png" alt="説明">
  <figcaption>図の説明</figcaption>
</figure>
```

## ページを追加・並び替えするとき

`build.py` の `PAGES` リストを編集します。

```python
PAGES = [
    ("index", "TOP", None),
    ("jisseki", "実績報告について", None),
    ("jisseki-seikyusho", "請求書（請求明細書）", "jisseki"),
    ...
]
```

`(ファイル名, 表示タイトル, 親ページ)` の順です。親が `None` なら第1階層、
親slugを書くとその下の階層になります。リストの並び順がそのまま
サイドバーの順序と「前へ／次へ」の順序になります。

## 画像

`docs/assets/img/` に置いて、本文からこう読み込みます。

```html
<img src="assets/img/seikyusho-sample.png" alt="請求書の記載例">
```

## GitHub Pages で公開する（自動ビルド）

このリポジトリには GitHub Actions の設定が入っているので、**push すれば自動で
ビルドと公開が行われます**。手元で `build.py` を実行する必要はありません。

### 最初に1回だけ行う設定

1. GitHubで新しいリポジトリを作成する
2. このフォルダの中身を push する
3. リポジトリの **Settings → Pages** を開く
4. Source を **GitHub Actions** に変更する（"Deploy from a branch" ではありません）

以上で完了です。数分後に `https://<ユーザー名>.github.io/<リポジトリ名>/` で公開されます。

### 2回目以降

`content/*.html` を編集して push するだけです。

```bash
git add .
git commit -m "請求書ページを更新"
git push
```

push すると Actions が動き、1〜2分でサイトに反映されます。
進行状況はリポジトリの **Actions** タブで確認できます。

### GitHubの画面だけで編集する

パソコンにGitを入れていなくても更新できます。

1. GitHubでリポジトリを開く
2. `content` フォルダから編集したいファイルを開く
3. 鉛筆アイコンをクリックして書き換える
4. **Commit changes** を押す

これだけで自動的にビルドされ、サイトが更新されます。

### docs/ はコミットしません

`docs/` は Actions が毎回生成するため `.gitignore` に入れてあります。
編集するのは `content/` と `build.py` だけです。

画像は例外で、`docs/assets/img/` に置いたものもコミットが必要です。
`.gitignore` の `docs/` の行を消して、代わりに次のように書き換えてください。

```
docs/*.html
docs/assets/style.css
docs/assets/site.js
```

## 独自ドメインを使う

Settings → Pages の Custom domain に入力したうえで、`build.py` の `main()` 内に
CNAMEファイルを出力する処理を追加してください。

```python
with open(os.path.join(OUT, "CNAME"), "w") as f:
    f.write("guide.example.co.jp")
```

## ローカルで確認する

```bash
python3 build.py
cd docs && python3 -m http.server 8000
```

ブラウザで http://localhost:8000 を開きます。

## Googleサイトからの引っ越し作業

各ページで、Googleサイト側の文章と画像を対応する `content/*.html` に移してください。
画像はGoogleサイト上で右クリック→画像を保存し、`docs/assets/img/` に置きます。
移行が済んだページから順に公開して問題ありません。
