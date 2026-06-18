#!/usr/bin/env python3
"""YouTube RSS の新曲を data/songs.json に蓄積し、menu.html を再生成する。

- RSS は最新15件しか返さないため「蓄積方式」。既存曲は消さない・並びも保持。
- 新しい動画だけ data/songs.json の先頭に追加（タイトルから自動パース）。
- songs.json を元に menu.html の3領域（メニュー一覧／本日のコース／おみくじ配列）を再生成。
"""
import json
import os
import re
import html
import urllib.request
import xml.etree.ElementTree as ET

CHANNEL_ID = "UCRi1_bAUClKJBGqtaiObXcA"
FEED_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
SONGS_JSON = "data/songs.json"
MENU_HTML = "menu.html"
NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}


def fetch_rss():
    """[(videoId, title), ...] を新しい順で返す。"""
    req = urllib.request.Request(FEED_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as res:
        root = ET.fromstring(res.read())
    out = []
    for e in root.findall("a:entry", NS):
        vid = e.find("yt:videoId", NS).text
        title = (e.find("a:title", NS).text or "").strip()
        out.append((vid, title))
    return out


def parse_title(title):
    """タイトル『絵文字 【曲名】｜ジャンル｜キャッチ』を分解。"""
    m = re.search(r"【(.+?)】", title)
    if m:
        name = m.group(1).strip()
        emoji = title[: m.start()].strip()
        rest = title[m.end():]
    else:
        name, emoji, rest = title, "", ""
    parts = [p.strip() for p in rest.split("｜") if p.strip()]
    is_mix = ("MIX" in title) or ("作業用" in title)
    if is_mix:
        disp = parts[0] if parts else name
        return {
            "emoji": emoji or "🌸",
            "name": disp,
            "genre": "Kawaii Future Bass MIX",
            "tagline": parts[1] if len(parts) > 1 else "",
            "mix": True,
        }
    return {
        "emoji": emoji,
        "name": name,
        "genre": parts[0] if parts else "",
        "tagline": parts[1] if len(parts) > 1 else "",
        "mix": False,
    }


def load_songs():
    if os.path.exists(SONGS_JSON):
        with open(SONGS_JSON, encoding="utf-8") as f:
            return json.load(f)
    return []


def esc(t):
    # HTML特殊文字のみエスケープ（× や — はそのまま）
    return html.escape(t or "", quote=False)


def build_menu(singles):
    items = []
    for s in singles:
        flavor = f'<span class="tag">{esc(s["genre"])}</span>'
        if s.get("tagline"):
            flavor += f' — {esc(s["tagline"])}'
        items.append(
            f'      <div class="menu-item"><div class="menu-row">'
            f'<span class="menu-name">{esc(s["emoji"])} {esc(s["name"])}</span>'
            f'<span class="menu-dots"></span>'
            f'<a class="menu-listen" href="https://www.youtube.com/watch?v={s["id"]}" '
            f'target="_blank" rel="noopener">試聴 ▸</a></div>'
            f'<p class="menu-flavor">{flavor}</p></div>'
        )
    return "\n".join(items)


def build_course(mixes):
    blocks = []
    for s in mixes:
        flavor = f'<span class="tag">{esc(s["genre"])}</span>'
        if s.get("tagline"):
            flavor += f' — {esc(s["tagline"])}'
        blocks.append(
            "      <!-- 本日のコース（作業用MIX） -->\n"
            '      <div class="course">\n'
            '        <span class="label">本日のコース 🍽</span>\n'
            f'        <span class="menu-name">{esc(s["emoji"])} {esc(s["name"])}</span>\n'
            f'        <p class="menu-flavor">{flavor}</p>\n'
            f'        <a class="menu-listen" href="https://www.youtube.com/watch?v={s["id"]}" '
            'target="_blank" rel="noopener">試聴 ▸</a>\n'
            "      </div>"
        )
    return "\n".join(blocks)


def build_omikuji(singles):
    rows = []
    for s in singles:
        n = f'{s["emoji"]} {s["name"]}'.replace("'", "’")  # JSの単一引用符対策
        rows.append(f"        {{ n: '{n}', id: '{s['id']}' }}")
    return ",\n".join(rows)


def main():
    songs = load_songs()
    existing = {s["id"] for s in songs}
    new = []
    for vid, title in fetch_rss():  # 新しい順
        if vid not in existing:
            s = parse_title(title)
            s["id"] = vid
            new.append(s)
    if new:
        songs = new + songs
        os.makedirs(os.path.dirname(SONGS_JSON), exist_ok=True)
        with open(SONGS_JSON, "w", encoding="utf-8") as f:
            json.dump(songs, f, ensure_ascii=False, indent=2)
            f.write("\n")

    singles = [s for s in songs if not s.get("mix")]
    mixes = [s for s in songs if s.get("mix")]

    with open(MENU_HTML, encoding="utf-8") as f:
        src = f.read()

    src = re.sub(
        r"<!-- MENU_LIST_START -->.*?<!-- MENU_LIST_END -->",
        lambda _: "<!-- MENU_LIST_START -->\n" + build_menu(singles) + "\n      <!-- MENU_LIST_END -->",
        src, flags=re.S,
    )
    src = re.sub(
        r"<!-- COURSE_START -->.*?<!-- COURSE_END -->",
        lambda _: "<!-- COURSE_START -->\n" + build_course(mixes) + "\n      <!-- COURSE_END -->",
        src, flags=re.S,
    )
    src = re.sub(
        r"// OMIKUJI_SONGS_START.*?// OMIKUJI_SONGS_END",
        lambda _: "// OMIKUJI_SONGS_START\n" + build_omikuji(singles) + "\n        // OMIKUJI_SONGS_END",
        src, flags=re.S,
    )

    with open(MENU_HTML, "w", encoding="utf-8") as f:
        f.write(src)

    print(f"songs total: {len(songs)} / new: {len(new)}")


if __name__ == "__main__":
    main()
