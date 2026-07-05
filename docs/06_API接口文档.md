# 参数表配置辅助工具 - API接口文档

## 1. 接口概述

### 1.1 文档说明
本文档描述参数表配置辅助工具的所有HTTP接口，包括接口路径、请求方法、参数说明和响应格式。

### 1.2 基础信息

| 项目 | 值 |
|------|------|
| 服务地址 | http://127.0.0.1:8080 |
| 接口前缀 | / |
| 请求格式 | HTTP GET/POST |
| 响应格式 | HTML页面渲染 |
| 认证方式 | 无（开发环境） |

### 1.3 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 403 | 权限不足（CSRF验证失败） |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 2. 首页接口

### 2.1 获取首页数据

**接口路径**：`/`

**请求方法**：GET

**功能描述**：获取系统首页数据，包含各模块统计信息

**请求参数**：无

**响应说明**：
- 返回首页HTML页面
- 包含参数表、需求、任务书、配置脚本统计卡片

---

## 3. 参数表管理接口

### 3.1 获取参数表列表

**接口路径**：`/tables/`

**请求方法**：GET

**功能描述**：获取参数表列表，支持筛选和搜索

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| domain | string | 否 | 业务领域筛选 |
| status | string | 否 | 状态筛选（draft/active/deprecated） |
| search | string | 否 | 搜索关键词 |

**响应说明**：
- 返回参数表列表HTML页面
- 包含筛选表单和参数表表格

---

### 3.2 获取参数表详情

**接口路径**：`/tables/<table_id>/`

**请求方法**：GET

**功能描述**：获取参数表详细信息，包含字段定义列表

**路径参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| table_id | string | 参数表ID |

**响应说明**：
- 返回参数表详情HTML页面
- 包含参数表基本信息、字段定义列表、关联INDEXID配置

---

## 4. 元数据管理接口

### 4.1 获取元数据列表

**接口路径**：`/metadata/`

**请求方法**：GET

**功能描述**：获取元数据配置列表，支持按字段类型筛选

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| field_type | string | 否 | 字段类型筛选 |

**响应说明**：
- 返回元数据列表HTML页面
- 包含元数据表格

---

## 5. 需求管理接口

### 5.1 获取需求列表

**接口路径**：`/requirements/`

**请求方法**：GET

**功能描述**：获取需求列表，支持按状态筛选

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| status | string | 否 | 状态筛选（pending/approved/in_progress/completed/rejected） |

**响应说明**：
- 返回需求列表HTML页面
- 包含状态统计和需求表格

---

### 5.2 获取需求详情

**接口路径**：`/requirements/<req_id>/`

**请求方法**：GET

**功能描述**：获取需求详细信息，包含关联文档和测试用例

**路径参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| req_id | string | 需求ID |

**响应说明**：
- 返回需求详情HTML页面
- 包含需求信息、关联任务书、关联测试用例

---

### 5.3 创建需求

**接口路径**：`/requirements/create/`

**请求方法**：GET / POST

**功能描述**：创建新需求

**GET请求参数**：无

**POST请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| title | string | 是 | 需求标题 |
| requirement_type | string | 是 | 需求类型（new/modify/reuse） |
| parameter_table | string | 否 | 关联参数表ID |
| business_description | string | 是 | 业务说明 |
| requester | string | 是 | 申请人 |
| story_points | integer | 否 | 故事点 |
| sprint | string | 否 | 冲刺 |

**响应说明**：
- GET：返回新建需求表单页面
- POST：成功后重定向到需求列表页面

---

## 6. 任务书管理接口

### 6.1 获取任务书列表

**接口路径**：`/task-documents/`

**请求方法**：GET

**功能描述**：获取任务书列表

**请求参数**：无

**响应说明**：
- 返回任务书列表HTML页面
- 包含任务书表格

---

### 6.2 导出任务书

**接口路径**：`/task-documents/export/<doc_id>/`

**请求方法**：GET

**功能描述**：导出任务书文档

**路径参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| doc_id | string | 任务书ID |

**响应说明**：
- 返回任务书内容（Word/PDF格式）

---

## 7. 配置脚本接口

### 7.1 获取配置脚本列表

**接口路径**：`/config-scripts/`

**请求方法**：GET

**功能描述**：获取配置脚本列表，支持按状态筛选

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| status | string | 否 | 状态筛选（generated/submitted/deployed/failed） |

**响应说明**：
- 返回配置脚本列表HTML页面
- 包含脚本表格

---

## 8. INDEXID配置接口

### 8.1 获取INDEXID配置列表

**接口路径**：`/index-id/`

**请求方法**：GET

**功能描述**：获取INDEXID配置列表

**请求参数**：无

**响应说明**：
- 返回INDEXID配置列表HTML页面
- 包含配置表格

---

## 9. 测试用例接口

### 9.1 获取测试用例列表

**接口路径**：`/test-cases/`

**请求方法**：GET

**功能描述**：获取测试用例列表，支持按类型筛选

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| case_type | string | 否 | 用例类型筛选（normal/boundary/exception） |

**响应说明**：
- 返回测试用例列表HTML页面
- 包含用例表格

---

## 10. 自动化测试结果接口

### 10.1 获取测试结果概览

**接口路径**：`/automation-test/`

**请求方法**：GET

**功能描述**：获取自动化测试结果概览

**请求参数**：无

**响应说明**：
- 返回测试结果概览HTML页面
- 包含测试统计和结果列表

---

## 11. SQL脚本维护接口

### 11.1 SQL管理页面

**接口路径**：`/sql-manager/`

**请求方法**：GET / POST

**功能描述**：SQL脚本执行界面

**GET请求参数**：无

**POST请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| sql | string | 是 | SQL语句 |

**响应说明**：
- GET：返回SQL管理页面
- POST：返回SQL执行结果页面

**注意事项**：
- 支持SELECT、INSERT、UPDATE、DELETE操作
- 执行前请确认操作的安全性

---

## 12. AI辅助分析接口

### 12.1 AI分析首页

**接口路径**：`/ai-analysis/`

**请求方法**：GET

**功能描述**：AI分析首页，包含参数表选择表单

**请求参数**：无

**响应说明**：
- 返回AI分析首页HTML页面
- 包含参数表统一分析和字段规范检查表单

---

### 12.2 参数表统一分析

**接口路径**：`/ai-analysis/unification/`

**请求方法**：POST

**功能描述**：分析参数表是否可以统一到SIMPLELIST表

**POST请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| table_id | string | 是 | 参数表ID |

**响应说明**：
- 返回分析结果页面
- 包含评分、评分详情、建议、最终推荐

**分析结果字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | 是否分析成功 |
| confidence | float | 置信度（0-1） |
| result | string | 分析结果摘要 |
| details.score | float | 统一可行性评分（0-1） |
| details.score_details | array | 评分详情列表 |
| details.suggestions | array | 建议列表 |
| details.recommendation | string | 最终推荐 |

---

### 12.3 字段定义规范性分析

**接口路径**：`/ai-analysis/normalization/`

**请求方法**：POST

**功能描述**：检查字段定义是否符合规范

**POST请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| table_id | string | 是 | 参数表ID |

**响应说明**：
- 返回检查结果页面
- 包含问题统计、问题详情列表

**检查结果字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | 是否检查成功 |
| confidence | float | 置信度（0-1） |
| result | string | 检查结果摘要 |
| details.issues_count | integer | 总问题数 |
| details.error_count | integer | 错误数 |
| details.warning_count | integer | 警告数 |
| details.issues | array | 问题详情列表 |

**问题详情字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| field | string | 字段名 |
| type | string | 问题类型（命名规范/类型匹配/长度设置） |
| severity | string | 严重程度（error/warning） |
| message | string | 问题描述 |
| suggestion | string | 建议修改方案 |

---

## 13. AI智能生成接口

### 13.1 AI生成首页

**接口路径**：`/ai-generation/`

**请求方法**：GET

**功能描述**：AI生成首页，包含任务书、测试用例、SQL生成表单

**请求参数**：无

**响应说明**：
- 返回AI生成首页HTML页面
- 包含三个生成功能表单

---

### 13.2 任务书生成

**接口路径**：`/ai-generation/task-document/`

**请求方法**：POST

**功能描述**：根据需求自动生成任务书文档

**POST请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| requirement_id | string | 是 | 需求ID |

**响应说明**：
- 返回生成结果页面
- 包含任务书内容、字数统计、章节列表

**生成结果字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | 是否生成成功 |
| confidence | float | 置信度（0-1） |
| result | string | 生成结果摘要 |
| details.content | string | 任务书内容（Markdown格式） |
| details.word_count | integer | 字数统计 |
| details.field_count | integer | 字段数 |
| details.sections | array | 章节列表 |

---

### 13.3 测试用例生成

**接口路径**：`/ai-generation/test-case/`

**请求方法**：POST

**功能描述**：根据需求自动生成测试用例

**POST请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| requirement_id | string | 是 | 需求ID |

**响应说明**：
- 返回生成结果页面
- 包含测试用例统计和测试用例列表

**生成结果字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | 是否生成成功 |
| confidence | float | 置信度（0-1） |
| result | string | 生成结果摘要 |
| details.total_cases | integer | 总用例数 |
| details.normal_count | integer | 正常流程用例数 |
| details.boundary_count | integer | 边界条件用例数 |
| details.exception_count | integer | 异常场景用例数 |
| details.cases | array | 测试用例列表 |

**测试用例字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| case_no | string | 用例编号 |
| title | string | 用例标题 |
| case_type | string | 用例类型（normal/boundary/exception） |
| priority | string | 优先级（high/medium/low） |
| preconditions | string | 前置条件 |
| steps | string | 测试步骤 |
| expected_result | string | 预期结果 |

---

### 13.4 SQL语句生成

**接口路径**：`/ai-generation/sql/`

**请求方法**：POST

**功能描述**：根据自然语言描述自动生成SQL语句

**POST请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| table_id | string | 是 | 参数表ID |
| natural_query | string | 是 | 自然语言查询描述 |

**响应说明**：
- 返回生成结果页面
- 包含生成的SQL语句、SQL类型、目标表名

**生成结果字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | 是否生成成功 |
| confidence | float | 置信度（0-1） |
| result | string | 生成结果摘要 |
| details.sql | string | 生成的SQL语句 |
| details.table | string | 目标表名 |
| details.type | string | SQL类型（SELECT/INSERT/UPDATE/DELETE） |

---

## 14. 错误处理

### 14.1 CSRF验证失败

**错误信息**：`403 Forbidden - CSRF cookie not set`

**原因**：表单提交时未携带CSRF令牌

**解决方案**：
- 在表单中添加 `{% csrf_token %}` 标签
- 使用Django测试客户端（Client）自动处理CSRF

### 14.2 资源不存在

**错误信息**：`404 Not Found`

**原因**：请求的资源ID不存在

**解决方案**：
- 检查资源ID是否正确
- 确认资源已创建

### 14.3 服务器内部错误

**错误信息**：`500 Internal Server Error`

**原因**：服务器处理请求时发生异常

**解决方案**：
- 查看服务器日志定位错误原因
- 检查代码逻辑

### 14.4 数据库锁定

**错误信息**：`database is locked`

**原因**：SQLite数据库被其他进程锁定

**解决方案**：
- 停止Django开发服务器
- 等待其他进程释放数据库
- 重新启动服务器

---

## 15. 接口使用示例

### 15.1 查询参数表列表

```bash
GET /tables/?domain=系统管理&status=active&search=CONFIG
```

### 15.2 获取参数表详情

```bash
GET /tables/1/
```

### 15.3 创建需求

```bash
POST /requirements/create/
Content-Type: application/x-www-form-urlencoded

title=新增系统配置参数表
requirement_type=new
business_description=为系统新增配置参数表，用于管理系统运行参数
requester=张三
```

### 15.4 参数表统一分析

```bash
POST /ai-analysis/unification/
Content-Type: application/x-www-form-urlencoded

table_id=1
```

### 15.5 生成测试用例

```bash
POST /ai-generation/test-case/
Content-Type: application/x-www-form-urlencoded

requirement_id=1
```

### 15.6 生成SQL语句

```bash
POST /ai-generation/sql/
Content-Type: application/x-www-form-urlencoded

table_id=1
natural_query=查询所有状态为active的记录
```

---

## 16. 接口统计

### 16.1 接口分类统计

| 模块 | 接口数 |
|------|--------|
| 首页 | 1 |
| 参数表管理 | 2 |
| 元数据管理 | 1 |
| 需求管理 | 3 |
| 任务书管理 | 2 |
| 配置脚本 | 1 |
| INDEXID配置 | 1 |
| 测试用例 | 1 |
| 自动化测试结果 | 1 |
| SQL脚本维护 | 1 |
| AI辅助分析 | 3 |
| AI智能生成 | 4 |
| **合计** | **21** |

### 16.2 请求方法统计

| 请求方法 | 接口数 |
|----------|--------|
| GET | 16 |
| POST | 5 |
| **合计** | **21** |

---

## 17. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-07-05 | 初始版本，包含所有基础功能和AI功能接口 |