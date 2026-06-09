# 医学刷题平台

这是一个面向医学生、执业医师考试和期末复习的医学刷题系统。当前包含 React 前端、FastAPI 后端、数据库模型、认证权限、题库管理、批量导入导出、刷题记录、错题本、收藏、模拟考试、反馈纠错、统计、操作日志、Docker、Seed 数据和接口文档。

## 目录结构

```text
medical-quiz-platform/
  backend/
    app/
      api/routers/          REST API 路由
      core/                 配置、安全、异常处理
      db/                   数据库连接和 Base
      models/               SQLAlchemy 数据模型
      schemas/              Pydantic 入参出参
      services/             判分、导入、统计等业务逻辑
      utils/                通用工具
    alembic/                数据库迁移
    scripts/                初始化、模板生成脚本
    tests/                  基础接口测试
    assets/                 Excel 模板生成输出目录
    uploads/                导入文件和错误报告目录
    Dockerfile
    requirements.txt
  frontend/
    src/                    React + TypeScript 前端源码
    package.json
    vite.config.ts
  docs/
    api.md                  前端对接接口说明
  docker-compose.yml
  .env.example
```

## 本地启动

后端：

```bash
cd /Users/caojiahua/Downloads/medical-quiz-platform/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python scripts/generate_excel_template.py
python scripts/seed.py
uvicorn app.main:app --reload
```

前端：

```bash
cd /Users/caojiahua/Downloads/medical-quiz-platform/frontend
pnpm install
pnpm dev
```

启动后访问：

- API: http://localhost:8000
- 前端: http://localhost:5173
- Swagger 文档: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Excel 模板下载: http://localhost:8000/api/admin/questions/import/template

默认管理员：

- 用户名：`admin`
- 密码：`admin123456`

## Docker 启动

```bash
cd /Users/caojiahua/Downloads/medical-quiz-platform
docker compose up --build
```

Docker 默认使用 PostgreSQL。开发环境直接跑后端时默认使用 SQLite。

## 前端配置

前端默认读取：

```text
VITE_API_BASE_URL=http://localhost:8000/api
```

登录后把 `access_token` 放到请求头：

```text
Authorization: Bearer <token>
```

学生端、后台端需要的主接口都在 [docs/api.md](/Users/caojiahua/Downloads/medical-quiz-platform/docs/api.md) 和 Swagger 中。Excel 导入模板会由 `python scripts/generate_excel_template.py` 或模板下载接口生成到 `backend/assets/`。

## 已实现能力

### 前端

- 中文登录/注册页，默认管理员账号可直接进入后台
- 学生端：首页、题库选择、刷题、错题本、收藏题、模拟考试、学习统计
- 做题页支持单选、多选、判断、填空、简答、图片、解析、收藏和反馈纠错
- 后台端：控制台、科目分栏、章节、知识点、题目管理、批量导入、套卷管理、用户管理、反馈、数据统计、日志、系统设置
- 后台题目表单支持题干图片和解析图片上传
- 使用 React + TypeScript + Vite + Ant Design + Zustand + Axios + ECharts

### 后端

- JWT 登录、注册、当前用户、角色权限隔离
- 普通用户、管理员、超级管理员三类角色
- 科目、章节、知识点管理
- 题目 CRUD、软删除、回收站恢复、彻底删除
- 题目选项、标签、图片 URL、状态、难度、来源、统计字段
- 管理员图片上传，供题干图片和解析图片使用
- 批量发布、下架、删除、改分类、改难度、打标签
- Excel 模板下载、Excel 导入预览、确认导入、错误报告、导入记录
- 导入确认支持科目/章节/知识点自动创建、手动匹配和跳过行
- Excel 导出题目
- 重复题检测，包含完全重复和相似度提示
- 顺序、随机、章节、知识点、错题、收藏、未做、高频错题等刷题入口
- 单选、多选、判断、填空、简答基础判分
- 答错自动进入错题本，再答错累加错误次数
- 收藏/取消收藏
- 模拟考试列表、开考、交卷、成绩、答题记录
- 手动组卷、自动组卷、发布/下架
- 自动组卷支持按简单/中等/困难比例抽题
- 题目反馈纠错和后台处理
- 用户学习统计和后台仪表盘统计
- 用户管理、禁用启用、重置密码
- 超级管理员创建管理员账号
- 操作日志、系统设置
- Alembic 迁移和 seed 示例数据不少于 20 道题