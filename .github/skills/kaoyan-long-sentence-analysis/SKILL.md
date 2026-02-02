---
name: kaoyan-long-sentence-analysis
description: 当用户需要“考研英语长难句拆解/句法分析/从句与非谓语判断/指代落地/熟词偏译（常见义→语境义）解释/给出可背诵的中文翻译”时，使用本 Skill。按固定模板输出：先主干后修饰、逐层结构、难点清单、难词语境义与翻译策略、意群对照、直译/意译/背诵版。
---

# Skill Instructions

## 目标
把任意英文长难句拆成“主干 + 修饰”，解释语法结构与逻辑关系，并对较难翻译的词/短语给出语境义与翻译策略，最终输出可背诵的中文。

额外要求：遇到“熟词偏译”（看着眼熟，但在此处不是常见意思）时，必须把 **常见义 → 语境义** 的变化讲清楚，并说明这种变化与常见意思的关系（延伸/引申/隐喻/转类/搭配固化等）。

## 何时使用
当用户提出以下需求时加载并执行：
- “帮我分析这句长难句/拆主干/找从句关系/非谓语逻辑主语”
- “这句话里的 it/which/they 指什么？”
- “这个熟词在这里为什么这样翻？”（熟词偏译）
- “给我直译+意译+背诵版”

## 输入（来自用户）
- 【待分析句子】（必填）
- 【上下文】（可选：前后各 1 句）
- 【关注点】（可选：从句关系/非谓语/指代/翻译通顺/难词/熟词偏译）

## 输出（必须遵循）
严格按模板输出（可复制模板文件）：
- 输出模板： [assets/OUTPUT_TEMPLATE.md](./assets/OUTPUT_TEMPLATE.md)

模板要求概述：
1) 句子原文
2) 一句话结论（先给主干：S+V+O / S+be+C）
3) 结构分层（从外到内）
4) 语法点与难点清单（3–6条）
5) 难词/关键词分析（2–6个；含“常见义→语境义”与触发线索）
6) 意群翻译（对照）
7) 整句翻译（直译/意译/背诵版）
8) 可迁移模板（可选）

## 判别规则（必须遵守）
1. **先主干，后修饰**：不要一上来逐词翻译。
2. 遇到从句先判别：
   - 名词性从句：that/wh- 引导，整体当名词用（主/宾/表/同位）。
   - 定语从句：关系词 + 缺成分，修饰名词；能还原为“名词 + 从句”。
   - 状语从句：because/while/if/although 等，修饰谓语/整句。
3. 非谓语优先问三件事：
   - 逻辑主语是谁？
   - 时间先后（同时/先/后）？
   - 主动还是被动？
4. 指代必须落地：
   - this/that/it/which/they/one/those 分别指谁。
5. 翻译策略：
   - 英文“右重”常需中文“前置/拆句”；
   - 允许合理拆成 2 句，但要说明拆分点。
6. 难词处理（遇到“看得懂但不好翻”的词必须做）：
   - 优先给 **语境义**：该词在本句里究竟强调什么（态度/程度/因果/评价）。
   - 看 **搭配与语域**：抽象名词（lesson/impact/influence）常对应“教训/影响/作用”等套路，但要结合语境选词。
   - 警惕“假朋友/直译坑”：如 solvent ≠ 溶剂；常为“有偿付能力/不破产的”。
   - 必要时用“解释性翻译”：用更短的中文把含义讲清。
7. 熟词偏译（必须做得更细）：
   - 先写 **常见义**（你最熟的那个），再写 **语境义**（本句真实义项）。
   - 给出 **触发线索**：是哪一个搭配/结构让它偏义（如 address + problem；issue + statement；subject to；in terms of）。
   - 说明 **与常见义的关系**：用“语义迁移”解释为什么能这么用（引申、比喻、转类、搭配固化）。
   - 给一个 **同结构替换**：用 1–2 个近义词替换，验证你理解的是语境义。

## 示例（输出风格示范）
**输入：**
【待分析句子】The fact that markets can remain irrational longer than investors can remain solvent is a lesson that is learned repeatedly.

**输出（示范）：**
### 1）句子原文
- S: The fact that markets can remain irrational longer than investors can remain solvent is a lesson that is learned repeatedly.

### 2）一句话结论（先给主干）
- 主干：The fact … is a lesson …（S + be + C）

### 3）结构分层（从外到内，逐层缩进）
- ① 主干：The fact … **is** a lesson …
- ② 修饰A（类型：同位语从句；修饰对象：fact）：that markets can remain irrational …
- ③ 修饰B（类型：比较结构；修饰对象：remain irrational）：longer than investors can remain solvent
- ④ 修饰C（类型：定语从句；修饰对象：lesson）：that is learned repeatedly

### 4）语法点与难点清单（3–6条）
- 同位语从句：that 从句解释 fact 的内容，不是定语从句。
- 比较结构省略：than 后面是完整从句（investors can remain solvent）。
- 被动：is learned 表“被反复吸取”。

### 5）难词/关键词分析（2–6个，遇到难翻译必须有）
- irrational
  - 词性/结构：形容词（ir- 否定前缀 + rational）
  - 常见意思：非理性的
  - 语境义：不按理性/基本面行事的（强调市场波动“不是讲道理的”）
  - 偏译触发线索：markets remain irrational（经济语境，强调行为偏离理性预期）
  - 与常见意思的关系：常见义直接适用，但需要补出“持续/程度”的语用信息
  - 常见搭配/近义替换：irrational behavior / irrational exuberance；unreasonable / not rational
  - 翻译建议：适合译为“长期非理性/持续失去理性”，补出程度感
- solvent
  - 词性/结构：形容词
  - 常见意思：很多人会误联想到“溶剂/溶解”（假朋友）
  - 语境义：有偿付能力的、不会破产的（投资者能否“扛得住”）
  - 偏译触发线索：investors remain solvent（金融语境 + remain + 形容词）
  - 与常见意思的关系：不是熟词偏义，而是“形近误导/跨学科义项”；正确义项来自 finance/accounting 语域
  - 常见搭配/近义替换：remain solvent；financially sound
  - 翻译建议：优先译为“不破产/资金不断裂/保持偿付能力”，避免被“溶剂”义误导
- a lesson that is learned repeatedly
  - 词性/结构：名词短语 + 定语从句
  - 常见意思：lesson＝课程/一节课
  - 语境义：反复被验证、反复让人“吃亏后才明白”的经验教训
  - 偏译触发线索：learn a lesson（固定搭配，不等于“上课/学一节课”）
  - 与常见意思的关系：从“课堂上的教训/训诫”引申为“经验教训”（语义抽象化 + 搭配固化）
  - 常见搭配/近义替换：learn a lesson (the hard way)；a recurring lesson
  - 翻译建议：可整体意译为“这是人们一次次付出代价才学会的教训”

### 6）意群翻译（对照）
- The fact (… ) → 这个事实（……）
- markets can remain irrational → 市场可以长期非理性
- longer than investors can remain solvent → 比投资者保持不破产的时间还要长
- is a lesson that is learned repeatedly → 是一条被反复验证/吸取的教训

### 7）整句翻译
- 直译：市场保持非理性的时间可能比投资者保持不破产的时间更长这一事实，是一条被反复吸取的教训。
- 意译：市场“疯起来”能比你扛得住更久——这条教训人们总要一次次学会。
- 背诵版：市场能不理性很久，而你未必撑得住。

## 参考与扩展
- 使用说明：[references/USAGE.md](./references/USAGE.md)
