# 儿童练习题生成器 - 产品设计记录

## 项目目的

这个项目帮助家长为孩子创建有针对性的练习题。目前的真实需求，是为在加拿大读四年级和五年级的孩子加强数学计算基础，并配合更系统的速算方法教学。

第一个交付目标有意保持很小：生成一份可打印的“整数乘法分配律”PDF 练习卷。但系统设计不能被 PDF 输出或单一数学专题锁住；未来应能演进为网页应用，支持更多科目、更多题型，以及由其他开发者提供的新题型插件。

## 已确定方向

### 产品方向

- 第一阶段从可打印 PDF 练习卷开始，不先开发网页界面。
- 将题目生成与输出渲染分离；同一组生成的题目以后可以用于 PDF、网页练习、答案页或学习记录。
- 从一开始按题型插件或类插件模块的边界设计系统。
- 暂不实现复杂的第三方插件安装机制；先通过我们自己新增题型的过程验证插件接口是否稳定。

### 语言与多语言支持

- 生成的 PDF 默认使用英文，因为孩子目前不认识中文。
- 应用架构需要为未来多语言支持留出空间。
- 标题、区域说明、学生信息栏标签等用户可见文本，不能硬编码在数学题目生成器中。
- 未来可使用 `en-CA`、`en-US`、`zh-CN` 等 locale；初始默认值为 `en-CA`。

### 第一版范围

- 专题：整数乘法中的分配律。
- 输出：只生成可打印 PDF 练习卷。
- 第一版暂不生成答案页。
- 默认纸张：A4。
- 默认方向：纵向。
- 默认结构：热身区加专项训练区。
- 默认展示顺序：拆分左侧数字，例如 `49 x 7 = (50 - 1) x 7`。

## 第一版练习卷

默认练习卷是一页 A4 纵向页面，页面上的文字使用英文。

建议版面内容：

```text
Distributive Property Multiplication Practice

Name: ____________________   Date: ______________   Time: ______________

A. Warm-up: Follow the given decomposition and complete each step.
4 questions, one question per line, with guided calculation blanks.

B. Practice: Use a convenient decomposition to calculate.
30 questions, two columns, with expression and answer space only.
```

页面应优先保证孩子书写舒适，而不是尽可能塞入最多题目。热身题需要填写步骤，因此应保留较充分的行间空间。

## 第一个题型：整数乘法分配律

第一个题型生成能够通过分配律拆分其中一个数字的乘法题。

### 初始支持的策略

1. 按数位进行加法拆分。

```text
34 x 6 = (30 + 4) x 6
```

2. 按接近整十或整百的数进行减法拆分。

```text
49 x 7 = (50 - 1) x 7
99 x 8 = (100 - 1) x 8
```

### 建议的初始生成选项

| 设置 | 默认值 | 说明 |
| --- | --- | --- |
| 左侧数字位数 | `2` | 可为以后支持 `3` 位数预留空间。 |
| 右侧数字位数 | `1` | 让首份练习卷聚焦于当前教学目标。 |
| 被拆分的一侧 | `left` | 孩子看到的展示形式稳定。 |
| 允许加法拆分 | `true` | 分配律基础理解所需。 |
| 允许减法拆分 | `true` | 覆盖已经讲授的速算方法。 |
| 距离整十/整百的范围 | `1..2` | 例如 `48`、`49`、`98`、`99`。 |
| 是否避免重复题 | `true` | 在同一份练习卷内生效。 |

当减法拆分策略启用时，按数位加法拆分题默认避开被 `near_round_distances` 覆盖的数字。例如当前设置下，`49 x 7` 应留给 `(50 - 1) x 7` 的速算训练，而不作为 `(40 + 9) x 7` 的普通加法拆分题出现，以免同一份练习卷传递冲突的策略提示。

### 建议默认配比

- 热身区：4 道有引导步骤的题，同时包含加法拆分和减法拆分。
- 专项训练区：当前 preset 为 30 道无步骤提示的题，双列排版。
- 各区域通过 `strategy_weights` 配置策略配比；当前专项区为 `60%` 按数位加法拆分、`40%` 接近整十/整百减法拆分，即 18 道与 12 道。

这个比例暂时只是提案。打印出第一批练习卷并观察孩子实际使用情况后，我们再调整会更可靠。

## 配置边界

配置应分为四类：练习卷模板（preset）、输出渲染器设置、区域选择、以及各题型插件自行拥有的数学规则设置。

### 练习卷模板而非全局配置

本地版本中的 TOML 文件是一份用户可选择或修改的练习卷模板，不是系统全局配置，也不是某个插件自身的配置。因此文件放在 `presets/` 下，例如：

```text
presets/distributive_property_beginner.toml
```

它负责组合标题、语言、输出形式和各区域要使用的题型。插件目录以后可以提供自己的默认值与格式定义，但不应持有用户某一次生成练习卷的选择。

### 通用练习卷设置与输出设置

输出设置由所选渲染器解释，例如纸张大小属于 PDF 输出，而不属于生成后的数学题目数据：

```toml
version = 1

[worksheet]
title = "Distributive Property Multiplication Practice"
locale = "en-CA"
student_fields = ["name", "date", "time"]

[output]
renderer = "pdf"
theme = "classic_a4"

[output.options]
paper_size = "A4"
orientation = "portrait"
```

### 区域选择与插件自己的设置

每个区域独立指定题型插件、题数、书写格式和插件参数。因此未来一份练习卷可以组合不同题型：

```toml
[[sections]]
name = "warmup"
plugin = "integer_multiplication_distributive"
count = 4
columns = 1
format = "guided_full_expansion"

[sections.settings]
left_operand_digits = [2]
right_operand_digits = [1]
decomposable_operand = "left"
strategies = ["place_value_addition", "near_round_number_subtraction"]
allow_duplicates = false
near_round_distances = [1, 2]

[sections.settings.strategy_weights]
place_value_addition = 0.5
near_round_number_subtraction = 0.5

[[sections]]
name = "practice"
plugin = "integer_multiplication_distributive"
count = 30
columns = 2
format = "expression_with_answer_blank"

[sections.settings]
left_operand_digits = [2]
right_operand_digits = [1]
decomposable_operand = "left"
strategies = ["place_value_addition", "near_round_number_subtraction"]
allow_duplicates = false
near_round_distances = [1, 2]

[sections.settings.strategy_weights]
place_value_addition = 0.6
near_round_number_subtraction = 0.4
```

未来其他题型示例：

```toml
[[sections]]
name = "division_practice"
plugin = "integer_division"

[sections.settings]
dividend_digits = [2, 3]
divisor_digits = [1]
allow_remainder = false
```

```toml
[[sections]]
name = "fraction_practice"
plugin = "fraction_add_subtract"

[sections.settings]
denominator_relation = "different"
require_simplification = true
allow_improper_result = false
```

这样，“是否允许余数”一类选项不会进入 PDF 渲染器的通用配置，新题型也能加入自己的合理参数。

## 题目书写格式模板

一个很重要的未来能力，是允许练习卷或题型控制一道题写在纸面上的格式。例如，一道热身题可以要求孩子填写每一个数学步骤：

```text
49 x 8 = (_ - _) x _ = _ x _ - _ x _ = _
```

更进一步，格式模板可以引用生成出的数字或推导值：

```text
{a} x {b} = ({a-n} + {n}) x {b} = _ x {b} + _ x _ = _
```

这里：

- `{a}` 和 `{b}` 表示生成的两个运算数字。
- `{n}` 表示选定的拆分部分。
- `{a-n}` 表示一个推导值。
- `_` 表示需要孩子填写的空位。

对于 `49 x 8` 这种接近整十的减法拆分题，未来更合适的变量表达形式会类似于：

```text
{a} x {b} = ({round} - {difference}) x {b} = _ x _ - _ x _ = _
```

### 设计要求

题目数据不应被限制为一个简单字符串 `prompt`。它最终需要能够携带展示格式或结构化显示组件，从而让 PDF 或网页渲染器显示已给出的数字、填空位、解题步骤，以及未来网页中的交互输入框。

### 第一版暂不做通用模板解析器

我们应在结构上记住这个能力，但第一版不急于实现任意公式模板语言，因为它会立即引入若干需要认真设计的问题：

- 模板变量中允许哪些安全、合法的表达式？
- 插件如何说明一个空位应该填写数字、运算符，还是整个表达式？
- 同一模板在 PDF 和网页交互界面中如何一致呈现？
- 翻译后的文字说明如何与不受语言影响的数学表达式分离？

第一版可以让分配律插件提供少数几个固定的、带名称的书写格式；同时让输出数据形状以后能被可配置模板替换。

建议的第一版格式配置：

```yaml
formats:
  warmup: "guided_full_expansion"
  practice: "expression_with_answer_blank"
```

未来可能的格式配置：

```yaml
formats:
  warmup:
    template: "{a} x {b} = ({round} - {difference}) x {b} = _ x _ - _ x _ = _"
  practice:
    template: "{a} x {b} = __________"
```

## 插件方向

一个题型插件最终应定义：

1. 插件标识符和经过翻译的显示名称。
2. 插件自身的配置 schema 及默认值。
3. 题目生成规则。
4. 支持的书写格式或模板变量。
5. 可由 PDF 与未来网页渲染器共同消费的统一题目数据。

PDF 渲染器不应理解分配律、余数、分数或小数精度等数学规则；它只负责渲染插件提供的结构化题目内容。

## 网页应用中的配置保存

本地命令行阶段使用 TOML，是因为它容易阅读、编辑和纳入版本管理。未来网页应用不以 TOML 文件作为主要持久化格式，而应保存可序列化的数据模型，API 与数据库层可使用 JSON。

网页端至少需要区分三类记录：

1. 插件定义：由插件包提供，包括插件标识、版本、配置 schema、默认值和支持的书写格式。
2. 练习卷模板：用户保存的组合偏好，例如“分配律基础训练 A4”，对应当前 `presets/` 中的内容。
3. 已生成练习卷实例：保存模板快照、插件版本、随机种子和实际题目数据，以便以后重新打印完全相同的练习卷。

TOML 将来仍可作为练习卷模板的导入/导出格式；核心数据模型应保持与存储格式无关。

## 后续题型想法

目前已经识别出的未来扩展方向包括：

- 使用结合律分组的乘法。
- 乘以 `11` 的速算。已确定为第二个题型插件，计划提供 `multiply_by_11_beginner.toml` preset。
- 十位相同且个位之和为 `10` 的两位数乘法。
- 分数比较大小。
- 分数加、减、乘、除。
- 小数四则运算。
- 正负数四则运算。

## 第二个题型：乘以 11

下一个题型插件确定为 `multiply_by_11`。它既适合独立练习，也能与已有的乘法分配律建立联系：

```text
34 x 11 = 34 x (10 + 1)
```

计划随后提供 `presets/multiply_by_11_beginner.toml`。对于专项训练区，今后新 preset 默认使用 `count = 30`；热身区仍保持较少题量，用于解释方法和填写步骤。

### 需要支持的策略

```text
No carrying:    23 x 11 = 253
With carrying:  68 x 11 = 748
```

题型配置可包含不进位与进位两类策略，并使用 `strategy_weights` 控制专项训练的题量比例。

### 带进位热身题的教学设计

只写 `68 x 11 = 6 _ 8` 不足以清楚表达进位过程。已确定热身区先用简短英文规则说明方法，再提供结构化步骤练习。英文提示为：

```text
Add the two digits. Put the ones digit in the middle and carry the tens digit to the left.
```

进位示例/填空形式：

```text
68 x 11: 6 + 8 = 14, so 6 + 1 | 4 | 8 = 748
57 x 11: 5 + 7 = __, so (__ + __) | __ | 7 = ______
```

`multiply_by_11_beginner` 默认安排为：热身区 4 题（不进位与带进位各 2 题），专项训练区 30 题，通过 `strategy_weights` 均衡配置两类题。区域的英文教学文字应作为结构化练习卷内容交给 PDF renderer，而不是由 renderer 硬编码某个数学题型的说明。

## 后续需要继续讨论的问题

- 第一版是否立即包含 `103 x 7` 一类三位数左侧数字，还是严格从两位数开始？
- 减法拆分第一版是否只生成略小于整十/整百的数字；而 `52 x 6 = (50 + 2) x 6` 仍归入普通加法策略？
- 第一版实际需要哪些固定的题目书写格式，才能避免过早实现通用模板？
- 是否保存每份练习卷的随机种子或实际题目数据，以便以后重新生成相同练习卷？
- 产品规则确定后，应选择哪一种 PDF 生成技术？

## 当前建议的下一步

先确定第一版固定使用的题目书写格式和数字生成规则，再围绕确认后的规则搭建最小生成器与 A4 英文 PDF 渲染器。从第一次实现起，数据模型就应携带 locale、题型插件设置和命名格式选择，即使初期只真正实现一个语言和少量固定格式。

## 开发约定

具体开发工作采用测试驱动方式进行：先用测试描述期望的配置行为、题目生成规则和 PDF 输出契约，再编写实现直到测试通过。详细约定记录在 `docs/development-conventions.md`。
