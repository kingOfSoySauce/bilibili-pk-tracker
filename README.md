# Bilibili PK Tracker

B站视频PK数据实时对比看板。当前追踪的是《流量王01》系列中大虾队 vs 雨哥队的播放量对决。

## 项目结构

```
├── crawler.py       # 数据采集脚本，调用B站公开API，每30分钟跑一次
├── data.json        # 采集到的快照数据（时间序列）
├── data.js          # data.json 的 JS 包装版，支持 file:// 直接打开
├── index.html       # 前端页面，ECharts图表，读取data.json/data.js渲染
└── assets/          # 视频封面和UP主头像
    ├── red-cover.jpg       # 大虾队视频封面
    ├── blue-cover.jpg      # 雨哥队视频封面
    ├── red-avatar.jpg      # 徐大虾咯头像
    ├── sanmu-avatar.jpg    # 自来卷三木头像
    ├── amazong-avatar.jpg  # 啊吗粽头像
    ├── blue-avatar.jpg     # 雨哥到处跑头像
    ├── liyuanjun-avatar.jpg # 力元君头像
    └── zhebie-avatar.jpg   # 在下哲别头像
```

## 追踪的视频

| 队伍 | BV号 | UP主 | 播放量(起始) |
|------|------|------|-------------|
| 大虾队（红队） | BV1zgTn6rEsh | 徐大虾咯 | ~191万 |
| 雨哥队（蓝队） | BV1UUTJ6dErS | 雨哥到处跑 | ~153万 |

视频发布时间：2026-07-03，数据采集从2026-07-05 03:48开始。

## 数据采集

`crawler.py` 通过B站公开API `api.bilibili.com/x/web-interface/view` 获取：
- 播放量、点赞、投币、收藏、弹幕、评论、分享
- 视频封面、UP主头像和名字

Cron job ID: `74c816300831`，每30分钟执行一次，deliver=local。

## 前端

纯静态HTML + ECharts，无构建步骤。直接双击打开 `index.html` 时，页面会用 `data.js` 渲染播放趋势；通过 HTTP 访问时优先读取 `data.json`。

本地预览：

```bash
cd /Users/leon/Code/bilibili-pk-tracker
python3 -m http.server 9926
# 访问 http://localhost:9926
```

页面会定期刷新实时数据；历史播放趋势来自 `data.json`，静态直开时回退到 `data.js`。

## 部署

页面仍然是纯静态文件，动态数据由 GitHub Actions 每30分钟运行 `crawler.py` 更新 `data.json` 并推回仓库。发布平台只需要支持“Git 仓库部署 + 自定义构建命令 + 静态目录输出”。

如果主要给国内用户访问，优先用腾讯 EdgeOne Pages；如果只是快速给少量人试用，也可以用 Cloudflare Pages。两者都可以复用同一套构建配置：

- Build command: `bash scripts/build-site.sh`
- Build output directory: `dist`

### EdgeOne Pages（国内优先）

1. 把本目录推到 GitHub 仓库，默认分支使用 `main`。
2. 在 EdgeOne Pages / Makers 控制台连接 GitHub 仓库。
3. 设置构建命令和输出目录为上面的 `bash scripts/build-site.sh` / `dist`。
4. 第一次发布后会得到平台分配的访问地址，可以直接发给别人访问。
5. 到 GitHub `Actions` 手动运行一次 `Update Bilibili data`，之后会每30分钟自动采集；每次 `data.json` 被提交后，平台会自动重新发布。

### Cloudflare Pages（海外/通用）

步骤：

1. 把本目录推到 GitHub 仓库，默认分支使用 `main`。
2. 在 Cloudflare Dashboard 进入 `Workers & Pages -> Create application -> Pages -> Import an existing Git repository`。
3. 选择这个仓库，设置：
   - Production branch: `main`
   - Build command: `bash scripts/build-site.sh`
   - Build output directory: `dist`
4. 第一次发布后会得到一个 `*.pages.dev` 地址，可以直接发给别人访问。
5. 到 GitHub `Actions` 手动运行一次 `Update Bilibili data`，之后会每30分钟自动采集；每次 `data.json` 被提交后，Cloudflare Pages 会自动重新发布。

发布内容只包含 `index.html`、`data.json`、`data.js` 和 `assets/`，不会把采集脚本作为网页文件发布出去。

## 团队背景

《流量王》是B站UP主团体自制的PK综艺，核心成员：在下哲别、力元君、自来卷三木、徐大虾咯、啊吗粽、雨哥到处跑、韩小沐。本轮PK规则：一周后播放量高的队伍获胜。

## 待办

- [ ] 页面视觉升级（当前版本AI味重，计划用Sentry风格重做）
- [x] 添加 Cloudflare Pages 发布配置和 GitHub Actions 定时采集
- [ ] 历史数据缺失（前2天），可用增长模型估算补全
