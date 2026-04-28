# MEMORY.md - Long Term Memory

This file stores important decisions, lessons learned, and key information that should persist across sessions.

---

## 2026-04-26

- 项目目录已整理完成，分类清晰：
  - `webProj/` → Flask网页项目（待办清单 + 词汇网站）
  - `Amazon/` → 亚马逊商品排名监控脚本
  - `Map/` → 高德地图查询脚本
  - `archive/` → 截图和SVG归档
  - `memory/` → 每日工作记录

- 飞书语音识别对接总结：
  - 已完成代码对接，但API权限仅对飞书旗舰版企业开放
  - 当前企业版本无法开通 `ai.asr.speech_recognize` 权限
  - 代码已就绪，企业升级到旗舰版后即可直接使用

- 待办网站服务保持 7*24 在线运行
  - HTTPS：`0.0.0.0:8080` → `https://101.96.196.120:8080/`
  - HTTP：`0.0.0.0:8081` → `http://101.96.196.120:8081/`
- 服务器公网IP：`101.96.196.120`

- 问题修复记录：
  - v3.1.9 修复了 `API_BASE` 变量重复定义冲突，导致API调用失败不显示任务列表bug

**最新版本：v3.6.3**
最新改动：title和版本号居中，task字体缩小一号，弹窗按钮居中，确认按钮背景色和add一致

**开发规则（强制遵守）：**
1. ✅ 每次改动代码，必须更新前端版本号（notion-style-todo.html 中显示）
2. ✅ 每次代码改动，必须先做测试，确认测试成功后再发布给用户

## 2026-04-28

- 每日任务执行情况：
  - 07:10 AM 已完成：汇率天气预报发送、亚马逊排名更新、GitHub备份
  - 淘宝购物车监控因需要登录未执行（需手动登录）
  - 10:47 AM 补跑10:00 AM任务：亚马逊商品搜索截图，两个ASIN均成功找到并截图，排名更新完成
  - 任务脚本 `amazon_search_mosaic_kits.py` 运行正常，两个目标ASIN都在搜索结果第一页找到

