#!/usr/bin/env python3
"""YouTube RSS から最新動画3本を取得し、index.html のマーカー間を書き換える。

GitHub Actions から定期実行される想定。チャンネルIDは固定。
LATEST_VIDEOS_START 〜 END の間だけを置換するので、それ以外のレイアウトには触れない。
"""
import html
import re
import time
import urllib.request
import xml.etree.ElementTree as ET

CHANNEL_ID = "UCRi1_bAUClKJBGqtaiObXcA"  # しんたや のチャンネル
FEED_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
HTML_FILE = "index.html"
MAX_VIDEOS = 3

# RSS（Atom）の名前空間
NS = {
    "a": "http://www.w3.org/2005/Atom",
    "yt": "http://www.youtube.com/xml/schemas/2015",
}


def fetch_latest():
    """RSS を取得して [(videoId, title), ...] を最大3件返す。
    一時的な失敗（404/タイムアウト等）はリトライ。最終的に失敗したら空リストを返す。"""
    req = urllib.request.Request(FEED_URL, headers={"User-Agent": "Mozilla/5.0"})
    last_err = None
    for attempt in range(4):  # 計4回トライ
        try:
            with urllib.request.urlopen(req, timeout=30) as res:
                root = ET.fromstring(res.read())
            videos = []
            for entry in root.findall("a:entry", NS)[:MAX_VIDEOS]:
                vid = entry.find("yt:videoId", NS).text
                title = (entry.find("a:title", NS).text or "").strip()
                videos.append((vid, title))
            return videos
        except Exception as e:  # noqa: BLE001 一時的失敗を握りつぶしてリトライ
            last_err = e
            if attempt < 3:
                time.sleep(5 * (attempt + 1))  # 5秒→10秒→15秒
    print(f"RSS取得に一時的に失敗（スキップ）: {last_err}")
    return []


def build_block(videos):
    """マーカー間に挿入するHTML（インデント込み）を組み立てる。"""
    items = []
    for vid, title in videos:
        safe = html.escape(title)
        items.append(
            f'      <a class="video-item" href="https://www.youtube.com/watch?v={vid}" target="_blank" rel="noopener">\n'
            f'        <span class="video-play" aria-hidden="true">▶</span>\n'
            f'        <span>{safe}</span>\n'
            f"      </a>"
        )
    return (
        "<!-- LATEST_VIDEOS_START -->\n"
        + "\n".join(items)
        + "\n      <!-- LATEST_VIDEOS_END -->"
    )


def main():
    videos = fetch_latest()
    if not videos:
        print("RSS から動画を取得できませんでした。中断します。")
        return

    with open(HTML_FILE, encoding="utf-8") as f:
        src = f.read()

    pattern = re.compile(
        r"<!-- LATEST_VIDEOS_START -->.*?<!-- LATEST_VIDEOS_END -->", re.S
    )
    new_block = build_block(videos)
    # 置換文字列に特殊文字が含まれてもよいよう、関数置換を使う
    out = pattern.sub(lambda _: new_block, src, count=1)

    if out != src:
        with open(HTML_FILE, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"updated: {len(videos)} videos")
    else:
        print("nochange")


if __name__ == "__main__":
    main()
