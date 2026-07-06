#!/usr/bin/env python3
"""
Bilibili PK 视频数据采集器
每30分钟抓取一次两个视频的播放量等数据，追加到 data.jsonl
"""

import json
import time
import os
import urllib.request
import urllib.error
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.jsonl")
DATA_JS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.js")
DATA_JS_HEADER = "window.BILI_PK_DATA = window.BILI_PK_DATA || { snapshots: [] };\n"

VIDEOS = [
    {
        "bvid": "BV1zgTn6rEsh",
        "label": "红队",
        "up": "徐大虾咯",
    },
    {
        "bvid": "BV1UUTJ6dErS",
        "label": "蓝队",
        "up": "雨哥到处跑",
    },
]

API_URL = "https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com",
}


def count_snapshots():
    if not os.path.exists(DATA_FILE):
        return 0
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


def append_snapshot(snapshot):
    payload = json.dumps(snapshot, ensure_ascii=False, separators=(",", ":"))
    with open(DATA_FILE, "a", encoding="utf-8") as f:
        f.write(payload)
        f.write("\n")
    append_data_js(payload)


def append_data_js(payload):
    needs_header = not os.path.exists(DATA_JS_FILE) or os.path.getsize(DATA_JS_FILE) == 0
    with open(DATA_JS_FILE, "a", encoding="utf-8") as f:
        if needs_header:
            f.write(DATA_JS_HEADER)
        f.write("window.BILI_PK_DATA.snapshots.push(")
        f.write(payload)
        f.write(");\n")


def now_iso():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def fetch_video(bvid):
    url = API_URL.format(bvid=bvid)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    if result.get("code") != 0:
        raise Exception(f"API error: {result.get('message', 'unknown')}")
    d = result["data"]
    stat = d["stat"]
    return {
        "title": d["title"],
        "up": d["owner"]["name"],
        "view": stat["view"],
        "like": stat["like"],
        "coin": stat["coin"],
        "favorite": stat["favorite"],
        "share": stat["share"],
        "danmaku": stat["danmaku"],
        "reply": stat["reply"],
        "pubdate": d["pubdate"],
        "duration": d["duration"],
    }


def main():
    ts = int(time.time())
    now = now_iso()
    print(f"[{now}] 开始采集...")

    snapshot = {"ts": ts, "time": now, "videos": {}}
    errors = []

    for v in VIDEOS:
        try:
            info = fetch_video(v["bvid"])
            snapshot["videos"][v["label"]] = info
            print(f"  {v['label']}({v['up']}): {info['view']:,} 播放 | {info['like']:,} 点赞 | {info['coin']:,} 投币")
        except Exception as e:
            print(f"  {v['label']} 采集失败: {e}")
            errors.append(f"{v['label']}: {e}")

        time.sleep(1)  # 礼貌间隔

    if errors:
        print("  采集未完整成功，跳过写入，避免页面展示错误快照")
        raise SystemExit(1)

    append_snapshot(snapshot)
    print(f"  已保存，共 {count_snapshots()} 条快照")


if __name__ == "__main__":
    main()
