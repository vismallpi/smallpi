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

**最新版本：v3.3.5**
最新改动：改成Notion简约风格，低饱和度配色，更简洁专业

**开发规则（强制遵守）：**
1. ✅ 每次改动代码，必须更新前端版本号（notion-style-todo.html 中显示）
2. ✅ 每次代码改动，必须先做测试，确认测试成功后再发布给用户

