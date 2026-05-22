# zh-human-finalizer

`zh-human-finalizer` 是一个面向 AI agent 的中文终稿编辑与语域校准 skill，用于把中文草稿处理成**语域一致、信息保真、节奏自然、适合发布**的最终版本。

它适用于中文改写、润色、翻译、审阅、平台语气改写、作者语域校准和终稿补丁。它的重点不是“伪装成人类”或规避检测，而是在保持事实与立场边界的前提下，提升中文文本的真实读感与交付质量。

> 差异性：它不是简单“去 AI 味”，而是面向中文成稿的终稿编辑 skill，会先识别文本的真实语域、作者意图和平台语气，再在不改立场与事实的前提下，把内容打磨成更像真人作者交付的最终版本。

## What It Does

这个 skill 为 AI agent 提供了一套中文写作终稿流程。它会根据任务类型选择不同的保真等级和语域，并在必要时读取参考资料，例如文本痕迹识别、中文自然表达节奏、平台语气规则、语域模板校准和信息保真边界。

| 能力 | 说明 |
|---|---|
| 中文保真改写 | 在不新增事实、经历、数据和结论的前提下，改善句式、节奏和表达 |
| 终稿自然化 | 降低模板化转折、讲义腔、二分对照壳、万能积极结尾等影响真实读感的问题 |
| 平台语域校准 | 支持公众号、知乎、邮件、聊天、口播、学术克制等不同中文语域 |
| 语域模板校准 | 根据样本提取段落长度、句式复杂度、标点习惯、转折方式和情绪表达，但不复制独特表达或冒充具体身份 |
| 翻译后中文化 | 先保证结构和信息准确，再在段内做自然中文修整 |
| 审阅与评分 | 找出最影响真实读感的 Top 问题，并给出修法 |

## Repository Structure

```text
skills/zh-human-finalizer/
├── SKILL.md
├── references/
│   ├── ai-trace-detector.md
│   ├── fidelity-guardrails.md
│   ├── human-speech-checklist.md
│   ├── registers.md
│   ├── rewrite-playbook.md
│   └── voice-calibration.md
├── scripts/
│   └── zh_style_lint.py
└── templates/
```

## How to Use

把 `skills/zh-human-finalizer/` 目录复制到你的 agent skills 目录中，或直接阅读 `SKILL.md` 并按其中的资源导航加载对应参考文件。

```bash
cp -r skills/zh-human-finalizer /path/to/your/skills/
```

如果你的环境支持 Manus-style skills，保持目录名和 `SKILL.md` 文件结构不变即可。

## Trigger Examples

这个 skill 适合在用户提出以下需求时使用：

```text
帮我把这段中文改得更像真人写的。
润色一下，保留原意，但不要太 AI。
把这篇改成小红书/公众号/知乎语气。
检查这段有没有 AI 味。
翻译成自然中文，不要翻译腔。
```

## Design Principles

`zh-human-finalizer` 默认遵循三条边界。第一，**信息保真优先**，不能为了显得真实而新增事实、身份、经历或来源。第二，**语域一致优先**，不同平台和读者关系使用不同表达距离。第三，**真实读感不等于口水化**，它不会把所有中文都改成碎片化短句，而是根据文本用途调整节奏、转场和判断力度。

## License

This repository is released under the MIT License. See [`LICENSE`](./LICENSE) for details.
