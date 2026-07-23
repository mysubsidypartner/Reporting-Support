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


def placeholder(slug, title):
    return f"""<p class="lead">このページの本文は <code>content/{slug}.html</code> を編集すると差し替わります。</p>

<h2>用意するもの</h2>
<p>Googleサイトから該当ページの文章と画像をここに移してください。</p>

<h2>手順</h2>
<ol class="steps">
  <li>
    <h3>書類を開く</h3>
    <p>手順の説明をここに書きます。1ステップに1つの操作だけを書くと迷いません。</p>
  </li>
  <li>
    <h3>内容を確認する</h3>
    <p>画像は <code>&lt;img src="assets/img/example.png" alt="説明"&gt;</code> で読み込みます。</p>
  </li>
</ol>

<div class="callout">
  <strong>提出前の確認</strong>
  <p>宛名・日付・金額が申請内容と一致しているか確認してください。</p>
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
  --paper:#f4f2ed;
  --panel:#faf9f6;
  --ink:#33312c;
  --ink-mid:#6b675e;
  --ink-light:#96918a;
  --rule:#d9d5cc;
  --rule-soft:#e6e3db;
  --mark:#7a2e28;
  --focus:#33312c;
  --measure:34em;
}
*{box-sizing:border-box}
body{
  margin:0;background:var(--paper);color:var(--ink);
  font-family:"Hiragino Kaku Gothic ProN","Yu Gothic Medium","Yu Gothic",Meiryo,system-ui,sans-serif;
  font-size:16px;line-height:2.0;
  font-feature-settings:"palt" 1;
  -webkit-font-smoothing:antialiased;
}
a{color:var(--ink);text-underline-offset:.25em;text-decoration-color:var(--rule)}
a:hover{text-decoration-color:var(--ink-mid)}
:focus-visible{outline:2px solid var(--focus);outline-offset:3px}
.skip{position:absolute;left:-9999px}
.skip:focus{left:16px;top:16px;background:var(--panel);padding:12px 18px;z-index:30}

/* ---------- ヘッダー ---------- */
.masthead{
  background:var(--paper);border-bottom:1px solid var(--rule);
  position:sticky;top:0;z-index:20;
}
.masthead-inner{
  max-width:1080px;margin:0 auto;padding:0 40px;
  height:68px;display:flex;align-items:center;justify-content:space-between;
}
.brand{display:flex;align-items:baseline;gap:12px;text-decoration:none}
.brand-name{font-size:16px;font-weight:600;letter-spacing:.18em}
.brand-sub{font-size:11px;letter-spacing:.22em;color:var(--ink-light)}
.nav-toggle{
  display:none;align-items:center;gap:8px;background:none;border:none;
  font:inherit;font-size:13px;letter-spacing:.14em;color:var(--ink);
  cursor:pointer;padding:8px 4px;
}
.nav-toggle-bars{width:16px;height:1px;background:var(--ink);box-shadow:0 5px var(--ink),0 -5px var(--ink)}

/* ---------- レイアウト ---------- */
.shell{
  max-width:1080px;margin:0 auto;padding:64px 40px 96px;
  display:grid;grid-template-columns:200px minmax(0,1fr);gap:72px;
}

/* ---------- 目次 ---------- */
.sidebar{position:sticky;top:112px;align-self:start;max-height:calc(100vh - 150px);overflow-y:auto}
.sidebar::-webkit-scrollbar{width:2px}
.sidebar::-webkit-scrollbar-thumb{background:var(--rule)}
.nav-list,.nav-sub{list-style:none;margin:0;padding:0}
.nav-item a{display:block;text-decoration:none;line-height:1.6}
.nav-item.top{margin-top:22px;padding-top:14px;border-top:1px solid var(--rule)}
.nav-item.top:first-child{margin-top:0;padding-top:0;border-top:none}
.nav-item.top>a{
  font-size:13px;letter-spacing:.1em;color:var(--ink);font-weight:600;padding:2px 0;
}
.nav-sub{display:none;margin-top:10px}
.nav-item.top.open>.nav-sub{display:block}
.nav-item.sub a{
  font-size:12.5px;color:var(--ink-light);padding:6px 0 6px 14px;
  position:relative;letter-spacing:.02em;
}
.nav-item.sub a:hover{color:var(--ink)}
.nav-item.current>a{color:var(--ink);font-weight:600}
.nav-item.sub.current a::before{
  content:"";position:absolute;left:0;top:50%;width:8px;height:1px;background:var(--mark);
}

/* ---------- 本文 ---------- */
.main{min-width:0}
.page-head{padding-bottom:32px;margin-bottom:44px;border-bottom:1px solid var(--rule)}
.eyebrow{margin:0 0 14px;font-size:11px;letter-spacing:.24em;color:var(--ink-light)}
h1{
  margin:0;font-size:26px;font-weight:600;line-height:1.65;
  letter-spacing:.06em;max-width:var(--measure);
}
.body{max-width:var(--measure)}
.body>*:first-child{margin-top:0}
.lead{font-size:15px;color:var(--ink-mid);line-height:2.05;margin:0 0 40px}
h2{
  margin:64px 0 20px;font-size:16px;font-weight:600;letter-spacing:.1em;line-height:1.8;
}
h3{margin:40px 0 12px;font-size:14.5px;font-weight:600;letter-spacing:.08em;color:var(--ink-mid)}
p{margin:0 0 22px}
ul,ol{padding-left:1.4em;margin:0 0 24px}
li{margin-bottom:10px}
strong{font-weight:600}
code{
  font-family:"SFMono-Regular",Consolas,monospace;font-size:13px;
  background:var(--rule-soft);padding:2px 6px;
}

/* ---------- 図版 ---------- */
.body img{max-width:100%;height:auto;display:block;margin:32px 0}
figure{margin:32px 0}
figure img{margin:0}
figcaption{font-size:12.5px;color:var(--ink-light);margin-top:12px;letter-spacing:.04em}

/* ---------- 表 ---------- */
.body table{width:100%;border-collapse:collapse;margin:32px 0;font-size:14px;line-height:1.8}
.body th,.body td{padding:14px 4px;text-align:left;border-bottom:1px solid var(--rule-soft);vertical-align:top}
.body th{
  font-weight:600;font-size:12px;letter-spacing:.12em;color:var(--ink-light);
  border-bottom:1px solid var(--rule);
}

/* ---------- 注記 ---------- */
.callout{
  margin:32px 0;padding:22px 0;
  border-top:1px solid var(--rule);border-bottom:1px solid var(--rule);
}
.callout strong{
  display:block;font-size:12px;letter-spacing:.16em;color:var(--mark);
  margin-bottom:8px;font-weight:600;
}
.callout p{margin:0;font-size:14.5px;color:var(--ink-mid);line-height:1.95}

/* ---------- 手順リスト ---------- */
.steps{list-style:none;padding:0;margin:32px 0;counter-reset:step}
.steps>li{
  counter-increment:step;position:relative;
  padding:24px 0 24px 44px;margin:0;border-bottom:1px solid var(--rule-soft);
}
.steps>li:first-child{border-top:1px solid var(--rule-soft)}
.steps>li::before{
  content:counter(step,decimal-leading-zero);position:absolute;left:0;top:24px;
  font-size:12px;letter-spacing:.08em;color:var(--ink-light);line-height:2;
}
.steps h3{margin:0 0 6px}
.steps p{margin:0;font-size:14.5px;color:var(--ink-mid)}

/* ---------- 目次カード ---------- */
.cards{list-style:none;padding:0;margin:32px 0;border-top:1px solid var(--rule)}
.cards li{margin:0}
.cards a{
  display:flex;align-items:baseline;gap:16px;
  padding:20px 4px;border-bottom:1px solid var(--rule-soft);
  text-decoration:none;font-size:15px;
}
.cards a:hover{background:var(--panel)}
.cards a::after{
  content:"→";margin-left:auto;color:var(--ink-light);font-size:13px;
}
.cards .note{font-size:12.5px;color:var(--ink-light)}

/* ---------- 前後ナビ ---------- */
.prevnext{
  display:flex;justify-content:space-between;gap:32px;
  margin-top:96px;padding-top:28px;border-top:1px solid var(--rule);
}
.pn{
  display:flex;flex-direction:column;gap:8px;text-decoration:none;max-width:47%;
}
.pn.next{margin-left:auto;text-align:right}
.pn-dir{font-size:11px;letter-spacing:.2em;color:var(--ink-light)}
.pn-title{font-size:14px;color:var(--ink);line-height:1.7}
.pn:hover .pn-title{text-decoration:underline;text-underline-offset:.25em}

/* ---------- フッター ---------- */
.foot{border-top:1px solid var(--rule);padding:40px 0 56px}
.foot-inner{max-width:1080px;margin:0 auto;padding:0 40px}
.foot p{
  margin:0;font-size:12px;line-height:2;color:var(--ink-light);max-width:46em;
}

/* ---------- モバイル ---------- */
@media (max-width:880px){
  .masthead-inner{padding:0 24px;height:60px}
  .shell{grid-template-columns:1fr;gap:0;padding:36px 24px 72px}
  .sidebar{
    position:static;max-height:none;display:none;
    margin-bottom:40px;padding-bottom:32px;border-bottom:1px solid var(--rule);
  }
  .sidebar.open{display:block}
  .nav-toggle{display:flex}
  h1{font-size:21px}
  .prevnext{flex-direction:column;gap:24px;margin-top:64px}
  .pn,.pn.next{max-width:100%;text-align:left;margin-left:0}
  .foot-inner{padding:0 24px}
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
