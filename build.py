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
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap" rel="stylesheet">
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
  <p class="masthead-notice">本サイトの無断転載・無断複製・無断転用・第三者への再配布を固く禁じます。</p>
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
  --bg:#f3f5f8;
  --surface:#ffffff;
  --ink:#152033;
  --ink-mid:#3d4a5c;
  --ink-light:#6b7789;
  --rule:#e2e7ee;
  --rule-soft:#eef2f7;
  --brand:#0b5394;
  --brand-soft:#eaf2f9;
  --brand-mid:#0d6aad;
  --warn:#9a3412;
  --warn-bg:#fff8f1;
  --warn-border:#f0d2b0;
  --measure:40rem;
  --sidebar:250px;
  --shell:1140px;
}
*{box-sizing:border-box}
body{
  margin:0;background:var(--bg);color:var(--ink);
  font-family:"Noto Sans JP","Hiragino Kaku Gothic ProN","Hiragino Sans","Yu Gothic Medium",Meiryo,sans-serif;
  font-size:15px;line-height:1.8;font-weight:400;
  -webkit-font-smoothing:antialiased;
}
a{color:var(--brand);text-underline-offset:.18em}
a:hover{color:var(--brand-mid)}
:focus-visible{outline:2px solid var(--brand);outline-offset:2px}
.skip{position:absolute;left:-9999px}
.skip:focus{left:16px;top:16px;background:var(--surface);padding:10px 14px;z-index:30;border:1px solid var(--rule)}

.masthead{background:var(--surface);border-bottom:1px solid var(--rule);position:sticky;top:0;z-index:20}
.masthead-inner{max-width:var(--shell);margin:0 auto;padding:0 28px;height:58px;display:flex;align-items:center;justify-content:space-between}
.brand{display:flex;align-items:baseline;gap:14px;text-decoration:none;color:inherit}
.brand-name{font-size:15px;font-weight:700;letter-spacing:.06em;color:var(--ink);padding-left:12px;border-left:3px solid var(--brand)}
.brand-sub{font-size:12px;color:var(--ink-light);font-weight:500}
.masthead-notice{
  margin:0;padding:8px 28px;border-top:1px solid var(--warn-border);
  background:var(--warn-bg);color:var(--warn);font-size:12px;font-weight:600;line-height:1.5;
  text-align:center;
}
.masthead-notice::before{content:"⚠️ ";}
.nav-toggle{display:none;align-items:center;gap:8px;background:var(--surface);border:1px solid var(--rule);font:inherit;font-size:13px;color:var(--ink);cursor:pointer;padding:7px 12px}
.nav-toggle-bars{width:14px;height:1.5px;background:var(--ink);box-shadow:0 5px var(--ink),0 -5px var(--ink)}

.shell{max-width:var(--shell);margin:0 auto;padding:24px 28px 64px;display:grid;grid-template-columns:var(--sidebar) minmax(0,1fr);gap:24px;align-items:start}

.sidebar{position:sticky;top:98px;align-self:start;max-height:calc(100vh - 122px);overflow-y:auto;background:var(--surface);border:1px solid var(--rule)}
.sidebar::-webkit-scrollbar{width:4px}
.sidebar::-webkit-scrollbar-thumb{background:#c9d2de}
.nav-label{margin:0;padding:14px 16px 8px;font-size:11px;font-weight:700;letter-spacing:.14em;color:var(--ink-light)}
.nav-list,.nav-sub{list-style:none;margin:0;padding:0}
.nav-item a{display:block;text-decoration:none;color:var(--ink-mid);line-height:1.4}
.nav-item.home a,.nav-item.top>a{padding:9px 16px;font-size:13px;font-weight:700;color:var(--ink)}
.nav-item.home a:hover,.nav-item.top>a:hover{background:var(--rule-soft);color:var(--brand)}
.nav-item.home.current a,.nav-item.top.current>a,.nav-item.top.active>a{color:var(--brand);background:var(--brand-soft);box-shadow:inset 3px 0 0 var(--brand)}
.nav-sub{margin:0 0 8px;padding:0 0 4px}
.nav-item.sub a{padding:5px 16px 5px 28px;font-size:12.5px;color:var(--ink-light)}
.nav-item.sub a:hover{color:var(--brand);background:var(--rule-soft)}
.nav-item.sub.current a{color:var(--brand);font-weight:700;background:var(--brand-soft);box-shadow:inset 3px 0 0 var(--brand)}

.main{min-width:0;background:var(--surface);border:1px solid var(--rule);padding:36px 44px 48px}
.page-head{margin:0 0 28px;padding:0 0 18px;border-bottom:1px solid var(--rule)}
.breadcrumb{margin:0 0 6px;font-size:12px;color:var(--ink-light);font-weight:500}
h1{margin:0;font-size:26px;font-weight:700;line-height:1.4;letter-spacing:.01em;color:var(--ink)}
.body{max-width:var(--measure)}
.body>*:first-child{margin-top:0}
.lead{font-size:15px;color:var(--ink-mid);line-height:1.85;margin:0 0 28px}
.lead-strong{font-size:16px;font-weight:700;color:var(--ink);line-height:1.7;margin:0 0 8px}
.body>h2{margin:40px 0 14px;padding:0 0 8px;border-bottom:1px solid var(--rule);font-size:15px;font-weight:700;letter-spacing:.04em;line-height:1.5;color:var(--ink)}
h3{margin:24px 0 8px;font-size:14.5px;font-weight:700;color:var(--ink)}
p{margin:0 0 14px}
ul,ol{padding-left:1.3em;margin:0 0 16px}
li{margin-bottom:5px}
strong{font-weight:700}
code{font-family:"SFMono-Regular",Consolas,monospace;font-size:12.5px;background:var(--rule-soft);padding:1px 6px;border:1px solid var(--rule)}
.source{font-size:12px;color:var(--ink-light);margin-top:10px}
.item-note{display:block;margin-top:4px;font-size:12.5px;font-weight:400;color:#b42318;line-height:1.6}

.timeline{list-style:none;padding:0;margin:8px 0 28px;border-left:2px solid var(--rule)}
.timeline>li{position:relative;padding:0 0 28px 28px;margin:0}
.timeline>li:last-child{padding-bottom:0}
.tl-step{position:absolute;left:-13px;top:0;width:24px;height:24px;background:var(--brand);color:#fff;border:2px solid var(--surface);display:grid;place-items:center;font-size:11px;font-weight:700;line-height:1}
.tl-body h3{margin:2px 0 6px;font-size:15px}
.tl-body p{margin:0 0 10px;font-size:14px;color:var(--ink-mid)}
.tl-body .callout,.tl-body .panel{margin-top:10px}

.panel{margin:12px 0;padding:0;background:var(--brand-soft);border:1px solid #cfdfea}
.panel>summary{list-style:none;cursor:pointer;padding:12px 14px;font-size:13.5px;font-weight:700;color:var(--brand)}
.panel>summary::-webkit-details-marker{display:none}
.panel>summary::before{content:"+ ";font-weight:700}
.panel[open]>summary::before{content:"− "}
.panel>summary+*{padding:0 14px 14px}
.panel ol,.panel ul{margin:0}

.btn{display:inline-flex;align-items:center;gap:6px;padding:10px 16px;font-size:13.5px;font-weight:700;text-decoration:none;color:#fff;background:var(--brand);border:1px solid var(--brand)}
.btn:hover{background:var(--brand-mid);color:#fff;border-color:var(--brand-mid)}
.btn-external::after{content:"↗";font-size:12px;font-weight:500;opacity:.85}
p .btn{margin:4px 0 8px}

.body img{max-width:100%;height:auto;display:block;margin:16px 0;border:1px solid var(--rule)}
figure{margin:16px 0}
figure img{margin:0}
figcaption{font-size:12px;color:var(--ink-light);margin-top:6px}

.body table{width:100%;border-collapse:collapse;margin:16px 0;font-size:13px;line-height:1.6;background:var(--surface);border:1px solid var(--rule)}
.body th,.body td{padding:10px 12px;text-align:left;vertical-align:top;border-bottom:1px solid var(--rule)}
.body th{font-weight:700;font-size:12px;color:var(--brand);background:var(--brand-soft)}

.callout{margin:16px 0;padding:14px 16px;background:var(--warn-bg);border:1px solid var(--warn-border);border-left:3px solid #c2410c}
.callout strong{display:block;font-size:12.5px;color:var(--warn);margin-bottom:4px;font-weight:700}
.callout p{margin:0;font-size:13.5px;color:#7c2d12;line-height:1.75}
.callout p+p,.callout ol,.callout ul{margin-top:8px}
.callout .btn{margin-top:10px}

.note-box{margin:16px 0;padding:14px 16px;background:var(--brand-soft);border:1px solid #c9dceb;border-left:3px solid var(--brand)}
.note-box strong{display:block;font-size:12.5px;color:var(--brand);margin-bottom:4px}
.note-box p,.note-box ul{margin:0;font-size:13.5px;color:#1e3a5f;line-height:1.75}
.note-box ul{padding-left:1.2em;margin-top:6px}
.note-box .btn{margin-top:10px}

.steps{list-style:none;padding:0;margin:16px 0;counter-reset:step;border:1px solid var(--rule)}
.steps>li{counter-increment:step;position:relative;padding:16px 16px 16px 56px;margin:0;border-bottom:1px solid var(--rule);background:var(--surface)}
.steps>li:last-child{border-bottom:none}
.steps>li::before{content:counter(step);position:absolute;left:16px;top:16px;width:24px;height:24px;background:var(--brand);color:#fff;display:grid;place-items:center;font-size:12px;font-weight:700;line-height:1}
.steps h3{margin:0 0 4px;font-size:14.5px}
.steps p{margin:0;font-size:13.5px;color:var(--ink-mid)}

.checks{list-style:none;padding:0;margin:12px 0;border:1px solid var(--rule)}
.checks li{position:relative;padding:11px 14px 11px 40px;margin:0;border-bottom:1px solid var(--rule);font-size:14px;background:var(--surface)}
.checks li:last-child{border-bottom:none}
.checks li::before{content:"";position:absolute;left:14px;top:14px;width:14px;height:14px;border:1.5px solid var(--brand);background:#fff}
.checks li::after{content:"";position:absolute;left:18px;top:17px;width:5px;height:8px;border:solid var(--brand);border-width:0 2px 2px 0;transform:rotate(45deg)}
.checks.numbered{counter-reset:chk}
.checks.numbered li{counter-increment:chk;padding-left:44px}
.checks.numbered li::before{content:counter(chk);width:20px;height:20px;left:12px;top:11px;border:none;background:var(--brand);color:#fff;display:grid;place-items:center;font-size:11px;font-weight:700;line-height:1}
.checks.numbered li::after{display:none}

.cards{list-style:none;padding:0;margin:12px 0;border:1px solid var(--rule)}
.cards li{margin:0;border-bottom:1px solid var(--rule)}
.cards li:last-child{border-bottom:none}
.cards a{display:flex;align-items:center;gap:12px;padding:13px 14px;background:var(--surface);text-decoration:none;font-size:14px;font-weight:600;color:var(--ink)}
.cards a:hover{background:var(--brand-soft);color:var(--brand)}
.cards a::after{content:"›";margin-left:auto;color:var(--ink-light);font-size:18px;font-weight:400}
.cards .note{font-size:11.5px;font-weight:500;color:var(--ink-light);border:1px solid var(--rule);padding:2px 8px;background:var(--bg)}

.sample-label{margin:16px 0 6px;font-size:12.5px;font-weight:700;color:var(--ink-mid)}
.sample-box{margin:0 0 20px;padding:12px;border:1px solid var(--rule);background:#fff;overflow:auto}
.sample-box svg{display:block;max-width:100%;height:auto}
.sample-bank{font-size:13px}
.sample-meta{margin-bottom:10px}
.sample-meta-title{font-weight:700;margin-bottom:4px}
.sample-meta-row{display:flex;gap:20px;flex-wrap:wrap;margin-bottom:2px}
.redact,.sample-table td.redacted{background:#1a1a1a;color:#1a1a1a}
.sample-table{width:100%;border-collapse:collapse;font-size:12px}
.sample-table th,.sample-table td{border:1px solid #bbb;padding:5px 4px;text-align:center}
.sample-table th{background:#e5e5e5}
.sample-table td.num{text-align:right}

.prevnext{display:flex;justify-content:space-between;gap:12px;margin-top:40px;padding-top:20px;border-top:1px solid var(--rule)}
.pn{display:flex;flex-direction:column;gap:3px;text-decoration:none;max-width:47%;padding:12px 14px;background:var(--bg);border:1px solid var(--rule);color:inherit}
.pn:hover{border-color:var(--brand);background:var(--brand-soft)}
.pn.next{margin-left:auto;text-align:right}
.pn-dir{font-size:11px;color:var(--brand);font-weight:700}
.pn-title{font-size:13.5px;color:var(--ink);line-height:1.5}

.foot{border-top:1px solid var(--rule);padding:22px 0 36px;background:var(--surface)}
.foot-inner{max-width:var(--shell);margin:0 auto;padding:0 28px}
.foot p{margin:0;font-size:12px;line-height:1.8;color:var(--ink-light);max-width:52em}

.gsite-embed{margin:0 0 20px}
.gsite-embed > div[style]{max-width:100%!important;margin:0!important;padding:0!important;background:transparent!important;font-family:inherit!important}


/* ----- 入力手順ガイド ----- */
.cond-bar{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin:0 0 20px;padding:12px 14px;background:var(--brand-soft);border:1px solid #c9dceb}
.cond-label{font-size:12px;font-weight:700;color:var(--brand);margin-right:4px}
.cond-chip{display:inline-block;font-size:12px;font-weight:600;color:var(--ink);background:#fff;border:1px solid var(--rule);padding:3px 10px}

.phase-flow{list-style:none;margin:0 0 22px;padding:0;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
.phase-flow-item{display:flex;align-items:center;gap:10px;padding:12px 12px;border:1px solid var(--rule);background:var(--bg)}
.phase-flow-item>span{flex:none;width:28px;height:28px;display:grid;place-items:center;font-size:12px;font-weight:700;background:var(--brand);color:#fff}
.phase-flow-item.is-us>span{background:#64748b}
.phase-flow-item strong{display:block;font-size:13px}
.phase-flow-item small{display:block;font-size:11.5px;color:var(--ink-light)}

.guide-tabs{display:flex;gap:0;margin:0 0 18px;border:1px solid var(--rule)}
.guide-tab{flex:1;appearance:none;border:0;border-right:1px solid var(--rule);background:var(--bg);color:var(--ink-mid);font:inherit;font-size:13.5px;font-weight:700;padding:12px 10px;cursor:pointer}
.guide-tab:last-child{border-right:0}
.guide-tab.is-active{background:var(--brand);color:#fff}
.guide-tab:hover:not(.is-active){background:var(--brand-soft);color:var(--brand)}
.guide-panel[hidden]{display:none!important}

.guide-steps{list-style:none;margin:0;padding:0;border:1px solid var(--rule)}
.guide-step{position:relative;display:grid;grid-template-columns:40px minmax(0,1fr);gap:12px;margin:0;padding:16px 16px 16px 12px;border-bottom:1px solid var(--rule);background:#fff}
.guide-step:last-child,.guide-step.last{border-bottom:none}
.guide-num{width:28px;height:28px;margin-top:1px;display:grid;place-items:center;background:var(--brand);color:#fff;font-size:12px;font-weight:700;line-height:1}
.guide-body h3{margin:2px 0 8px;font-size:15px}
.guide-body>p{margin:0 0 10px;font-size:14px;color:var(--ink-mid)}
.guide-body .note-box,.guide-body .callout,.guide-body table{margin-top:10px;margin-bottom:10px}

.ui-path{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin:0 0 8px}
.ui-path-item{display:inline-block;padding:5px 10px;border:1px solid var(--rule);background:var(--bg);font-size:12.5px;font-weight:600;color:var(--ink-mid)}
.ui-path-item.primary{background:var(--brand-soft);border-color:#b7cee4;color:var(--brand)}
.ui-path-sep{color:var(--ink-light);font-size:12px}

.ui-btn{display:inline-flex;align-items:center;padding:7px 12px;margin:0 4px 4px 0;border:1px solid var(--brand);background:var(--brand);color:#fff;font-size:12.5px;font-weight:700}
.ui-btn.ghost{background:#fff;color:var(--ink-mid);border-color:var(--rule)}
.ui-btn.accent{background:#c2410c;border-color:#c2410c}
.ui-btn.success{background:#0f766e;border-color:#0f766e}

.file-chip{display:flex;align-items:flex-start;gap:10px;margin:0 0 8px;padding:10px 12px;border:1px solid var(--rule);background:var(--bg)}
.file-num{flex:none;width:22px;height:22px;display:grid;place-items:center;background:var(--brand);color:#fff;font-size:11px;font-weight:700}
.file-name{font-size:13.5px;font-weight:700;color:var(--ink);word-break:break-all}
.file-sub{font-size:12px;color:var(--ink-light);margin-top:2px}

.choice-list{display:grid;gap:6px;margin:0 0 10px}
.choice{padding:10px 12px;border:1px solid var(--rule);background:#fff;font-size:13.5px;color:var(--ink-light)}
.choice.on{border-color:var(--brand);background:var(--brand-soft);color:var(--ink);font-weight:700}
.choice-tag{margin-left:8px;font-size:11.5px;font-weight:700;color:var(--brand)}
.choice.off{opacity:.7}

.login-guide{margin:10px 0 12px;border:1px solid var(--rule);background:#fff}
.login-tabs{display:flex;flex-wrap:wrap;gap:0;border-bottom:1px solid var(--rule);background:var(--bg)}
.login-tab{appearance:none;border:0;border-right:1px solid var(--rule);border-bottom:2px solid transparent;background:transparent;color:var(--ink-mid);font:inherit;font-size:12px;font-weight:700;padding:10px 10px;cursor:pointer;margin-bottom:-1px}
.login-tab:hover:not(.is-active){color:var(--brand);background:var(--brand-soft)}
.login-tab.is-active{color:var(--brand);background:#fff;border-bottom-color:var(--brand)}
.login-panel{padding:14px 14px 12px}
.login-panel[hidden]{display:none!important}
.login-panel>p{margin:0 0 10px;font-size:14px;color:var(--ink-mid)}
.login-panel ol{margin:0 0 10px;padding-left:1.25em;font-size:14px;color:var(--ink-mid);line-height:1.75}
.login-panel .note-box,.login-panel .callout{margin:10px 0 0}

@media (max-width:700px){
  .phase-flow{grid-template-columns:1fr}
  .guide-step{grid-template-columns:32px minmax(0,1fr);padding:14px 12px}
  .login-tab{flex:1 1 40%;border-right:0;border-bottom:1px solid var(--rule);font-size:11.5px;padding:9px 8px}
}

@media (max-width:900px){
  .masthead-inner{padding:0 16px;height:52px}
  .masthead-notice{padding:8px 16px;font-size:11.5px;text-align:left}
  .shell{grid-template-columns:1fr;gap:0;padding:16px 16px 48px}
  .sidebar{position:static;max-height:none;display:none;margin-bottom:16px}
  .sidebar.open{display:block}
  .nav-toggle{display:flex}
  .main{padding:22px 18px 32px}
  h1{font-size:21px}
  .body>h2{font-size:14.5px;margin:32px 0 12px}
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
  if(btn&&side){
    btn.addEventListener('click',function(){
      var open=side.classList.toggle('open');
      btn.setAttribute('aria-expanded',String(open));
    });
  }
  document.querySelectorAll('a[href]').forEach(function(a){
    var href=a.getAttribute('href')||'';
    if(/^https?:\/\//i.test(href)){
      a.setAttribute('target','_blank');
      var rel=(a.getAttribute('rel')||'').split(/\s+/).filter(Boolean);
      if(rel.indexOf('noopener')===-1)rel.push('noopener');
      if(rel.indexOf('noreferrer')===-1)rel.push('noreferrer');
      a.setAttribute('rel',rel.join(' '));
    }
  });

  // 入力手順タブ（①/③）
  document.querySelectorAll('[data-guide-tab]').forEach(function(btn){
    btn.addEventListener('click',function(){
      var id=btn.getAttribute('data-guide-tab');
      var root=btn.closest('.body')||document;
      root.querySelectorAll('[data-guide-tab]').forEach(function(b){b.classList.toggle('is-active',b===btn)});
      root.querySelectorAll('.guide-panel').forEach(function(p){
        var show=p.id==='guide-panel-'+id;
        if(show)p.removeAttribute('hidden'); else p.setAttribute('hidden','');
      });
    });
  });

  // ログイン手順タブ
  document.querySelectorAll('[data-login-guide]').forEach(function(guide){
    guide.querySelectorAll('[data-login-tab]').forEach(function(btn){
      btn.addEventListener('click',function(){
        var id=btn.getAttribute('data-login-tab');
        guide.querySelectorAll('[data-login-tab]').forEach(function(b){
          var on=b===btn;
          b.classList.toggle('is-active',on);
          b.setAttribute('aria-selected',String(on));
        });
        guide.querySelectorAll('[data-login-panel]').forEach(function(p){
          var show=p.getAttribute('data-login-panel')===id;
          p.classList.toggle('is-active',show);
          if(show)p.removeAttribute('hidden'); else p.setAttribute('hidden','');
        });
      });
    });
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
