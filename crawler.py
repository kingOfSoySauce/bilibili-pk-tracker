#!/usr/bin/env python3
"""
Bilibili PK 视频数据采集器
每30分钟抓取一次两个视频的播放量等数据，存入 data.json
"""

import json
import time
import os
import urllib.request
import urllib.error
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")
DATA_JS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.js")

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


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"snapshots": [], "meta": {"created": now_iso()}}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    save_data_js(data)


def save_data_js(data):
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    with open(DATA_JS_FILE, "w", encoding="utf-8") as f:
        f.write("window.BILI_PK_DATA = ")
        f.write(payload)
        f.write(";\n")


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
    data = load_data()
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

            # 保存meta信息（只在第一次写入）
            if v["label"] not in data.get("meta", {}).get("videos", {}):
                data.setdefault("meta", {}).setdefault("videos", {})[v["label"]] = {
                    "bvid": v["bvid"],
                    "title": info["title"],
                    "up": info["up"],
                    "pubdate": info["pubdate"],
                }
        except Exception as e:
            print(f"  {v['label']} 采集失败: {e}")
            errors.append(f"{v['label']}: {e}")

        time.sleep(1)  # 礼貌间隔

    if errors:
        print("  采集未完整成功，跳过写入，避免页面展示错误快照")
        raise SystemExit(1)

    data["snapshots"].append(snapshot)
    save_data(data)
    print(f"  已保存，共 {len(data['snapshots'])} 条快照")


if __name__ == "__main__":
    main()
