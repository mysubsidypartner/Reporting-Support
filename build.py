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
    ("index", "はじめに", None),
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

    out = [
        '<nav class="side" aria-label="サイト内メニュー">',
        '<p class="nav-label">目次</p>',
        '<ul class="nav-list">',
    ]
    # TOP
    top_cur = " current" if current == "index" else ""
    top_aria = ' aria-current="page"' if current == "index" else ""
    out.append(
        f'<li class="nav-item home{top_cur}">'
        f'<a href="{url("index")}"{top_aria}>はじめに</a></li>'
    )
    for slug, title, parent in PAGES:
        if slug == "index" or parent is not None:
            continue
        label = NAV_SHORT.get(slug, title)
        active = " active" if slug == active_section else ""
        cur = " current" if slug == current else ""
        aria = ' aria-current="page"' if slug == current else ""
        out.append(
            f'<li class="nav-item top{active}{cur}">'
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
<title>{title} | 補助金ガイド｜実績報告のご案内</title>
<meta name="description" content="IT導入補助金の実績報告に必要な書類と申請手順のご案内。{title}">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<a class="skip" href="#main">本文へ移動</a>

<header class="masthead">
  <div class="masthead-inner">
    <a class="brand" href="index.html">
      <span class="brand-name">補助金ガイド</span>
      <span class="brand-sub">実績報告のご案内</span>
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
      <p class="breadcrumb">{eyebrow}</p>
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
  --bg:#f5f7fa;
  --surface:#ffffff;
  --ink:#1f2937;
  --ink-mid:#4b5563;
  --ink-light:#6b7280;
  --rule:#e5e7eb;
  --rule-soft:#eef1f5;
  --brand:#0b5394;
  --brand-soft:#e8f1f8;
  --brand-mid:#0d6aad;
  --warn:#9a3412;
  --warn-bg:#fff7ed;
  --warn-border:#fed7aa;
  --measure:44em;
  --sidebar:240px;
  --shell:1120px;
}
*{box-sizing:border-box}
body{
  margin:0;background:var(--bg);color:var(--ink);
  font-family:"Hiragino Kaku Gothic ProN","Hiragino Sans","Yu Gothic Medium","Yu Gothic",Meiryo,sans-serif;
  font-size:15px;line-height:1.85;
  font-feature-settings:"palt" 1;
  -webkit-font-smoothing:antialiased;
}
a{color:var(--brand);text-underline-offset:.2em}
a:hover{color:var(--brand-mid)}
:focus-visible{outline:2px solid var(--brand);outline-offset:2px}
.skip{position:absolute;left:-9999px}
.skip:focus{left:16px;top:16px;background:var(--surface);padding:10px 14px;z-index:30;border:1px solid var(--rule)}

/* ---------- ヘッダー ---------- */
.masthead{
  background:var(--surface);border-bottom:1px solid var(--rule);
  position:sticky;top:0;z-index:20;
}
.masthead-inner{
  max-width:var(--shell);margin:0 auto;padding:0 32px;
  height:56px;display:flex;align-items:center;justify-content:space-between;
}
.brand{display:flex;align-items:baseline;gap:12px;text-decoration:none;color:inherit}
.brand-name{font-size:15px;font-weight:700;letter-spacing:.04em;color:var(--ink)}
.brand-sub{font-size:12px;color:var(--ink-light);letter-spacing:.02em}
.nav-toggle{
  display:none;align-items:center;gap:8px;background:var(--surface);
  border:1px solid var(--rule);font:inherit;font-size:13px;color:var(--ink);
  cursor:pointer;padding:7px 12px;
}
.nav-toggle-bars{width:14px;height:1.5px;background:var(--ink);box-shadow:0 5px var(--ink),0 -5px var(--ink)}

/* ---------- レイアウト ---------- */
.shell{
  max-width:var(--shell);margin:0 auto;padding:28px 32px 72px;
  display:grid;grid-template-columns:var(--sidebar) minmax(0,1fr);gap:40px;
}

/* ---------- 目次 ---------- */
.sidebar{
  position:sticky;top:72px;align-self:start;
  max-height:calc(100vh - 96px);overflow-y:auto;
  background:var(--surface);border:1px solid var(--rule);padding:16px 0 20px;
}
.sidebar::-webkit-scrollbar{width:4px}
.sidebar::-webkit-scrollbar-thumb{background:#d1d5db}
.nav-label{
  margin:0 16px 10px;font-size:11px;font-weight:700;
  letter-spacing:.12em;color:var(--ink-light);text-transform:uppercase;
}
.nav-list,.nav-sub{list-style:none;margin:0;padding:0}
.nav-item a{
  display:block;text-decoration:none;color:var(--ink-mid);line-height:1.45;
}
.nav-item.home a,
.nav-item.top>a{
  padding:8px 16px;font-size:13px;font-weight:700;color:var(--ink);
}
.nav-item.home a:hover,
.nav-item.top>a:hover{background:var(--rule-soft);color:var(--brand)}
.nav-item.home.current a,
.nav-item.top.current>a,
.nav-item.top.active>a{
  color:var(--brand);background:var(--brand-soft);
  box-shadow:inset 3px 0 0 var(--brand);
}
.nav-sub{margin:2px 0 10px;padding:0}
.nav-item.sub a{
  padding:5px 16px 5px 28px;font-size:12.5px;color:var(--ink-light);
}
.nav-item.sub a:hover{color:var(--brand);background:var(--rule-soft)}
.nav-item.sub.current a{
  color:var(--brand);font-weight:700;background:var(--brand-soft);
  box-shadow:inset 3px 0 0 var(--brand);
}

/* ---------- 本文 ---------- */
.main{min-width:0;background:var(--surface);border:1px solid var(--rule);padding:32px 40px 48px}
.page-head{
  margin:0 0 28px;padding:0 0 20px;border-bottom:1px solid var(--rule);
}
.breadcrumb{
  margin:0 0 8px;font-size:12px;color:var(--ink-light);letter-spacing:.02em;
}
h1{
  margin:0;font-size:24px;font-weight:700;line-height:1.45;
  letter-spacing:.02em;color:var(--ink);
}
.body{max-width:var(--measure)}
.body>*:first-child{margin-top:0}
.lead{
  font-size:15px;color:var(--ink-mid);line-height:1.85;margin:0 0 24px;
}
.lead-strong{
  font-size:16px;font-weight:700;color:var(--ink);line-height:1.7;margin:0 0 8px;
}
.body>h2{
  margin:40px 0 14px;padding:0 0 8px;border-bottom:1px solid var(--rule);
  font-size:16px;font-weight:700;letter-spacing:.02em;line-height:1.5;
  color:var(--ink);
}
h3{margin:28px 0 8px;font-size:14.5px;font-weight:700;color:var(--ink)}
p{margin:0 0 16px}
ul,ol{padding-left:1.35em;margin:0 0 18px}
li{margin-bottom:6px}
strong{font-weight:700}
code{
  font-family:"SFMono-Regular",Consolas,monospace;font-size:12.5px;
  background:var(--rule-soft);padding:1px 6px;border:1px solid var(--rule);
}

/* Googleサイトから移植した埋め込みをサイトに馴染ませる */
.gsite-embed{margin:0 0 28px}
.gsite-embed > div[style]{
  max-width:100%!important;margin:0!important;padding:0!important;
  background:transparent!important;font-family:inherit!important;
}
.gsite-embed h1,.gsite-embed h2{
  font-family:inherit!important;color:var(--ink)!important;
}
.gsite-embed .step-box{border-left-color:var(--brand)!important}
.gsite-embed .step-label{color:var(--brand)!important}
.gsite-embed .step-button{
  border-color:var(--brand)!important;color:var(--brand)!important;
}
.gsite-embed .step-button:hover{
  background:var(--brand)!important;color:#fff!important;
}
.gsite-embed details{
  background:var(--brand-soft)!important;border-left-color:var(--brand)!important;
}
.gsite-embed summary{color:var(--brand)!important}
.gsite-embed table{font-size:13px;width:100%}
.gsite-embed img{max-width:100%;height:auto}

/* ---------- 図版 ---------- */
.body img{max-width:100%;height:auto;display:block;margin:20px 0;border:1px solid var(--rule)}
figure{margin:20px 0}
figure img{margin:0}
figcaption{font-size:12px;color:var(--ink-light);margin-top:8px}

/* ---------- 表 ---------- */
.body table{
  width:100%;border-collapse:collapse;margin:20px 0;
  font-size:13.5px;line-height:1.7;background:var(--surface);
  border:1px solid var(--rule);
}
.body th,.body td{padding:10px 12px;text-align:left;vertical-align:top;border-bottom:1px solid var(--rule)}
.body th{
  font-weight:700;font-size:12px;letter-spacing:.04em;
  color:var(--brand);background:var(--brand-soft);border-bottom:1px solid var(--rule);
}

/* ---------- 注記 ---------- */
.callout{
  margin:20px 0;padding:14px 16px;background:var(--warn-bg);
  border:1px solid var(--warn-border);border-left:3px solid #ea580c;
}
.callout strong{
  display:block;font-size:12.5px;color:var(--warn);margin-bottom:4px;font-weight:700;
}
.callout p{margin:0;font-size:13.5px;color:#7c2d12;line-height:1.75}
.callout p+p{margin-top:6px}

.note-box{
  margin:20px 0;padding:14px 16px;background:var(--brand-soft);
  border:1px solid #c9dceb;border-left:3px solid var(--brand);
}
.note-box strong{display:block;font-size:12.5px;color:var(--brand);margin-bottom:4px}
.note-box p,.note-box ul{margin:0;font-size:13.5px;color:#1e3a5f;line-height:1.75}
.note-box ul{padding-left:1.2em}

/* ---------- 手順 ---------- */
.steps{list-style:none;padding:0;margin:20px 0;counter-reset:step;border:1px solid var(--rule)}
.steps>li{
  counter-increment:step;position:relative;
  padding:16px 16px 16px 56px;margin:0;
  border-bottom:1px solid var(--rule);background:var(--surface);
}
.steps>li:last-child{border-bottom:none}
.steps>li::before{
  content:counter(step);position:absolute;left:16px;top:16px;
  width:24px;height:24px;
  background:var(--brand);color:#fff;
  display:grid;place-items:center;font-size:12px;font-weight:700;line-height:1;
}
.steps h3{margin:0 0 4px;font-size:14.5px}
.steps p{margin:0;font-size:13.5px;color:var(--ink-mid)}
.steps p+p{margin-top:6px}

/* ---------- チェックリスト ---------- */
.checks{list-style:none;padding:0;margin:16px 0;border:1px solid var(--rule)}
.checks li{
  position:relative;padding:10px 14px 10px 40px;margin:0;
  border-bottom:1px solid var(--rule);font-size:14px;background:var(--surface);
}
.checks li:last-child{border-bottom:none}
.checks li::before{
  content:"";position:absolute;left:14px;top:14px;
  width:14px;height:14px;border:1.5px solid var(--brand);background:#fff;
}
.checks li::after{
  content:"";position:absolute;left:18px;top:17px;
  width:5px;height:8px;border:solid var(--brand);
  border-width:0 2px 2px 0;transform:rotate(45deg);
}

/* ---------- 目次カード ---------- */
.cards{list-style:none;padding:0;margin:16px 0;border:1px solid var(--rule)}
.cards li{margin:0;border-bottom:1px solid var(--rule)}
.cards li:last-child{border-bottom:none}
.cards a{
  display:flex;align-items:center;gap:12px;
  padding:12px 14px;background:var(--surface);
  text-decoration:none;font-size:14px;font-weight:600;color:var(--ink);
}
.cards a:hover{background:var(--brand-soft);color:var(--brand)}
.cards a::after{
  content:"›";margin-left:auto;flex:none;color:var(--ink-light);font-size:16px;font-weight:400;
}
.cards .note{
  font-size:11.5px;font-weight:400;color:var(--ink-light);
  border:1px solid var(--rule);padding:2px 8px;background:var(--bg);
}

/* ---------- 前後ナビ ---------- */
.prevnext{
  display:flex;justify-content:space-between;gap:12px;
  margin-top:40px;padding-top:20px;border-top:1px solid var(--rule);
}
.pn{
  display:flex;flex-direction:column;gap:3px;text-decoration:none;
  max-width:47%;padding:12px 14px;background:var(--bg);border:1px solid var(--rule);
  color:inherit;
}
.pn:hover{border-color:var(--brand);background:var(--brand-soft)}
.pn.next{margin-left:auto;text-align:right}
.pn-dir{font-size:11px;color:var(--brand);font-weight:700}
.pn-title{font-size:13.5px;color:var(--ink);line-height:1.5}

/* ---------- フッター ---------- */
.foot{border-top:1px solid var(--rule);padding:24px 0 40px;background:var(--surface)}
.foot-inner{max-width:var(--shell);margin:0 auto;padding:0 32px}
.foot p{margin:0;font-size:12px;line-height:1.8;color:var(--ink-light);max-width:52em}

/* ---------- モバイル ---------- */
@media (max-width:900px){
  .masthead-inner{padding:0 16px;height:52px}
  .shell{grid-template-columns:1fr;gap:0;padding:16px 16px 48px}
  .sidebar{
    position:static;max-height:none;display:none;margin-bottom:16px;
  }
  .sidebar.open{display:block}
  .nav-toggle{display:flex}
  .main{padding:22px 18px 32px}
  h1{font-size:20px}
  .body>h2{font-size:15px;margin:32px 0 12px}
  .prevnext{flex-direction:column;gap:8px}
  .pn,.pn.next{max-width:100%;text-align:left;margin-left:0}
  .foot-inner{padding:0 16px}
  .brand-sub{display:none}
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

        eyebrow = TITLES[parent] if parent else "実績報告のご案内"
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
