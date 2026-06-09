# Kids_Exo 后续发展方向优先级规划 2026-06-09

本文档用于梳理 Kids_Exo 项目接下来几个主要方向的优先级、依赖关系、实施阶段和可验证结果。

当前需要考虑的方向包括：

1. 部署到公网 VPS；
2. 注册 / 登录 / 用户管理；
3. 给学生添加“作业本”页面；
4. 家长异步布置作业，学生也可以自己添加 practice；
5. 未来支持课程；
6. 数学应用题，例如鸡兔同笼、植树问题、相遇追击、水池进水放水等；
7. 更多数学计算类型，例如分数、小数、正负数、混合运算；
8. 几何问题，例如周长、面积、对称性等；
9. 以后继续扩展 badge、statistics、learner dashboard。

---

## 一、总体判断

我的建议是：

```text
不要先部署公网。
不要先做复杂课程系统。
不要先大规模增加题型。
应该先把 Learner / Assignment / Practice / Result 之间的产品结构理清楚。
```

原因是：

- 公网部署会立刻引入账号、权限、安全、数据隔离、备份、HTTPS、域名、日志、隐私等问题；
- 如果作业本和课程模型还没有设计好，公网部署后数据结构会很快反复迁移；
- 如果先大量添加题型，后面再引入作业本、课程、统计，会发现这些题型没有统一的归档、追踪、布置、完成、复习机制；
- 当前最核心的产品闭环应该是：

```text
家长选择内容
    ↓
布置给学生
    ↓
学生完成
    ↓
系统记录结果
    ↓
Dashboard 展示进展
    ↓
系统推荐复习 / 家长继续布置
```

所以，优先级应该围绕这个闭环来排。

---

# 二、推荐优先级总览

## Priority 0 - 稳定现有基础

当前正在进行：

```text
Learner Dashboard 重构
Generic answer pipeline
Renderer / evaluator / plugin metadata 抽象
```

这些是后面所有功能的地基。必须先保持稳定。

## Priority 1 - 作业本 / Assignment Notebook

这是最应该优先做的业务功能。

原因：

- 它连接家长和学生；
- 它可以承载现在已有的 practice；
- 它以后可以承载课程；
- 它可以为 badge、statistics、progress tracking 提供清晰的数据来源；
- 它不需要公网部署也能先在本地开发验证。

## Priority 2 - 用户 / 角色 / 权限模型，本地优先

公网部署之前必须做，但不一定一开始就做完整注册系统。

先做：

```text
Parent
Learner
Role
Local login / simple auth boundary
Data ownership
```

后做：

```text
public registration
email verification
password reset
OAuth
subscription/payment
```

## Priority 3 - 数学内容扩展：先做“计算类”，再做“应用题”，最后做“几何”

数学扩展建议顺序：

```text
A. 分数 / 小数 / 正负数 / 混合运算
B. 简单文字应用题
C. 经典应用题类型
D. 几何
```

原因：

- 计算类题目结构最接近现在的 numeric/text answer pipeline；
- 应用题需要题干模板、变量生成、解题步骤、单位、解释；
- 几何还可能需要图形、diagram renderer、图片/Canvas/SVG，因此依赖更多。

## Priority 4 - 课程系统

课程不要太早做成复杂 LMS。建议先把课程理解成：

```text
Lesson = explanation + examples + linked practices
```

等 Assignment 系统稳定后，再让作业本可以包含 lesson。

## Priority 5 - Badge / Statistics

Badge 和 Statistics 很有价值，但它们依赖稳定的事件和结果数据。

应该先有：

```text
PracticeAttempt
Assignment
Result
Mistake
SkillProgress
```

再做：

```text
BadgeRule
BadgeAward
StatisticsTrend
```

## Priority 6 - 公网 VPS 部署

公网部署应该排在产品结构稳定之后。

上线之前至少要完成：

```text
用户/角色/权限
数据隔离
登录
HTTPS
备份
环境变量管理
数据库迁移
日志
基本安全策略
```

---

# 三、推荐实施路线

## Phase 0 - 完成当前 Learner Dashboard 重构

### 目标

把 Learner Detail 从长页面改成 Dashboard + Tabs + Tables。

### 必须完成

- Practice History 使用 table；
- Mistake Notebook 使用 table；
- Skill Breakdown 使用 table；
- Overview 只显示 top-N summary；
- Badges / Statistics 有 placeholder tab；
- 页面不再因为练习记录增加而无限变长。

### 可验证结果

- Learner detail 页面有 tabs；
- 练习历史可以分页；
- 错题本可以分页；
- 技能表可以排序；
- 原有 review result、create practice from mistakes、open practice 行为不变；
- 现有测试通过。

---

## Phase 1 - 设计并实现 Assignment Notebook MVP

### 目标

给每个 learner 添加一个“作业本”页面。家长可以给学生布置 practice，学生也可以把 practice 加入自己的作业本。

### 为什么先做它

Assignment Notebook 是后续课程、badge、statistics、异步学习的核心容器。

它解决的问题是：

```text
现在 practice 是一次性的。
未来需要有“待完成 / 已完成 / 需要复习 / 家长布置 / 学生自选”的状态管理。
```

### 推荐数据模型

```text
Assignment
- id
- learner_id
- title
- description
- status
  - assigned
  - in_progress
  - completed
  - skipped
  - archived
- source_type
  - parent_assigned
  - learner_added
  - system_recommended
  - lesson_generated
- due_at
- created_by_role
  - parent
  - learner
  - system
- created_at
- completed_at

AssignmentItem
- id
- assignment_id
- item_type
  - practice_plugin
  - saved_practice_session
  - lesson
- plugin
- plugin_settings
- question_count
- feedback_mode
- show_timer
- order_index
- required
- status
- linked_session_id
```

### MVP 范围

第一版只支持：

```text
家长给 learner 添加一个 practice assignment
学生打开 assignment 并开始 practice
practice 完成后 assignment item 标记完成
assignment 全部 item 完成后 assignment 标记 completed
```

### 暂时不要做

- 课程；
- 自动推荐；
- 重复作业；
- complicated due date rules；
- 多学生批量布置；
- notification；
- badge 联动。

### UI 建议

在 Learner Dashboard 中添加 tab：

```text
Homework / 作业本
```

里面显示：

```text
待完成
进行中
已完成
已归档
```

使用 table 或 compact card，不要无限长 card list。

### 可验证结果

- 家长可以从 learner 页面创建 assignment；
- assignment 可以包含一个现有 practice plugin；
- 学生可以从作业本打开 practice；
- 学生完成 practice 后 assignment item 状态更新；
- 作业本能显示 assigned / completed；
- 原有直接创建 practice 的功能不被破坏；
- 后端有 assignment tests；
- 前端有 assignment UI tests。

---

## Phase 2 - 本地用户 / 角色 / 权限模型

### 目标

为未来公网部署做准备，但先不急着公开注册。

### 推荐角色

```text
Parent
Learner
Admin
```

### 推荐概念

```text
Account
- id
- email
- display_name
- password_hash 或外部 auth id
- created_at

Household
- id
- name
- owner_account_id

HouseholdMember
- household_id
- account_id
- role
  - parent
  - child
  - admin

LearnerProfile
- id
- household_id
- nickname
- optional_account_id
- active
```

### 为什么需要 Household

因为一个家长可能管理多个孩子；以后也可能两个家长管理同一个 household。

### MVP 范围

先支持：

```text
本地单 parent account
parent 登录后只能看到自己的 learners
learner profile 归属于 parent/household
```

### 暂时不要做

- 公开注册；
- email verification；
- password reset；
- OAuth；
- payment；
- multi-tenant admin panel。

### 可验证结果

- 未登录不能访问管理页面；
- 登录 parent 只能看到自己的 learners；
- learner/session/assignment 都归属于 household；
- API 层有权限检查；
- 原有 learner 数据可迁移或兼容；
- 后端权限测试通过。

---

## Phase 3 - 数学计算类内容扩展

### 目标

先扩展最容易落地的数学内容类型：

```text
分数计算
小数计算
正负数计算
混合运算
```

### 为什么这类先做

它们大多仍然是 structured answer：

```text
numeric_answer
text_answer
fraction_answer
```

比应用题和几何更容易接入现有 evaluator / renderer / result pipeline。

### 推荐新增 answer types

```text
decimal_exact
fraction_exact
fraction_equivalent
signed_integer_exact
expression_exact
```

### 推荐新增 renderers

```text
decimal_answer_renderer
fraction_answer_renderer
expression_answer_renderer
```

### 推荐 plugin 分类

```text
Math / Arithmetic / Fractions
Math / Arithmetic / Decimals
Math / Arithmetic / Integers
Math / Arithmetic / Mixed Operations
```

### MVP 顺序

1. 正负数加减法；
2. 小数加减乘除；
3. 分数加减；
4. 分数乘除；
5. 四则混合运算。

### 可验证结果

- 每类至少一个 plugin；
- 每个 plugin 有 metadata；
- 每个 plugin 可从 Parent Studio 创建 practice；
- 每类题目可以完成并记录结果；
- 错题本能显示 expected/submitted answer；
- result review 不依赖 integer column；
- backend evaluator tests 覆盖新 answer types；
- frontend renderer tests 覆盖新 input UI。

---

## Phase 4 - 简单应用题框架

### 目标

在不做复杂 AI 解题的情况下，先支持模板化数学应用题。

### 为什么不能太早做复杂应用题

应用题不仅是答案，还包括：

```text
题干生成
变量约束
单位
解题步骤
解释
多步推理
可能存在多个等价解法
```

所以要先做框架。

### 推荐模型

```text
WordProblemTemplate
- id
- plugin
- problem_type
- prompt_template
- variable_schema
- solution_schema
- explanation_template
- answer_type
- difficulty

GeneratedWordProblem
- prompt
- variables
- expected_answer
- explanation_steps
- units
```

### 先支持的问题类型

建议顺序：

1. 和差倍问题；
2. 鸡兔同笼；
3. 植树问题；
4. 相遇问题；
5. 追击问题；
6. 水池进水放水问题。

### 推荐 renderer

第一版可以仍然使用：

```text
text prompt + numeric answer
```

后续再支持：

```text
step-by-step answer
hint
solution explanation
diagram
```

### 可验证结果

- 每个应用题 plugin 可以生成可重复题目；
- seed 相同时题目一致；
- evaluator 能判断最终答案；
- result review 能显示正确答案；
- 可以显示 explanation；
- 至少有一个 problem type 有完整 tests；
- 不影响现有 arithmetic plugins。

---

## Phase 5 - Lesson MVP

### 目标

不要一开始做完整课程系统。先做最小 lesson：

```text
Lesson = 讲解 + 例题 + 关联 practice
```

### Lesson 和 Assignment 的关系

建议关系是：

```text
Assignment 可以包含 Lesson
Assignment 可以包含 Practice
Lesson 可以推荐 Practice
Course 可以包含多个 Lesson
```

也就是：

```text
Course
  └── Lesson
        ├── Explanation
        ├── Example Questions
        └── Practice Links

Assignment
  ├── Lesson Item
  └── Practice Item
```

### 推荐数据模型

```text
Lesson
- id
- title
- subject
- topic
- content_blocks
- related_plugins
- created_at

LessonProgress
- learner_id
- lesson_id
- status
- started_at
- completed_at
```

### MVP 范围

先支持：

```text
静态 lesson 页面
lesson 中显示解释和例题
lesson 下方有 Start Practice
assignment item 可以引用 lesson
```

### 暂时不要做

- rich course authoring UI；
- video course；
- adaptive learning path；
- AI-generated lessons；
- full LMS。

### 可验证结果

- 可以打开 lesson；
- lesson 可以链接到 practice；
- assignment 可以包含 lesson item；
- lesson progress 可以记录 completed；
- learner dashboard 可以显示 lesson progress。

---

## Phase 6 - Badge MVP

### 目标

在 Assignment 和 Result 稳定后，再做 badge。

### 为什么不要太早做

Badge 依赖稳定事件：

```text
practice completed
assignment completed
perfect score
streak
skill accuracy
mistake resolved
```

如果这些事件还没有统一，badge 会写成很多临时逻辑。

### 推荐模型

```text
BadgeDefinition
- id
- code
- name
- description
- icon
- level
- parent_badge_id
- active

BadgeRule
- id
- badge_definition_id
- rule_type
- rule_config_json
- active

LearnerBadge
- learner_id
- badge_definition_id
- status
- progress_current
- progress_target
- awarded_at

BadgeEvent
- learner_id
- badge_definition_id
- event_type
- source_session_id
- source_assignment_id
- metadata_json
- created_at
```

### MVP badge rules

先支持内置规则：

```text
完成一次全对 practice
连续 3 次全对
完成 5 个 assignments
某个 skill 正确率达到 90%
```

家长自定义 rule 可以后做。

### 可验证结果

- 完成全对 practice 后获得 badge；
- dashboard badge tab 显示 badge；
- badge event 被记录；
- 重复完成不会重复发同一个不可重复 badge；
- tests 覆盖 badge awarding。

---

## Phase 7 - Statistics 扩展

### 目标

从简单 summary 扩展到趋势分析。

### 建议统计维度

```text
Accuracy over time
Practice time over time
Skill accuracy
Subject comparison
Mistake recurrence
Assignment completion rate
Badge progress
```

### 实施前提

最好先有：

```text
Assignment
PracticeResult
Skill tags
BadgeEvent
```

### 可验证结果

- dashboard statistics tab 有真实数据；
- 可以按时间范围过滤；
- 可以按 subject / skill 过滤；
- 不显示 fake statistics；
- tests 覆盖统计计算。

---

## Phase 8 - 公网 VPS 部署准备

### 目标

只有在用户/权限/数据隔离稳定后，才部署公网。

### 上线前必须完成

```text
登录 / 认证
用户和 household 数据隔离
HTTPS
反向代理
数据库迁移
环境变量管理
备份
日志
错误监控
最基本安全策略
```

### 推荐部署形态

```text
VPS
├── Nginx / Caddy
├── FastAPI backend
├── Angular static frontend
├── PostgreSQL
├── Alembic migration
└── backup script
```

### 不建议一开始做

```text
公开注册
在线支付
多租户管理后台
复杂 admin 系统
```

可以先做：

```text
private beta
手动创建 parent account
只给自己家庭或少数朋友使用
```

### 可验证结果

- HTTPS 可访问；
- 未登录不能进入管理页面；
- API 不泄漏其他用户数据；
- 数据库可备份恢复；
- 部署流程可重复；
- migration 可在 VPS 上运行；
- 日志能看到错误。

---

# 四、最终推荐顺序

## 最推荐路线

```text
0. 完成 Learner Dashboard 重构
1. Assignment Notebook MVP
2. 本地用户 / 角色 / 权限模型
3. 数学计算类扩展
4. 简单应用题框架
5. Lesson MVP
6. Badge MVP
7. Statistics 扩展
8. VPS private beta 部署
9. 更完整的公网注册 / 用户管理
10. 几何内容扩展
```

## 为什么几何排得靠后

几何很重要，但它通常需要：

```text
图形渲染
SVG/Canvas
diagram metadata
不同答案类型
可能有多步骤解释
```

比纯计算和文字应用题复杂。因此建议等 renderer 架构和 lesson/assignment 结构更稳定后再做。

## 为什么公网部署不排第一

公网部署不是单纯把代码放到 VPS。它会强迫你处理：

```text
认证
权限
数据隔离
安全
备份
隐私
错误恢复
迁移
```

如果产品模型还在快速变化，公网部署会放大维护成本。

## 为什么 Assignment Notebook 排第一

因为它是整个学习产品的核心组织方式：

```text
家长布置
学生完成
系统记录
Dashboard 展示
Badge / Statistics / Lesson 全部可以挂在它上面
```

---

# 五、给 Codex 的下一步建议

下一份具体实现文档建议先写：

```text
Assignment Notebook MVP Implementation Plan
```

范围只包含：

```text
Assignment / AssignmentItem 数据模型
后端 CRUD API
Learner Dashboard Homework tab
从 Parent Studio 或 Learner Detail 创建 assignment
学生从 assignment 启动 practice
完成 practice 后更新 assignment item 状态
tests
```

不要在同一轮里同时做：

```text
课程
badge
公网部署
复杂应用题
几何
```

这样任务边界最清晰，结果也最容易验证。
