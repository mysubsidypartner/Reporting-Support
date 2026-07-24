#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path

PORTAL = "https://portal.shinsei.it-shien.smrj.go.jp/"
KANA = "https://tinyurl.com/kouza-kana"
ROOT = Path(__file__).resolve().parent if False else Path(".")
CONTENT = ROOT / "content"


def ui(*labels):
    parts = []
    for i, lab in enumerate(labels):
        cls = "ui-path-item" + (" primary" if i == len(labels) - 1 else "")
        parts.append(f'<span class="{cls}">{lab}</span>')
        if i < len(labels) - 1:
            parts.append('<span class="ui-path-sep">→</span>')
    return '<div class="ui-path">' + "".join(parts) + "</div>"


def file_chip(num, name, sub=None):
    sub_html = f'<div class="file-sub">{sub}</div>' if sub else ""
    return f"""<div class="file-chip">
  <span class="file-num">{num}</span>
  <div><div class="file-name">{name}</div>{sub_html}</div>
</div>"""


def step(n, title, body, last=False):
    last_cls = " last" if last else ""
    return f"""<li class="guide-step{last_cls}">
  <span class="guide-num">{n}</span>
  <div class="guide-body">
    <h3>{title}</h3>
    {body}
  </div>
</li>"""


def phase1_steps(cfg):
    inv = cfg["waku"] == "invoice"
    sho = cfg["kibo"] == "shoukibo"
    pc_yes = cfg["pc"] == "yes"
    pos_yes = cfg["pos"] == "yes"
    steps = []
    n = 1

    steps.append(step(n, "申請マイページにログインする", f"""
<p><a class="btn btn-external" href="{PORTAL}" target="_blank" rel="noopener">申請マイページを開く</a></p>
{ui("申請者メニュー", "実績報告情報編集")}
""")); n += 1

    steps.append(step(n, "説明画面を確認する", """
<p>説明が表示されます。内容を確認し、下へスクロールして進みます。</p>
<p><span class="ui-btn">次へ</span></p>
""")); n += 1

    steps.append(step(n, "請求書を添付する", f"""
{file_chip("1", "1_請求明細書_事業者名")}
<p><span class="ui-btn">次へ</span></p>
""")); n += 1

    steps.append(step(n, "支払方法を選択する", """
<p>「銀行振込」を選択してください。</p>
<div class="choice-list">
  <div class="choice on">銀行振込 <span class="choice-tag">こちらを選択</span></div>
  <div class="choice off">クレジットカード払い</div>
</div>
<p><span class="ui-btn">次へ</span></p>
""")); n += 1

    steps.append(step(n, "支払証憑を添付する", f"""
{file_chip("2", "2_支払証憑_事業者名")}
<p><span class="ui-btn">次へ</span></p>
""")); n += 1

    if inv and sho:
        body6 = f"""
<p>従業員一覧を添付してください。</p>
{file_chip("3", "3_従業員一覧_事業者名")}
<p><span class="ui-btn">次へ</span></p>
"""
    else:
        body6 = """
<p>この画面での追加添付はありません。</p>
<div class="note-box"><strong>ポイント</strong><p>添付不要です。そのまま「次へ」を押してください。</p></div>
<p><span class="ui-btn">次へ</span></p>
"""
    steps.append(step(n, "その他資料を確認する", body6)); n += 1

    steps.append(step(n, "ソフトウェア証憑を添付する", f"""
{file_chip("4", "4_ソフトウェア証憑_事業者名")}
<p><span class="ui-btn">次へ</span></p>
""")); n += 1

    if inv:
        if pc_yes:
            pc_body = f"""
<p>PC・タブレット等の導入ありを選択し、次を添付します。</p>
<div class="choice-list"><div class="choice on">はい</div></div>
{file_chip("5", "5_ハードウェア導入情報（納品書）_事業者名", "納品書欄")}
{file_chip("6", "6_ハードウェア導入情報（現物写真）_事業者名", "現物写真欄")}
<p><span class="ui-btn">次へ</span></p>
"""
        else:
            pc_body = """
<p>PC・タブレット等を導入していない場合は「いいえ」を選択します。</p>
<div class="choice-list"><div class="choice on">いいえ</div></div>
<div class="note-box"><strong>ポイント</strong><p>「いいえ」を選ぶだけで進みます。</p></div>
<p><span class="ui-btn">次へ</span></p>
"""
        steps.append(step(n, "ハードウェア導入情報（PC・タブレット等）", pc_body)); n += 1

        if pos_yes:
            pos_body = f"""
<p>POSレジ等の導入ありを選択し、次を添付します。</p>
<div class="choice-list"><div class="choice on">はい</div></div>
{file_chip("5", "5_ハードウェア導入情報（納品書）_事業者名", "納品書欄")}
{file_chip("6", "6_ハードウェア導入情報（現物写真）_事業者名", "現物写真欄")}
<p><span class="ui-btn">次へ</span></p>
"""
        else:
            pos_body = """
<p>POSレジ等を導入していない場合は「いいえ」を選択します。</p>
<div class="choice-list"><div class="choice on">いいえ</div></div>
<div class="note-box"><strong>ポイント</strong><p>「いいえ」を選ぶだけで進みます。</p></div>
<p><span class="ui-btn">次へ</span></p>
"""
        steps.append(step(n, "ハードウェア導入情報（POSレジ等）", pos_body)); n += 1

    steps.append(step(n, "口座情報を添付する", f"""
{file_chip("7", "7_口座情報_事業者名")}
<p><span class="ui-btn">次へ</span></p>
""")); n += 1

    steps.append(step(n, "口座情報を入力する", f"""
<p>添付したPDFを開き、画面の項目へ入力します。</p>
<table>
  <thead><tr><th>項目</th><th>入力方法</th></tr></thead>
  <tbody>
    <tr><th>金融機関名</th><td>PDFを開く → 下へスクロール →「検索」→ 全角カナで入力 → 余白クリック →「検索」→ 選択<br><span class="item-note">文字入力中は「検索」が押せません</span></td></tr>
    <tr><th>支店名</th><td>金融機関名と同じ手順で検索・選択</td></tr>
    <tr><th>口座名義（カナ）</th><td>金融機関登録の名義と完全一致が必要です（スペース・濁点に注意）<br><a class="btn btn-external" href="{KANA}" target="_blank" rel="noopener">口座名義変換ツール</a></td></tr>
  </tbody>
</table>
<p><span class="ui-btn">次へ</span></p>
""")); n += 1

    steps.append(step(n, "実績報告入力を完了する", """
<p>補助事業者入力確認画面で内容を確認し、一番下のボタンを押します。</p>
<p><span class="ui-btn success">実績報告入力完了</span></p>
<div class="note-box">
  <strong>ここまでで①は完了</strong>
  <p>IT導入支援事業者に引き継がれます。弊社確認後、③「事務局への提出」をご案内します。</p>
</div>
""", last=True))
    return "\n".join(steps)


def phase3_steps():
    return "\n".join([
        step(1, "申請マイページにログインする", f"""
<p><a class="btn btn-external" href="{PORTAL}" target="_blank" rel="noopener">申請マイページを開く</a></p>
{ui("申請者メニュー", "実績報告情報編集")}
"""),
        step(2, "実績報告内容を最終確認する", """
<p>添付・入力内容が一覧表示されます。金額を含め、すべて確認してください。</p>
<div class="callout"><strong>注意</strong><p>修正が必要な場合は「戻る」で対応できます。</p></div>
<p><span class="ui-btn ghost">戻る</span> <span class="ui-btn">次へ</span></p>
"""),
        step(3, "SMS認証コードを発行・入力する", """
<ol>
  <li>「認証コードを発行する」を押す</li>
  <li>SMSで届いた4桁のコードを入力する</li>
</ol>
<div class="callout"><strong>有効期限</strong><p>認証コードは発行から30分間有効です。30分以内に提出まで完了してください。</p></div>
<p><span class="ui-btn accent">認証コードを発行する</span></p>
"""),
        step(4, "事務局へ提出する", """
<p>認証コード入力後、「事務局へ提出」を押します。</p>
<p><span class="ui-btn success">事務局へ提出</span></p>
<div class="note-box">
  <strong>提出完了</strong>
  <p>この画面が表示されれば完了です。その後、事務局による確定検査が行われます。</p>
</div>
<div class="callout"><strong>差し戻し時</strong><p>不備がある場合は事務局から連絡があります。速やかに対応してください。</p></div>
""", last=True),
    ])


def chips_for(cfg, override=None):
    if override:
        items = override
    elif cfg["waku"] == "tsujou":
        items = ["通常枠"]
    else:
        items = [
            "インボイス枠",
            "小規模事業者" if cfg["kibo"] == "shoukibo" else "中小企業",
            "PCあり" if cfg["pc"] == "yes" else "PCなし",
            "POSあり" if cfg["pos"] == "yes" else "POSなし",
        ]
    return "".join(f'<span class="cond-chip">{c}</span>' for c in items)


def guide_page(cfg, show_phase1=True, default_tab=1, chip_override=None):
    chip_html = chips_for(cfg, chip_override)
    flow = """
<ol class="phase-flow">
  <li class="phase-flow-item is-you"><span>①</span><div><strong>貴社</strong><small>添付・送信</small></div></li>
  <li class="phase-flow-item is-us"><span>②</span><div><strong>弊社</strong><small>内容確認</small></div></li>
  <li class="phase-flow-item is-you"><span>③</span><div><strong>貴社</strong><small>事務局へ提出</small></div></li>
</ol>"""

    if show_phase1:
        tab1_on = " is-active" if default_tab == 1 else ""
        tab3_on = " is-active" if default_tab == 3 else ""
        tabs = f"""
<div class="guide-tabs" role="tablist">
  <button type="button" class="guide-tab{tab1_on}" data-guide-tab="1" role="tab">① 添付・送信</button>
  <button type="button" class="guide-tab{tab3_on}" data-guide-tab="3" role="tab">③ 事務局へ提出</button>
</div>"""
        p1_hidden = "" if default_tab == 1 else " hidden"
        p3_hidden = "" if default_tab == 3 else " hidden"
        phase1 = f"""
<section class="guide-panel" id="guide-panel-1"{p1_hidden}>
  <ol class="guide-steps">
{phase1_steps(cfg)}
  </ol>
</section>"""
    else:
        tabs = """
<div class="guide-tabs" role="tablist">
  <button type="button" class="guide-tab is-active" data-guide-tab="3" role="tab">③ 事務局へ提出</button>
</div>"""
        phase1 = ""
        p3_hidden = ""

    phase3 = f"""
<section class="guide-panel" id="guide-panel-3"{p3_hidden}>
  <ol class="guide-steps">
{phase3_steps()}
  </ol>
</section>"""

    return f"""<p class="lead">申請マイページでの操作手順です。画面の表示に沿って、上から順に進めてください。</p>

<div class="cond-bar">
  <span class="cond-label">このページの対象</span>
  {chip_html}
</div>

{flow}
{tabs}
{phase1}
{phase3}
"""


def main():
    CONTENT.mkdir(exist_ok=True)

    hub = """<p class="lead">申請枠・事業者区分・導入内容に合う手順を選んでください。完了までの流れは共通です。</p>

<ol class="phase-flow">
  <li class="phase-flow-item is-you"><span>①</span><div><strong>貴社</strong><small>添付・送信</small></div></li>
  <li class="phase-flow-item is-us"><span>②</span><div><strong>弊社</strong><small>内容確認</small></div></li>
  <li class="phase-flow-item is-you"><span>③</span><div><strong>貴社</strong><small>事務局へ提出</small></div></li>
</ol>

<h2>通常枠</h2>
<ul class="cards">
  <li><a href="tejun-tsujo.html">通常枠の入力手順</a></li>
</ul>

<h2>インボイス枠｜中小企業</h2>
<ul class="cards">
  <li><a href="tejun-inv-chusho-pc1-pos1.html">PCあり / POSあり</a></li>
  <li><a href="tejun-inv-chusho-pc1-pos0.html">PCあり / POSなし</a></li>
  <li><a href="tejun-inv-chusho-pc0-pos1.html">PCなし / POSあり</a></li>
  <li><a href="tejun-inv-chusho-pc0-pos0.html">PCなし / POSなし</a></li>
</ul>

<h2>インボイス枠｜小規模事業者</h2>
<ul class="cards">
  <li><a href="tejun-inv-shokibo-pc1-pos1.html">PCあり / POSあり</a></li>
  <li><a href="tejun-inv-shokibo-pc1-pos0.html">PCあり / POSなし</a></li>
  <li><a href="tejun-inv-shokibo-pc0-pos1.html">PCなし / POSあり</a></li>
  <li><a href="tejun-inv-shokibo-pc0-pos0.html">PCなし / POSなし</a></li>
</ul>

<h2>最後に</h2>
<ul class="cards">
  <li><a href="tejun-teishutsu.html">事務局への提出<span class="note">全枠共通</span></a></li>
</ul>

<div class="note-box">
  <strong>事前準備</strong>
  <p>書類がそろっていない場合は、先に<a href="jisseki.html">実績報告について</a>で必要書類を確認してください。</p>
</div>
"""
    (CONTENT / "tejun.html").write_text(hub, encoding="utf-8")

    pages = {
        "tejun-tsujo.html": {"waku": "tsujou", "kibo": "chuusho", "pc": "no", "pos": "no"},
        "tejun-inv-chusho-pc1-pos1.html": {"waku": "invoice", "kibo": "chuusho", "pc": "yes", "pos": "yes"},
        "tejun-inv-chusho-pc1-pos0.html": {"waku": "invoice", "kibo": "chuusho", "pc": "yes", "pos": "no"},
        "tejun-inv-chusho-pc0-pos1.html": {"waku": "invoice", "kibo": "chuusho", "pc": "no", "pos": "yes"},
        "tejun-inv-chusho-pc0-pos0.html": {"waku": "invoice", "kibo": "chuusho", "pc": "no", "pos": "no"},
        "tejun-inv-shokibo-pc1-pos1.html": {"waku": "invoice", "kibo": "shoukibo", "pc": "yes", "pos": "yes"},
        "tejun-inv-shokibo-pc1-pos0.html": {"waku": "invoice", "kibo": "shoukibo", "pc": "yes", "pos": "no"},
        "tejun-inv-shokibo-pc0-pos1.html": {"waku": "invoice", "kibo": "shoukibo", "pc": "no", "pos": "yes"},
        "tejun-inv-shokibo-pc0-pos0.html": {"waku": "invoice", "kibo": "shoukibo", "pc": "no", "pos": "no"},
    }
    for name, cfg in pages.items():
        (CONTENT / name).write_text(guide_page(cfg, show_phase1=True, default_tab=1), encoding="utf-8")
        print("wrote", name)

    (CONTENT / "tejun-teishutsu.html").write_text(
        guide_page(
            {"waku": "tsujou", "kibo": "chuusho", "pc": "no", "pos": "no"},
            show_phase1=False,
            default_tab=3,
            chip_override=["全枠共通"],
        ),
        encoding="utf-8",
    )
    print("wrote tejun-teishutsu.html")


if __name__ == "__main__":
    main()
