# Kids Exercise Generator

一个从可打印数学练习卷开始、为未来网页应用与可扩展题型插件预留结构的小项目。

## 当前版本

第一版生成英文 A4 PDF 练习卷，用于整数乘法分配律训练：

- Warm-up：4 道显示拆分步骤的引导题。
- Practice：30 道只显示算式与答题空位的专项题。
- 策略：按数位加法拆分，以及接近整十/整百的减法拆分。

项目也支持英文 A4 的乘以 `11` 入门练习卷：

- Warm-up：显示英文速算规则和完整进位示例，随后完成 4 道步骤题。
- Practice：30 道专项题，默认均衡混合不进位与带进位。

第三份英文 A4 入门练习卷训练“十位相同、个位之和为 10”的两位数乘法：

- Warm-up：解释两段式速算规则，并提示尾部乘积不足两位时补零。
- Practice：30 道专项题，均衡混合 `41 x 49 = 2009` 一类补零题与普通两位尾积题。

## 生成练习卷

```bash
python -m kids_exo generate --preset presets/distributive_property_beginner.toml --output output/distributive-practice.pdf --seed 20260523
```

指定 `--seed` 可以重复生成完全相同的一套题目；不指定则每次随机生成。

生成乘以 `11` 练习卷：

```bash
python -m kids_exo generate --preset presets/multiply_by_11_beginner.toml --output output/multiply-by-11-practice.pdf --seed 20260524
```

生成十位相同、个位和为十的练习卷：

```bash
python -m kids_exo generate --preset presets/same_tens_ones_sum_to_ten_beginner.toml --output output/same-tens-practice.pdf --seed 20260524
```

## 配置结构

- `presets/` 保存一份完整练习卷的组合选择，包括输出方式和各区域使用的题型。
- `kids_exo/plugins/` 保存题型自己的生成规则、格式与专属设置。
- `kids_exo/renderers/` 保存 PDF 等输出方式自己的排版设置与渲染实现。

目前一个 preset 的每个区域都可以独立选择插件，为以后同一份卷子混合多个题型预留了结构。

题型区域还可以通过 `strategy_weights` 调整生成策略的题目比例。例如当前 Practice 区的 `0.6/0.4` 会在 `30` 道题中生成 `18` 道按数位加法拆分题和 `12` 道近整十/整百减法拆分题。

## 运行测试

```bash
python -m unittest discover -s tests -v
```

设计讨论见 [docs/product-design.md](docs/product-design.md)，测试驱动开发约定见 [docs/development-conventions.md](docs/development-conventions.md)。
