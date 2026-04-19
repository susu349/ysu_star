---
name: git-task-manager
description: Git 版本控制与任务管理助手 - 自动记录代码变更，管理开发任务
type: 项目管理
---

# Git 任务管理助手

## 核心原则

### 每次代码变更都要提交 Git
- **修改代码前**：检查 git 状态，确认当前分支
- **完成一组功能/修复后**：立即 git add + git commit
- **提交信息规范**：清晰描述变更内容（中文）

### 任务管理流程
1. 使用 `TaskCreate` 创建开发任务
2. 使用 `TaskUpdate` 标记任务进度（in_progress/completed）
3. 任务完成后，立即执行 Git 提交
4. 使用 `TaskList` 查看当前任务状态

## Git 提交规范

### 提交信息格式
```
<类型>: <简短描述>

<详细描述（可选）>
```

### 类型说明
- `feat`: 新功能
- `fix`: 修复 bug
- `refactor`: 重构代码
- `style`: 代码格式调整
- `docs`: 文档更新
- `test`: 测试相关
- `chore`: 构建/工具相关

### 示例
```
feat: 添加赛事搜索和排序功能
- 后端添加 search/order_by 参数
- 前端添加搜索框和排序选择
- 支持按 URL 数字排序

fix: 修复赛事列表 limit 参数验证
- 将 limit 最大值从 100 改为 1000
```

## 工作流程

1. **开始工作**
   - 运行 `git status` 检查当前状态
   - 使用 `TaskCreate` 创建任务

2. **开发过程**
   - 编写/修改代码
   - 使用 `TaskUpdate` 标记进度
   - 阶段性提交 Git

3. **完成功能**
   - 运行 `git add <文件>`
   - 运行 `git commit -m "<提交信息>"`
   - 使用 `TaskUpdate` 标记 completed

## 当前项目
校园AI助手 - 赛事推荐与组队系统

让我们开始吧！
