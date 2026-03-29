---
layout: post
title: "Claude 入门使用指南"
date: 2026-03-29 10:00:00 +0800
description: 全面介绍 Anthropic Claude 的核心能力、使用方式与最佳实践，帮助开发者和普通用户快速上手。
tag: [Claude, AI, LLM, Anthropic]
categories: [AI]
---

* Kramdown table of contents
{:toc .toc}

# 什么是 Claude

Claude 是由 [Anthropic](https://www.anthropic.com) 开发的大型语言模型（LLM）助手。与其他 AI 产品不同，Anthropic 从创立之初便将 AI 安全性作为核心研究方向，并将这一理念深度融入 Claude 的训练目标中。Claude 被设计为「有帮助、无害、诚实」（Helpful, Harmless, Honest）的 AI 助手，旨在成为用户可信赖的智能伙伴。

<img src="https://claude.ai/images/claude_app_icon.png" alt="Claude App Icon" style="width: 120px; margin: 20px auto; display: block;">

## Claude 的发展历程

| 版本 | 发布时间 | 特点 |
|------|----------|------|
| Claude 1 | 2023年3月 | 首个公开版本，对话能力强 |
| Claude 2 | 2023年7月 | 100K tokens 上下文，代码能力提升 |
| Claude 3 | 2024年3月 | Haiku / Sonnet / Opus 三档产品线 |
| Claude 3.5 | 2024年6月 | Sonnet 3.5 综合能力超越 GPT-4o |
| Claude 4 | 2025年 | 支持 Extended Thinking，复杂推理大幅提升 |

## Claude 与其他 LLM 的区别

Claude 在以下几个维度表现突出：

1. **超长上下文**：支持最高 200K tokens 的上下文窗口，约 15 万个汉字，可以一次性分析整个代码库或完整书籍。
2. **安全对齐**：采用 Constitutional AI（CAI）技术，通过原则约束模型行为，而非仅靠人工标注。
3. **诚实性**：当 Claude 不确定时会主动声明，不会编造看似合理的错误信息（幻觉率相对较低）。
4. **指令遵循**：对复杂、多步骤的结构化指令有优秀的理解能力。


# Claude 的核心能力

## 写作与文本处理

Claude 擅长各类写作任务，包括：

- **内容创作**：博客文章、营销文案、故事创作、学术论文
- **文本改写**：调整语气、简化表达、翻译
- **摘要提炼**：从大量文本中提取关键信息
- **校对润色**：语法纠错、表达优化

**示例 Prompt：**

```
请将以下技术文档改写为面向非技术用户的说明，语言要通俗易懂，
控制在 300 字以内：

[粘贴原文]
```

## 代码开发

这是 Claude 最受开发者欢迎的功能之一。Claude 支持超过 50 种编程语言，能够：

- 理解并解释现有代码逻辑
- 根据需求生成完整的功能模块
- Debug：分析错误信息并给出修复方案
- Code Review：指出潜在的 Bug 和性能问题
- 编写单元测试

**示例：让 Claude 写一个 Spring Boot 接口**

```
帮我写一个 Spring Boot REST 接口，要求：
1. POST /api/users，接收 JSON body（name, email, age）
2. 校验 email 格式，age 必须在 18-100 之间
3. 返回创建成功的用户对象，包含自动生成的 UUID
4. 使用 @Valid 注解进行参数校验
```

Claude 会给出完整的 Controller、DTO、以及必要的配置代码，并附带说明。

## 数据分析与推理

Claude 可以帮助：

- 分析结构化数据（如 CSV 内容）并给出洞察
- 构建数学模型和统计分析方案
- 逻辑推理和问题分解
- 商业分析、竞品对比、SWOT 分析

## 多模态能力（图像理解）

Claude 3 及以上版本支持图像输入，可以：

- 理解图表、流程图、架构图
- 识别截图中的文字和 UI 元素
- 分析照片内容并回答问题

<img src="https://raw.githubusercontent.com/chihebnabil/claude-ui/main/public/ui.png" alt="Claude 对话界面截图" style="width: 85%; margin: 20px auto; display: block; border: 1px solid #eee; border-radius: 8px;">


# Claude 的使用方式

## 方式一：Claude.ai 网页端

最直接的方式是访问 [claude.ai](https://claude.ai)，注册账号后即可免费使用 Claude（免费版有使用量限制，Pro 版每月 $20 可使用更多配额和更强模型）。

**适合场景：** 日常对话、临时任务、探索 Claude 能力

**使用技巧：**
- 可以在对话中上传文件（PDF、代码文件、图片等）
- 使用「Projects」功能管理不同主题的对话，并为每个项目设置系统提示
- 对话历史会自动保存

## 方式二：API 调用

对于开发者，可以通过 Anthropic API 将 Claude 集成到自己的应用中。

**安装 SDK：**

```bash
# Python
pip install anthropic

# Node.js
npm install @anthropic-ai/sdk
```

**Python 基础调用示例：**

```python
import anthropic

client = anthropic.Anthropic(api_key="your-api-key")

message = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "用 Python 写一个计算斐波那契数列的函数，要求支持记忆化递归"
        }
    ]
)

print(message.content[0].text)
```

**多轮对话示例：**

```python
messages = []

while True:
    user_input = input("You: ")
    messages.append({"role": "user", "content": user_input})

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system="你是一位经验丰富的 Java 后端工程师，请用中文回答问题。",
        messages=messages
    )

    assistant_reply = response.content[0].text
    messages.append({"role": "assistant", "content": assistant_reply})
    print(f"Claude: {assistant_reply}\n")
```

**主要 API 参数说明：**

| 参数 | 说明 | 示例 |
|------|------|------|
| `model` | 模型 ID | `claude-sonnet-4-6` |
| `max_tokens` | 最大输出 token 数 | `4096` |
| `system` | 系统提示词，设定 AI 角色 | `"你是一位..." ` |
| `messages` | 对话历史，支持多轮 | `[{"role": "user", ...}]` |
| `temperature` | 随机性（0~1），0 最确定 | `0.7` |

## 方式三：Claude Code（CLI 工具）

Claude Code 是 Anthropic 官方推出的命令行 AI 编程助手，可以直接在终端中运行，并能访问本地代码文件系统。

```bash
# 安装
npm install -g @anthropic-ai/claude-code

# 在项目目录下启动
cd your-project
claude
```

启动后，Claude Code 可以：

- 读取、修改项目中的文件
- 执行 shell 命令（需用户确认）
- 理解整个代码库的上下文
- 完成完整的开发任务（新增功能、重构、修 Bug）

这是目前 AI 辅助编程体验最接近「真实开发流程」的工具之一。

<img src="https://raw.githubusercontent.com/anthropics/claude-code/main/demo.gif" alt="Claude Code 终端演示" style="width: 85%; margin: 20px auto; display: block; border-radius: 8px;">

## 方式四：第三方集成

Claude 已被集成到众多工具中：

- **IDE 插件**：VS Code、JetBrains 系列（通过 Anthropic 或第三方扩展）
- **Cursor**：基于 Claude 的 AI 代码编辑器
- **Slack / Teams**：企业聊天集成
- **Notion AI**：文档写作辅助
- **Amazon Bedrock**：AWS 上托管的 Claude 服务


# Prompt 工程最佳实践

高质量的输入是获得高质量输出的前提。以下是一些经过验证的 Prompt 技巧：

## 1. 明确角色与目标

```
# 不好的写法
解释一下微服务

# 好的写法
你是一位有 10 年经验的 Java 架构师。请向一位刚转型后端的前端工程师
解释微服务架构，重点说明它解决了什么问题，以及与单体架构相比的优缺点。
使用通俗易懂的类比，控制在 500 字以内。
```

## 2. 结构化输出要求

明确告诉 Claude 你期望的输出格式：

```
分析以下 Java 代码的性能问题，请按照以下格式输出：

## 问题清单
- [严重程度] 问题描述

## 优化建议
针对每个问题给出具体的代码修改建议

## 优先级排序
按照影响程度从高到低排列

代码：
[粘贴代码]
```

## 3. 提供上下文和约束

```
背景：我们的系统是一个电商平台，日订单量约 10 万，使用 MySQL 8.0 + Redis。

问题：商品详情页接口响应时间 > 2s，请帮我分析可能的原因并给出优化方案。

约束：不能修改数据库表结构，需要保持向后兼容。
```

## 4. 迭代与追问

不要期望一次 Prompt 得到完美答案，善用追问：

```
# 第一轮
请给出一个 JWT 认证的实现方案

# 第二轮（追问）
你提到的 Token 刷新机制，具体怎么处理并发刷新的场景？
请给出代码实现。

# 第三轮
这个实现在分布式环境下有什么问题？如何用 Redis 解决？
```

## 5. 使用 XML 标签组织复杂输入

```
请审查以下代码，重点关注安全漏洞：

<code language="java">
[粘贴代码]
</code>

<requirements>
- 关注 SQL 注入、XSS、CSRF 风险
- 检查敏感信息是否有泄漏风险
- 验证输入校验是否完善
</requirements>

<output_format>
按照 OWASP Top 10 分类报告发现的问题
</output_format>
```


# Extended Thinking：深度推理模式

Claude 3.7 Sonnet 及以上版本支持 Extended Thinking（扩展思考）功能。开启后，Claude 会在回答前进行深度内部推理，对复杂数学、逻辑推理、多步骤编程任务有显著提升。

```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000  # 给 Claude 思考的 token 预算
    },
    messages=[{
        "role": "user",
        "content": "请设计一个支持千万级 QPS 的短链接服务，给出完整的架构方案"
    }]
)
```

在返回结果中，可以看到 Claude 的思考过程（`thinking` block），这有助于理解 AI 的推理路径。


# 使用建议与注意事项

## 适合使用 Claude 的场景

- 代码生成、Review、重构
- 文档撰写与技术翻译
- 方案设计与技术选型分析
- 学习新技术（让 Claude 教你）
- 数据处理脚本编写

## 需要注意的限制

1. **知识截止日期**：Claude 的训练数据有时间截止点，对最新事件可能不了解，需要提供上下文。
2. **不要盲目信任代码**：生成的代码需要经过测试，特别是安全敏感的逻辑。
3. **复杂数学计算**：LLM 在精确计算方面仍有局限，关键计算需人工验证。
4. **隐私保护**：避免向 API 发送真实的用户数据、密码、密钥等敏感信息。

## 费用参考（API）

| 模型 | 输入价格（per 1M tokens） | 输出价格（per 1M tokens） |
|------|--------------------------|--------------------------|
| Claude Haiku 4.5 | $0.80 | $4.00 |
| Claude Sonnet 4.6 | $3.00 | $15.00 |
| Claude Opus 4.6 | $15.00 | $75.00 |

对于中低频的开发调试场景，Sonnet 性价比最高；生产环境的批量任务可考虑 Haiku。


# 总结

Claude 是一个功能强大且使用门槛相对较低的 AI 助手。对于开发者来说，从 [claude.ai](https://claude.ai) 注册开始体验，到通过 API 集成到自己的工作流，再到使用 Claude Code 实现 AI 辅助编程，每个阶段都有合适的使用方式。

核心要点：
- **明确需求**，在 Prompt 中提供足够的上下文
- **迭代对话**，不要期望一次得到完美结果
- **验证输出**，特别是代码和重要信息
- **保护隐私**，不向 AI 发送敏感数据

AI 工具的价值在于放大你的能力，而不是替代你的思考。合理使用 Claude，可以显著提升开发效率和内容产出质量。
