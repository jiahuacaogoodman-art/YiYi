# 医学刷题平台 API 对接说明

基础地址：`http://localhost:8000/api`

鉴权：登录后在请求头添加 `Authorization: Bearer <access_token>`。

## 认证

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/auth/login` | 登录，返回 JWT |
| POST | `/auth/register` | 注册学生账号 |
| GET | `/auth/me` | 当前登录用户 |
| POST | `/auth/logout` | 前端清 token 即可，后端返回成功 |

## 学生端

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/subjects` | 科目分栏，带题量和用户进度 |
| GET | `/chapters?subject_id=1` | 章节列表 |
| GET | `/knowledge-points?chapter_id=1` | 知识点列表 |
| GET | `/questions` | 题目列表，支持分页和筛选 |
| GET | `/questions/{id}` | 题目详情 |
| POST | `/practice/start` | 按模式开始练习 |
| POST | `/practice/answer` | 提交答案并判分 |
| GET | `/practice/wrong` | 错题本 |
| GET | `/practice/favorites` | 收藏题 |
| POST | `/questions/{id}/favorite` | 收藏题目 |
| DELETE | `/questions/{id}/favorite` | 取消收藏 |
| GET | `/exams` | 公开试卷列表 |
| GET | `/exams/{id}` | 试卷详情 |
| POST | `/exams/{id}/start` | 开始考试 |
| POST | `/exams/{id}/submit` | 提交考试 |
| GET | `/exams/records/{id}` | 考试记录 |
| POST | `/questions/{id}/feedback` | 提交题目纠错 |
| GET | `/statistics/user` | 学习统计 |

## 管理后台

所有 `/admin/*` 接口需要管理员或超级管理员。

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/admin/statistics/dashboard` | 后台控制台 |
| POST | `/admin/subjects` | 新增科目 |
| PUT | `/admin/subjects/{id}` | 编辑科目 |
| DELETE | `/admin/subjects/{id}` | 删除科目 |
| POST | `/admin/subjects/reorder` | 拖拽排序保存 |
| POST | `/admin/chapters` | 新增章节 |
| PUT | `/admin/chapters/{id}` | 编辑章节 |
| DELETE | `/admin/chapters/{id}` | 删除章节 |
| POST | `/admin/chapters/batch-status` | 批量启用/禁用章节 |
| POST | `/admin/knowledge-points` | 新增知识点 |
| PUT | `/admin/knowledge-points/{id}` | 编辑知识点 |
| DELETE | `/admin/knowledge-points/{id}` | 删除知识点 |
| POST | `/admin/knowledge-points/import` | 批量导入知识点 |
| POST | `/admin/questions` | 新增题目 |
| PUT | `/admin/questions/{id}` | 编辑题目 |
| DELETE | `/admin/questions/{id}` | 软删除题目 |
| POST | `/admin/questions/{id}/restore` | 从回收站恢复 |
| DELETE | `/admin/questions/{id}/hard` | 彻底删除 |
| POST | `/admin/questions/batch` | 批量操作 |
| GET | `/admin/questions/export` | 导出题目 Excel |
| GET | `/admin/questions/import/template` | 下载导入模板 |
| POST | `/admin/questions/import` | 上传 Excel 并预览校验，兼容原始需求路径 |
| POST | `/admin/questions/import/preview` | 上传 Excel 并预览校验 |
| POST | `/admin/questions/import/confirm` | 确认导入，支持自动创建、手动映射、跳过行 |
| GET | `/admin/questions/import/records` | 导入记录 |
| GET | `/admin/questions/import/records/{id}` | 导入记录详情和逐行预览 |
| GET | `/admin/questions/import/records/{id}/error-report` | 下载导入错误报告 |
| POST | `/admin/questions/check-duplicate` | 查重 |
| POST | `/admin/upload/image` | 上传题干或解析图片 |
| GET | `/admin/exams` | 后台试卷列表 |
| POST | `/admin/exams` | 创建试卷 |
| POST | `/admin/exams/auto-generate` | 自动组卷 |
| PUT | `/admin/exams/{id}` | 编辑试卷 |
| POST | `/admin/exams/{id}/publish` | 发布试卷 |
| POST | `/admin/exams/{id}/offline` | 下架试卷 |
| GET | `/admin/exams/{id}/statistics` | 试卷统计 |
| GET | `/admin/users` | 用户列表 |
| POST | `/admin/users` | 创建管理员账号，超级管理员限定 |
| PUT | `/admin/users/{id}/status` | 启用/禁用用户 |
| POST | `/admin/users/{id}/reset-password` | 重置密码 |
| GET | `/admin/feedback` | 反馈列表 |
| PUT | `/admin/feedback/{id}` | 处理反馈 |
| GET | `/admin/logs` | 操作日志 |
| GET | `/admin/settings` | 系统设置 |
| PUT | `/admin/settings/{key}` | 修改系统设置，超级管理员限定 |

## 常用枚举

- 题型：`single_choice` 单选，`multiple_choice` 多选，`true_false` 判断，`fill_blank` 填空，`short_answer` 简答
- 难度：`easy` 简单，`medium` 中等，`hard` 困难
- 重要程度：`normal` 普通，`key` 重点，`frequent` 高频
- 题目状态：`draft` 草稿，`pending_review` 待审核，`published` 已发布，`offline` 已下架
- 反馈状态：`pending` 未处理，`processing` 处理中，`resolved` 已处理，`ignored` 已忽略
