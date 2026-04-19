# 赛事数据爬取脚本使用说明

## 脚本列表

### 1. crawl_all.py - 通用爬取脚本
支持灵活的参数配置，适合手动测试和一次性爬取。

**使用方式：**
```bash
# 爬取3页列表页，处理5个详情页，跳过AI处理
uv run python scripts/crawl_all.py --list-pages 3 --detail-pages 5 --skip-ai

# 爬取全部70页，处理所有新赛事，包含AI处理
uv run python scripts/crawl_all.py --list-pages 70
```

**参数说明：**
- `--list-pages N`: 爬取多少页列表页（默认5页）
- `--detail-pages N`: 最多处理多少个详情页（默认不限制）
- `--skip-ai`: 跳过AI智能处理

---

### 2. scheduled_crawl.py - 定时任务脚本
支持定时运行，适合部署为每天自动更新。

**使用方式：**
```bash
# 立即运行一次全量爬取（70页）
uv run python scripts/scheduled_crawl.py --full

# 立即运行一次，只爬取10页
uv run python scripts/scheduled_crawl.py --full --list-pages 10

# 启动定时任务，每天凌晨2点自动运行
uv run python scripts/scheduled_crawl.py --schedule

# 启动定时任务，每天早上8点运行，每次爬取20页
uv run python scripts/scheduled_crawl.py --schedule --time 08:00 --list-pages 20
```

**参数说明：**
- `--full`: 立即运行一次
- `--schedule`: 启动定时任务模式
- `--list-pages N`: 每次爬取多少页（默认70页）
- `--time HH:MM`: 定时运行时间（默认02:00）
- `--skip-ai`: 跳过AI处理

---

### 3. test_single.py - 单页测试脚本
测试单个详情页的爬取和AI处理。

```bash
uv run python scripts/test_single.py
```

---

### 4. test_with_attachments.py - 附件下载测试
测试附件下载功能。

```bash
uv run python scripts/test_with_attachments.py
```

---

## 推荐使用流程

### 首次使用 - 全量爬取
```bash
# 爬取全部70页历史数据（可能需要几十分钟）
uv run python scripts/crawl_all.py --list-pages 70
```

### 日常更新 - 增量爬取
```bash
# 每天手动运行一次，只爬取前几页检查新内容
uv run python scripts/crawl_all.py --list-pages 10

# 或者设置定时任务自动运行
uv run python scripts/scheduled_crawl.py --schedule --list-pages 10
```

---

## 定时任务部署

### 使用 nohup 后台运行
```bash
cd /home/su/桌面/ysustar/backend
nohup uv run python scripts/scheduled_crawl.py --schedule > crawl.log 2>&1 &
```

### 查看日志
```bash
tail -f /home/su/桌面/ysustar/backend/crawl.log
```

### 停止定时任务
```bash
# 查找进程
ps aux | grep scheduled_crawl

# 杀掉进程
kill <PID>
```

---

## 数据查看

### 启动后端API
```bash
uv run uvicorn campus_ai.main:app --reload
```

访问：
- API文档: http://127.0.0.1:8000/docs
- 赛事列表: http://127.0.0.1:8000/api/v1/contest/list
