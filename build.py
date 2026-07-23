# -*- coding: utf-8 -*-
"""補助金ガイド 静的サイトビルダー
python3 build.py で docs/ 以下に全ページを生成します。
"""
import os, shutil, html

OUT = "docs"

# ---------------------------------------------------------------
# サイト構造： (slug, タイトル, 親slug or None)
# 本文は content/<slug>.html があればそれを読み込み、無ければ雛形を出力
# ---------------------------------------------------------------
PAGES = [
    ("index", "TOP", None),
    ("jisseki", "実績報告について", None),
    ("jisseki-seikyusho", "請求書（請求明細書）", "jisseki"),
    ("jisseki-software", "ソフトウェアの利用確認", "jisseki"),
    ("jisseki-shiharai", "支払証憑", "jisseki"),
    ("jisseki-kouza", "補助金受取口座", "jisseki"),
    ("jisseki-hw-nouhin", "【ハードウェア導入者】ハードウェアの納品書", "jisseki"),
    ("jisseki-hw-shashin", "【ハードウェア導入者】ハードウェアの写真", "jisseki"),
    ("jisseki-juugyouin", "【小規模事業者】従業員一覧", "jisseki"),
    ("tejun", "実績報告入力手順", None),
    ("tejun-tsujo", "通常枠", "tejun"),
    ("tejun-inv-chusho-pc1-pos1", "インボイス枠｜中小企業｜PC:あり｜POS:あり", "tejun"),
    ("tejun-inv-chusho-pc1-pos0", "インボイス枠｜中小企業｜PC:あり｜POS:なし", "tejun"),
    ("tejun-inv-chusho-pc0-pos1", "インボイス枠｜中小企業｜PC:なし｜POS:あり", "tejun"),
    ("tejun-inv-chusho-pc0-pos0", "インボイス枠｜中小企業｜PC:なし｜POS:なし", "tejun"),
    ("tejun-inv-shokibo-pc1-pos1", "インボイス枠｜小規模事業者｜PC:あり｜POS:あり", "tejun"),
    ("tejun-inv-shokibo-pc1-pos0", "インボイス枠｜小規模事業者｜PC:あり｜POS:なし", "tejun"),
    ("tejun-inv-shokibo-pc0-pos1", "インボイス枠｜小規模事業者｜PC:なし｜POS:あり", "tejun"),
    ("tejun-inv-shokibo-pc0-pos0", "インボイス枠｜小規模事業者｜PC:なし｜POS:なし", "tejun"),
    ("tejun-teishutsu", "全枠共通（事務局への提出）", "tejun"),
]


# サイドバー用の短い表示名（省略したいページのみ指定）
NAV_SHORT = {
    "jisseki-hw-nouhin": "ハードウェアの納品書",
    "jisseki-hw-shashin": "ハードウェアの写真",
    "jisseki-juugyouin": "従業員一覧",
    "tejun-inv-chusho-pc1-pos1": "中小企業｜PC○ POS○",
    "tejun-inv-chusho-pc1-pos0": "中小企業｜PC○ POS✕",
    "tejun-inv-chusho-pc0-pos1": "中小企業｜PC✕ POS○",
    "tejun-inv-chusho-pc0-pos0": "中小企業｜PC✕ POS✕",
    "tejun-inv-shokibo-pc1-pos1": "小規模｜PC○ POS○",
    "tejun-inv-shokibo-pc1-pos0": "小規模｜PC○ POS✕",
    "tejun-inv-shokibo-pc0-pos1": "小規模｜PC✕ POS○",
    "tejun-inv-shokibo-pc0-pos0": "小規模｜PC✕ POS✕",
    "tejun-teishutsu": "事務局への提出",
}

ORDER = [p[0] for p in PAGES]
TITLES = {p[0]: p[1] for p in PAGES}


def url(slug):
    return "index.html" if slug == "index" else slug + ".html"


def build_nav(current):
    parent_of = {p[0]: p[2] for p in PAGES}
    active_section = current if parent_of.get(current) is None else parent_of[current]

    out = ['<nav class="side" aria-label="サイト内メニュー"><ul class="nav-list">']
    for slug, title, parent in PAGES:
        if slug == "index":
            continue
        label = NAV_SHORT.get(slug, title)
        if parent is None:
            open_cls = " open" if slug == active_section else ""
            cur = " current" if slug == current else ""
            aria = ' aria-current="page"' if slug == current else ""
            out.append(
                f'<li class="nav-item top{open_cls}{cur}">'
                f'<a href="{url(slug)}"{aria}>{html.escape(label)}</a>'
            )
            children = [c for c in PAGES if c[2] == slug]
            if children:
                out.append('<ul class="nav-sub">')
                for cs, ct, _ in children:
                    clabel = NAV_SHORT.get(cs, ct)
                    ccur = " current" if cs == current else ""
                    caria = ' aria-current="page"' if cs == current else ""
                    out.append(
                        f'<li class="nav-item sub{ccur}">'
                        f'<a href="{url(cs)}"{caria}>{html.escape(clabel)}</a></li>'
                    )
                out.append("</ul>")
            out.append("</li>")
    out.append("</ul></nav>")
    return "\n".join(out)


def build_prevnext(current):
    i = ORDER.index(current)
    prev_s = ORDER[i - 1] if i > 0 else None
    next_s = ORDER[i + 1] if i < len(ORDER) - 1 else None
    parts = ['<div class="prevnext">']
    if prev_s:
        parts.append(
            f'<a class="pn prev" href="{url(prev_s)}"><span class="pn-dir">前へ</span>'
            f'<span class="pn-title">{html.escape(TITLES[prev_s])}</span></a>'
        )
    else:
        parts.append('<span></span>')
    if next_s:
        parts.append(
            f'<a class="pn next" href="{url(next_s)}"><span class="pn-dir">次へ</span>'
            f'<span class="pn-title">{html.escape(TITLES[next_s])}</span></a>'
        )
    else:
        parts.append('<span></span>')
    parts.append("</div>")
    return "\n".join(parts)


DRAFTS = {
 "jisseki-seikyusho": ("ITツール・ハードウェアの代金を請求した書類です。金額の内訳がわかるものをご用意ください。",
  ["宛名が申請した事業者名と一致していること","日付が交付決定日より後になっていること","品目ごとの内訳と金額が記載されていること","補助対象の品目が判別できること"],
  "金額が交付決定額と異なる場合は、そのままでは受理されません。差額の理由がわかる書類を添えるか、事務局にご相談ください。"),
 "jisseki-software": ("導入したソフトウェアを実際に使い始めていることを示す資料です。管理画面などの画面キャプチャをご用意ください。",
  ["ログイン後の管理画面が写っていること","アカウント名または事業者名が判別できること","撮影日または画面内の日付がわかること","申請したツール名が確認できること"],
  "画面の一部を隠す必要がある場合でも、事業者名とツール名は必ず見える状態にしてください。"),
 "jisseki-shiharai": ("代金を実際に支払ったことを証明する書類です。銀行振込の明細やクレジットカードの利用明細が該当します。",
  ["振込日が確認できること","振込元が申請した事業者の口座であること","振込先が販売事業者と一致していること","金額が請求書と一致していること"],
  "現金払いは原則として認められません。やむを得ない事情がある場合は、事前に事務局へご確認ください。"),
 "jisseki-kouza": ("補助金の振込先となる口座の情報です。通帳やネットバンキングの画面をご用意ください。",
  ["金融機関名と支店名が確認できること","口座種別と口座番号が確認できること","口座名義が申請した事業者名と一致していること","名義がカタカナで確認できること"],
  "屋号付き口座の場合、申請書の事業者名と表記が異なると差し戻しになることがあります。事前にご確認ください。"),
 "jisseki-hw-nouhin": ("ハードウェアが納品されたことを示す書類です。ハードウェアを導入した方のみ提出します。",
  ["納品日が交付決定日より後になっていること","型番または製品名が記載されていること","数量が申請内容と一致していること","納品先が申請した事業者であること"],
  "ハードウェアを導入していない場合、このページの書類は不要です。次に進んでください。"),
 "jisseki-hw-shashin": ("納品されたハードウェアが設置され、使える状態にあることを示す写真です。",
  ["製品の全体が写っていること","型番のラベルまたはシールが読み取れること","設置場所の様子がわかること","申請した数量分すべてが確認できること"],
  "型番が読み取れない写真は再提出になります。ラベル部分を近くから撮った写真も併せてご用意ください。"),
 "jisseki-juugyouin": ("小規模事業者として申請した方が、要件を満たしていることを示す書類です。",
  ["常時使用する従業員の人数が確認できること","業種区分に応じた上限を超えていないこと","作成日が記載されていること","事業者名が申請内容と一致していること"],
  "小規模事業者として申請していない場合、この書類は不要です。役員や個人事業主本人は従業員数に含みません。"),
}

def placeholder(slug, title):
    d = DRAFTS.get(slug)
    if d:
        lead, checks, note = d
        items = "\n".join(f"  <li>{c}</li>" for c in checks)
        return f"""<p class="lead">{lead}</p>

<h2>提出前のチェック</h2>
<ul class="checks">
{items}
</ul>

<div class="callout">
  <strong>注意</strong>
  <p>{note}</p>
</div>

<div class="note-box">
  <strong>この先の作業</strong>
  <p>Googleサイトから記載例の画像を移してください。画像は <code>assets/img/</code> に置き、<code>&lt;figure&gt;</code> で囲むと説明文を付けられます。</p>
</div>"""

    return f"""<p class="lead">申請システムへの入力手順です。画面の順に沿って進めてください。</p>

<h2>入力の流れ</h2>
<ol class="steps">
  <li>
    <h3>マイページにログインする</h3>
    <p>gBizIDでログインします。</p>
  </li>
  <li>
    <h3>実績報告を開く</h3>
    <p>該当する交付決定番号を選びます。</p>
  </li>
  <li>
    <h3>書類をアップロードする</h3>
    <p>用意した書類を項目ごとに添付します。</p>
  </li>
</ol>

<div class="note-box">
  <strong>この先の作業</strong>
  <p>Googleサイトから、この枠の画面キャプチャと説明をここに移してください。<code>content/{slug}.html</code> を編集します。</p>
</div>"""


TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | 補助金ガイド</title>
<meta name="description" content="{title}に関するご案内。">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<a class="skip" href="#main">本文へ移動</a>

<header class="masthead">
  <div class="masthead-inner">
    <a class="brand" href="index.html">
      <span class="brand-name">補助金ガイド</span>
      <span class="brand-sub">実績報告</span>
    </a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="sidebar">
      <span class="nav-toggle-bars" aria-hidden="true"></span>目次
    </button>
  </div>
</header>

<div class="shell">
  <aside id="sidebar" class="sidebar">
{nav}
  </aside>

  <main id="main" class="main">
    <div class="page-head">
      <p class="eyebrow">{eyebrow}</p>
      <h1>{title}</h1>
    </div>
    <div class="body">
{content}
    </div>
{prevnext}
  </main>
</div>

<footer class="foot">
  <div class="foot-inner">
    <p>本サイトの内容は、独立行政法人中小企業基盤整備機構および経済産業省が公表する公式情報をもとに作成しています。制度の最新情報や詳細は<a href="https://it-shien.smrj.go.jp/" target="_blank" rel="noopener">公式サイト</a>をご確認ください。</p>
  </div>
</footer>

<script src="assets/site.js"></script>
</body>
</html>
"""

CSS = """:root{
  --paper:#faf7f0;
  --panel:#fffdf8;
  --ink:#3a352c;
  --ink-mid:#6e6759;
  --ink-light:#9c9484;
  --rule:#e3ddd0;
  --rule-soft:#efeae0;
  --leaf:#6d8b52;
  --leaf-pale:#eef2e6;
  --leaf-deep:#4e6a3a;
  --apricot:#d9a05b;
  --apricot-pale:#fbf1e2;
  --clay:#b5654a;
  --r:14px;
  --measure:34em;
}
*{box-sizing:border-box}
body{
  margin:0;background:var(--paper);color:var(--ink);
  font-family:"Hiragino Maru Gothic ProN","Hiragino Kaku Gothic ProN","Yu Gothic Medium","Yu Gothic",Meiryo,system-ui,sans-serif;
  font-size:16px;line-height:1.95;
  font-feature-settings:"palt" 1;
  -webkit-font-smoothing:antialiased;
}
a{color:var(--leaf-deep);text-underline-offset:.22em;text-decoration-color:#cfd9c2}
a:hover{text-decoration-color:var(--leaf)}
:focus-visible{outline:2px solid var(--leaf);outline-offset:3px;border-radius:4px}
.skip{position:absolute;left:-9999px}
.skip:focus{left:16px;top:16px;background:var(--panel);padding:12px 18px;z-index:30;border-radius:8px}

/* ---------- ヘッダー ---------- */
.masthead{
  background:rgba(250,247,240,.92);backdrop-filter:blur(8px);
  border-bottom:1px solid var(--rule);position:sticky;top:0;z-index:20;
}
.masthead-inner{
  max-width:1060px;margin:0 auto;padding:0 40px;
  height:70px;display:flex;align-items:center;justify-content:space-between;
}
.brand{display:flex;align-items:center;gap:11px;text-decoration:none}
.brand::before{
  content:"";width:26px;height:26px;border-radius:9px;flex:none;
  background:var(--leaf-pale);border:1.5px solid var(--leaf);
  background-image:linear-gradient(135deg,transparent 46%,var(--leaf) 46%,var(--leaf) 54%,transparent 54%);
}
.brand-name{font-size:16px;font-weight:700;letter-spacing:.1em;color:var(--ink)}
.brand-sub{
  font-size:11px;letter-spacing:.14em;color:var(--leaf-deep);
  background:var(--leaf-pale);padding:3px 9px;border-radius:999px;
}
.nav-toggle{
  display:none;align-items:center;gap:8px;background:var(--panel);
  border:1px solid var(--rule);border-radius:999px;
  font:inherit;font-size:13px;color:var(--ink);cursor:pointer;padding:8px 16px;
}
.nav-toggle-bars{width:14px;height:1.5px;background:var(--ink);border-radius:2px;box-shadow:0 5px var(--ink),0 -5px var(--ink)}

/* ---------- レイアウト ---------- */
.shell{
  max-width:1060px;margin:0 auto;padding:52px 40px 96px;
  display:grid;grid-template-columns:206px minmax(0,1fr);gap:64px;
}

/* ---------- 目次 ---------- */
.sidebar{position:sticky;top:110px;align-self:start;max-height:calc(100vh - 150px);overflow-y:auto}
.sidebar::-webkit-scrollbar{width:3px}
.sidebar::-webkit-scrollbar-thumb{background:var(--rule);border-radius:3px}
.nav-list,.nav-sub{list-style:none;margin:0;padding:0}
.nav-item a{display:block;text-decoration:none;line-height:1.55;border-radius:9px}
.nav-item.top{margin-top:10px}
.nav-item.top>a{
  font-size:13.5px;letter-spacing:.04em;color:var(--ink);font-weight:700;
  padding:9px 12px;
}
.nav-item.top>a:hover{background:var(--panel)}
.nav-item.top.open>a{background:var(--leaf-pale);color:var(--leaf-deep)}
.nav-sub{display:none;margin:4px 0 4px 12px;padding-left:11px;border-left:1.5px solid var(--rule-soft)}
.nav-item.top.open>.nav-sub{display:block}
.nav-item.sub a{
  font-size:12.5px;color:var(--ink-light);padding:6px 10px;letter-spacing:.01em;
}
.nav-item.sub a:hover{color:var(--ink);background:var(--panel)}
.nav-item.sub.current a{
  color:var(--leaf-deep);font-weight:700;background:var(--leaf-pale);
}
.nav-item.top.current>a{background:var(--leaf-pale);color:var(--leaf-deep)}

/* ---------- 本文 ---------- */
.main{min-width:0}
.page-head{margin-bottom:40px}
.eyebrow{
  display:inline-block;margin:0 0 14px;font-size:11.5px;letter-spacing:.1em;
  color:var(--leaf-deep);background:var(--leaf-pale);
  padding:5px 12px;border-radius:999px;
}
h1{
  margin:0;font-size:27px;font-weight:700;line-height:1.55;
  letter-spacing:.02em;max-width:var(--measure);
}
.body{max-width:var(--measure)}
.body:has(.gsite-embed){max-width:52em}
.body>*:first-child{margin-top:0}
.lead{
  font-size:15.5px;color:var(--ink-mid);line-height:1.95;margin:0 0 38px;
}
.lead-strong{
  font-size:18px;font-weight:700;color:var(--ink);line-height:1.7;margin:0 0 12px;
}
h2{
  margin:56px 0 18px;font-size:17.5px;font-weight:700;letter-spacing:.03em;
  line-height:1.6;display:flex;align-items:center;gap:10px;
}
.body>h2::before{
  content:"";width:7px;height:7px;border-radius:50%;
  background:var(--leaf);flex:none;
}
.gsite-embed{
  margin:0 0 40px;padding:8px 0;
}
.gsite-embed > div[style]{
  max-width:100%!important;margin:0!important;
  background:var(--panel)!important;border:1px solid var(--rule);
  border-radius:var(--r);overflow:auto;
}
.gsite-embed table{font-size:13px}
.gsite-embed img{max-width:100%;height:auto}
h3{margin:32px 0 10px;font-size:15px;font-weight:700;letter-spacing:.02em}
p{margin:0 0 20px}
ul,ol{padding-left:1.35em;margin:0 0 22px}
li{margin-bottom:9px}
li::marker{color:var(--leaf)}
strong{font-weight:700}
code{
  font-family:"SFMono-Regular",Consolas,monospace;font-size:13px;
  background:var(--rule-soft);padding:2px 7px;border-radius:5px;
}

/* ---------- 図版 ---------- */
.body img{max-width:100%;height:auto;display:block;margin:28px 0;border-radius:var(--r)}
figure{margin:28px 0}
figure img{margin:0}
figcaption{font-size:12.5px;color:var(--ink-light);margin-top:10px}

/* ---------- 表 ---------- */
.body table{
  width:100%;border-collapse:separate;border-spacing:0;margin:28px 0;
  font-size:14px;line-height:1.75;background:var(--panel);
  border:1px solid var(--rule);border-radius:var(--r);overflow:hidden;
}
.body th,.body td{padding:14px 16px;text-align:left;vertical-align:top}
.body th{
  font-weight:700;font-size:12.5px;letter-spacing:.06em;
  color:var(--leaf-deep);background:var(--leaf-pale);
}
.body tbody tr+tr td{border-top:1px solid var(--rule-soft)}

/* ---------- 注記 ---------- */
.callout{
  margin:28px 0;padding:20px 22px;background:var(--apricot-pale);
  border-radius:var(--r);border:1px solid #f0e0c6;
}
.callout strong{
  display:flex;align-items:center;gap:7px;font-size:13px;
  color:#8a5a24;margin-bottom:7px;font-weight:700;
}
.callout strong::before{
  content:"!";display:grid;place-items:center;width:17px;height:17px;
  border-radius:50%;background:var(--apricot);color:#fff;font-size:11px;flex:none;
}
.callout p{margin:0;font-size:14.5px;color:#6d5636;line-height:1.85}
.callout p+p{margin-top:8px}

.note-box{
  margin:28px 0;padding:20px 22px;background:var(--leaf-pale);
  border-radius:var(--r);border:1px solid #dce5cd;
}
.note-box strong{display:block;font-size:13px;color:var(--leaf-deep);margin-bottom:7px}
.note-box p,.note-box ul{margin:0;font-size:14.5px;color:#4f5a41;line-height:1.85}
.note-box ul{padding-left:1.2em}

/* ---------- 手順 ---------- */
.steps{list-style:none;padding:0;margin:28px 0;counter-reset:step}
.steps>li{
  counter-increment:step;position:relative;
  padding:20px 22px 20px 60px;margin:0 0 12px;
  background:var(--panel);border:1px solid var(--rule);border-radius:var(--r);
}
.steps>li::before{
  content:counter(step);position:absolute;left:20px;top:21px;
  width:26px;height:26px;border-radius:50%;
  background:var(--leaf);color:#fff;
  display:grid;place-items:center;font-size:13px;font-weight:700;line-height:1;
}
.steps h3{margin:0 0 5px;font-size:15px}
.steps p{margin:0;font-size:14.5px;color:var(--ink-mid)}
.steps p+p{margin-top:8px}

/* ---------- チェックリスト ---------- */
.checks{list-style:none;padding:0;margin:24px 0}
.checks li{
  position:relative;padding:11px 0 11px 32px;margin:0;
  border-bottom:1px dashed var(--rule);font-size:15px;
}
.checks li:last-child{border-bottom:none}
.checks li::before{
  content:"";position:absolute;left:2px;top:17px;
  width:16px;height:16px;border-radius:5px;
  border:1.5px solid var(--leaf);background:var(--leaf-pale);
}
.checks li::after{
  content:"";position:absolute;left:7px;top:21px;
  width:5px;height:9px;border:solid var(--leaf);
  border-width:0 2px 2px 0;transform:rotate(45deg);
}

/* ---------- 目次カード ---------- */
.cards{list-style:none;padding:0;margin:28px 0;display:grid;gap:10px}
.cards li{margin:0}
.cards a{
  display:flex;align-items:center;gap:14px;
  padding:18px 20px;background:var(--panel);
  border:1px solid var(--rule);border-radius:var(--r);
  text-decoration:none;font-size:15px;font-weight:700;color:var(--ink);
  transition:transform .12s ease,border-color .12s ease;
}
.cards a:hover{border-color:var(--leaf);transform:translateY(-1px)}
.cards a::after{
  content:"";margin-left:auto;flex:none;width:7px;height:7px;
  border:solid var(--leaf);border-width:0 1.8px 1.8px 0;transform:rotate(-45deg);
}
.cards .note{
  font-size:12px;font-weight:400;color:var(--leaf-deep);
  background:var(--leaf-pale);padding:3px 10px;border-radius:999px;
}

/* ---------- 前後ナビ ---------- */
.prevnext{
  display:flex;justify-content:space-between;gap:14px;margin-top:72px;
}
.pn{
  display:flex;flex-direction:column;gap:5px;text-decoration:none;
  max-width:47%;padding:15px 20px;background:var(--panel);
  border:1px solid var(--rule);border-radius:var(--r);
}
.pn:hover{border-color:var(--leaf)}
.pn.next{margin-left:auto;text-align:right}
.pn-dir{font-size:11.5px;color:var(--leaf-deep);font-weight:700}
.pn-title{font-size:14px;color:var(--ink);line-height:1.6}

/* ---------- フッター ---------- */
.foot{border-top:1px solid var(--rule);padding:36px 0 52px;background:var(--panel)}
.foot-inner{max-width:1060px;margin:0 auto;padding:0 40px}
.foot p{margin:0;font-size:12.5px;line-height:1.9;color:var(--ink-light);max-width:46em}

/* ---------- モバイル ---------- */
@media (max-width:880px){
  .masthead-inner{padding:0 20px;height:62px}
  .shell{grid-template-columns:1fr;gap:0;padding:28px 20px 64px}
  .sidebar{
    position:static;max-height:none;display:none;
    margin-bottom:28px;padding-bottom:20px;border-bottom:1px solid var(--rule);
  }
  .sidebar.open{display:block}
  .nav-toggle{display:flex}
  h1{font-size:22px}
  h2{font-size:16px;margin:44px 0 16px}
  .prevnext{flex-direction:column;gap:10px;margin-top:56px}
  .pn,.pn.next{max-width:100%;text-align:left;margin-left:0}
  .foot-inner{padding:0 20px}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
"""

JS = """(function(){
  var btn=document.querySelector('.nav-toggle');
  var side=document.getElementById('sidebar');
  if(!btn||!side)return;
  btn.addEventListener('click',function(){
    var open=side.classList.toggle('open');
    btn.setAttribute('aria-expanded',String(open));
  });
})();
"""


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, "assets", "img"), exist_ok=True)
    os.makedirs("content", exist_ok=True)

    with open(os.path.join(OUT, "assets", "style.css"), "w", encoding="utf-8") as f:
        f.write(CSS)
    with open(os.path.join(OUT, "assets", "site.js"), "w", encoding="utf-8") as f:
        f.write(JS)
    open(os.path.join(OUT, ".nojekyll"), "w").close()

    for slug, title, parent in PAGES:
        cpath = os.path.join("content", slug + ".html")
        if os.path.exists(cpath):
            with open(cpath, encoding="utf-8") as f:
                content = f.read()
        else:
            content = placeholder(slug, title)
            with open(cpath, "w", encoding="utf-8") as f:
                f.write(content)

        eyebrow = TITLES[parent] if parent else "補助金ガイド"
        page = TEMPLATE.format(
            title=html.escape(title),
            eyebrow=html.escape(eyebrow),
            nav=build_nav(slug),
            content=content,
            prevnext=build_prevnext(slug),
        )
        with open(os.path.join(OUT, url(slug)), "w", encoding="utf-8") as f:
            f.write(page)

    print("built %d pages -> %s/" % (len(PAGES), OUT))


if __name__ == "__main__":
    main()
