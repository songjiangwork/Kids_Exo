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

第四份练习卷训练尾数为 `5` 的两位数平方：

- 该题型复用“十位相同、个位和为 10”的构题核心，是其专项子插件。
- Warm-up：说明先计算十位乘下一数，再在末尾写 `25`。
- Practice：30 道专项题；由于两位数范围内只有 9 道不同题，允许重复以服务熟练度训练。

第五份练习卷将“相同前缀、个位和为 10”的规则扩展到三位数：

- 例如 `123 x 127 = 15621`，先算共同前缀 `12 x 13 = 156`，再接 `3 x 7 = 21`。
- Warm-up：用英文说明共同的前两位规则与补零要求。
- Practice：30 道专项题，均衡覆盖尾积补零与普通两位尾积。

第六份练习卷将乘以 `11` 扩展到三位数，并继续复用 `multiply_by_11` 插件：

- 例如 `326 x 11 = 3586`，保留首尾数字，在中间填写相邻数字之和。
- Warm-up：用英文提示从右向左处理进位，并展示 `386 x 11 = 4246` 的进位示例。
- Practice：30 道专项题，均衡混合不进位与至少一处进位的三位数乘法。

第七份练习卷训练乘以 `9`、`99` 和 `999`：

- 把这些乘数理解为 `10 - 1`、`100 - 1` 与 `1000 - 1`，复用分配律思想。
- Warm-up：显示例如 `36 x 99 = 36 x (100 - 1)` 的英文引导。
- Practice：30 道专项题，三个乘数各 10 道。

第八份练习卷训练乘以 `5`、`25` 和 `125`：

- 分别将题目改写为先除以 `2`、`4`、`8`，再乘以 `10`、`100`、`1000`。
- Beginner preset 仅生成可整除的两位数，先让孩子专注速算规则。
- Practice：30 道专项题，三个乘数各 10 道。

第九份练习卷训练“十位和为 `10`、个位相同”的两位数乘法：

- 例如 `43 x 63 = 2709`，前半部分为 `4 x 6 + 3 = 27`，后半部分为 `3 x 3 = 09`。
- Warm-up：用英文解释前半部分需加共同个位，并强调尾部平方保持两位。
- Practice：30 道专项题，均衡混合尾部平方补零与普通两位尾积。

第十份练习卷训练两个因数同侧接近整十或整百数的乘法：

- 例如 `48 x 47` 以 `50` 为基准，可计算 `50 x (50 - 2 - 3) + 2 x 3`。
- Warm-up：用英文说明共同基准数与两个小偏移量。
- Practice：30 道专项题，均衡包含都低于基准数与都高于基准数的题。

第十一份练习卷训练平方差公式：

- 例如 `47 x 53 = (50 - 3) x (50 + 3) = 50 x 50 - 3 x 3`。
- Warm-up：用英文说明两个因数必须关于基准数等距对称。
- Practice：30 道专项题，聚焦识别对称形式并快速计算。

混合专项练习卷用于孩子已经学过多种方法之后的识别与应用训练：

- 不包含 Warm-up，只保留一个 `Mixed Practice` 区域。
- 从 6 种已学速算方法各抽取 5 道题，合并后随机打乱为 30 道题。
- 训练重点从“按提示使用方法”转为“自行识别最合适的快捷方法”。

100 题混合专项练习卷用于更长时间的集中熟练度训练：

- 同样不包含 Warm-up，从 6 种方法合并并打乱生成 100 道题。
- PDF 会自动分页，续页显示 continuation 标题，并在每页显示页码。
- 当前 A4 纵向默认版面会把这份练习卷排成 3 页。

## 生成练习卷

日常使用推荐直接启动程序进入交互式菜单；程序会显示当前可用练习卷，并在 `output/` 中生成不会覆盖旧文件的 PDF：

```bash
python -m kids_exo
```

显式写为 `python -m kids_exo interactive` 也具有相同行为。

查看所有可选练习卷及其稳定 ID：

```bash
python -m kids_exo list
```

无需手写 TOML 路径，也可以通过稳定 ID 直接生成一份练习卷：

```bash
python -m kids_exo generate --preset-id math.mental_multiplication.difference_of_squares.beginner --seed 20260524
```

开发、调试或自行修改 preset 时，仍可直接指定 TOML 文件与输出路径：

```bash
python -m kids_exo generate --preset presets/distributive_property_beginner.toml --output output/distributive-practice.pdf --seed 20260523
```

自动决定输出文件名时，指定 `--seed` 会生成如 `difference-of-squares-seed-20260524.pdf` 的名称；不指定种子则使用如 `difference-of-squares-20260525-143015.pdf` 的生成时间。若同名文件已存在，程序自动追加 `-2`、`-3`，因此重复运行不会覆盖已有练习卷。显式传入 `--output` 时，程序使用用户指定的精确路径。

指定 `--seed` 可以重复生成完全相同的一套题目；不指定则每次随机生成。

生成乘以 `11` 练习卷：

```bash
python -m kids_exo generate --preset presets/multiply_by_11_beginner.toml --output output/multiply-by-11-practice.pdf --seed 20260524
```

生成十位相同、个位和为十的练习卷：

```bash
python -m kids_exo generate --preset presets/same_tens_ones_sum_to_ten_beginner.toml --output output/same-tens-practice.pdf --seed 20260524
```

生成尾数为 `5` 的平方练习卷：

```bash
python -m kids_exo generate --preset presets/square_ending_in_5_beginner.toml --output output/squares-ending-in-5.pdf --seed 20260524
```

生成三位数相同前缀、个位和为十的练习卷：

```bash
python -m kids_exo generate --preset presets/three_digit_same_prefix_ones_sum_to_ten_beginner.toml --output output/three-digit-same-prefix.pdf --seed 20260524
```

生成三位数乘以 `11` 练习卷：

```bash
python -m kids_exo generate --preset presets/multiply_by_11_three_digit_beginner.toml --output output/multiply-by-11-three-digit.pdf --seed 20260524
```

生成乘以 `9`、`99`、`999` 练习卷：

```bash
python -m kids_exo generate --preset presets/multiply_by_9_99_999_beginner.toml --output output/multiply-by-nines.pdf --seed 20260524
```

生成乘以 `5`、`25`、`125` 练习卷：

```bash
python -m kids_exo generate --preset presets/multiply_by_5_25_125_beginner.toml --output output/multiply-by-five-family.pdf --seed 20260524
```

生成十位和为十、个位相同的练习卷：

```bash
python -m kids_exo generate --preset presets/tens_sum_to_ten_same_ones_beginner.toml --output output/tens-sum-to-ten-same-ones.pdf --seed 20260524
```

生成同侧接近整十/整百数的乘法练习卷：

```bash
python -m kids_exo generate --preset presets/near_round_pair_multiplication_beginner.toml --output output/near-round-pair.pdf --seed 20260524
```

生成平方差公式练习卷：

```bash
python -m kids_exo generate --preset presets/difference_of_squares_beginner.toml --output output/difference-of-squares.pdf --seed 20260524
```

生成不含 warm-up 的混合专项练习卷：

```bash
python -m kids_exo generate --preset-id math.mental_multiplication.mixed_practice --seed 20260524
```

生成分页的 100 题混合专项练习卷：

```bash
python -m kids_exo generate --preset-id math.mental_multiplication.mixed_practice_100 --seed 20260524
```

## 配置结构

- `presets/` 保存一份完整练习卷的组合选择，包括输出方式和各区域使用的题型。
- `kids_exo/catalog.py` 保存面向用户的练习卷目录，包括稳定 ID、科目分类、preset 路径和默认 PDF 文件名。
- `kids_exo/plugins/` 保存题型自己的生成规则、格式与专属设置。
- `kids_exo/renderers/` 保存 PDF 等输出方式自己的排版设置与渲染实现。

交互式入口让用户选择练习卷 preset，而不是直接选择 plugin，因为一份可打印练习卷还需要题量、展示格式、教学文字和输出配置。一个 preset 的不同出题来源可以通过 `combine_into` 合并到同一展示区域，并使用 `shuffle = true` 混排，支持真正的混合专项卷而不是按题型分块排列。PDF 渲染器会依据页面剩余空间对长区域自动分页，因此同一套结构也能承载短卷和 100 题长卷。

题型之间也可以形成扩展关系；例如 `square_ending_in_5` 收窄共同规则，而 `three_digit_same_prefix_ones_sum_to_ten` 将同一套前缀构题逻辑扩展至更长的前缀，只覆盖自己的数字范围和教学展示。对于数学算法完全一致、仅数字范围不同的情况，例如两位数与三位数乘以 `11`，则由同一个插件配合不同 preset 复用规则。表面相似但实际步骤不同的镜像方法，例如“十位相同、个位和为十”与“十位和为十、个位相同”，则各自保留独立插件与清晰教学文案。

题型区域还可以通过 `strategy_weights` 调整生成策略的题目比例。例如当前 Practice 区的 `0.6/0.4` 会在 `30` 道题中生成 `18` 道按数位加法拆分题和 `12` 道近整十/整百减法拆分题。

## 网页后端原型

网页应用已经开始第一条后端切片。当前 FastAPI 服务提供在线题型 catalog、练习预览以及保存后可供孩子答题的 session，用于支撑下一步 Parent/Student 浏览器界面：

- `GET /api/practice-plugins` 返回在线题型、题量/反馈选项及 UI 可配置 schema。
- `POST /api/practice-sessions/preview` 根据配置生成仅供预览的题面快照，并返回 locale fallback 提示；响应不会包含标准答案。
- `POST /api/learners` 创建原型阶段的 learner nickname 档案。
- `POST /api/learners/{id}/sessions` 保存一份练习并返回短期 student token 与安全题面。
- `GET /api/student/sessions/{token}` 与 `POST .../questions/{id}/attempts` 支持孩子打开练习并提交一次正式答案；延迟反馈模式不会在提交时透露正误。

安装可选网页开发依赖并启动 API：

```bash
python -m venv .venv
.venv/bin/python -m pip install -e '.[web,test]'
.venv/bin/python -m alembic upgrade head
.venv/bin/python -m uvicorn kids_exo.web.app:app --reload
```

数据库结构由 `Alembic` 建立和升级，应用启动不会隐式建表；CRUD 通过 `SQLAlchemy 2.0 ORM` repository 完成。原型当前还没有 Parent 认证与结果报告页面，这两项会在可见前端流程之后继续补齐。

## 可视网页原型

Angular Material 前端位于 `web-client/`，现已提供两条可操作界面：

- Parent Studio：填写 learner nickname，配置乘以 `11` 的题量、两位/三位数、进位题选择、反馈和计时器，然后创建练习。
- Student Practice：点击生成的 learner 按钮后，以一题一屏的方式填写答案；即时反馈模式会显示正误，延迟反馈模式只确认答案已保存。

启动后端后，在另一个终端启动前端：

```bash
cd web-client
npm install
npm start
```

打开 `http://localhost:4200/manage` 即可试用 Parent 流程。前端开发服务器已经配置 `/api` proxy，自动转发到 `http://127.0.0.1:8000` 的 FastAPI 服务。

当前可视原型刻意保持小范围：只开放 `Multiply by 11`，暂不包含 Parent 登录、历史报告或 deferred feedback 的结果复盘页面。

## 运行测试

```bash
.venv/bin/python -m unittest discover -s tests -v
cd web-client && npm test -- --watch=false
cd web-client && npm run build
```

设计讨论见 [docs/product-design.md](docs/product-design.md)，网页应用原型规划见 [docs/web-app-design.md](docs/web-app-design.md)，测试驱动开发约定见 [docs/development-conventions.md](docs/development-conventions.md)。
