#!/usr/bin/env python3
"""每日自动生成两篇技术博客文章并提交 PR。"""

import anthropic
import os
import re
import subprocess
from datetime import datetime, timezone, timedelta

# 北京时间
CST = timezone(timedelta(hours=8))
TODAY = datetime.now(CST).strftime("%Y-%m-%d")
POSTS_DIR = "_posts"

TOPIC_POOL = [
    ("Docker 容器化实战指南", "Docker, 容器, DevOps"),
    ("Kubernetes 核心概念与实战", "Kubernetes, K8s, 容器编排, DevOps"),
    ("Redis 缓存设计与实践", "Redis, 缓存, 数据库, Java"),
    ("MySQL 索引优化深度解析", "MySQL, 数据库, 性能优化, Java"),
    ("Spring Boot 微服务最佳实践", "Spring Boot, 微服务, Java"),
    ("Prometheus + Grafana 监控体系搭建", "Prometheus, Grafana, 监控, DevOps"),
    ("Terraform 基础设施即代码入门", "Terraform, IaC, DevOps, 云原生"),
    ("ArgoCD GitOps 持续部署实践", "ArgoCD, GitOps, Kubernetes, CD"),
    ("Kafka 消息队列核心原理与实战", "Kafka, 消息队列, 分布式, Java"),
    ("Java 并发编程深度解析", "Java, 并发, 多线程, JUC"),
    ("Nginx 反向代理与负载均衡配置", "Nginx, 负载均衡, 运维, DevOps"),
    ("ElasticSearch 搜索引擎实战", "ElasticSearch, 搜索, 全文检索, Java"),
    ("gRPC 微服务通信实践", "gRPC, 微服务, RPC, 分布式"),
    ("Istio 服务网格入门", "Istio, 服务网格, Kubernetes, 云原生"),
    ("Python 数据分析入门", "Python, 数据分析, Pandas, 机器学习"),
]


def get_existing_titles() -> set[str]:
    """读取已有文章标题，避免重复。"""
    titles = set()
    if not os.path.isdir(POSTS_DIR):
        return titles
    for fname in os.listdir(POSTS_DIR):
        if not fname.endswith(".md"):
            continue
        with open(os.path.join(POSTS_DIR, fname), encoding="utf-8") as f:
            for line in f:
                m = re.match(r'^title:\s*["\']?(.+?)["\']?\s*$', line)
                if m:
                    titles.add(m.group(1).strip())
                    break
    return titles


def pick_topics(n: int = 2) -> list[tuple[str, str]]:
    """从 TOPIC_POOL 中挑选尚未写过的主题。"""
    existing = get_existing_titles()
    candidates = [t for t in TOPIC_POOL if t[0] not in existing]
    if len(candidates) < n:
        candidates = TOPIC_POOL  # 全部写完后循环
    return candidates[:n]


def generate_post(client: anthropic.Anthropic, topic: str, tags: str, date: str) -> str:
    """调用 Claude API 生成一篇完整的 Jekyll 博客文章。"""
    slug = re.sub(r"[^\w一-鿿]+", "-", topic).strip("-").lower()

    system = """你是一位技术博主，专注于 Java 后端、DevOps 和云原生领域。
写作风格：技术准确、语言清晰、中文行文、适量代码示例、有实战价值。
输出要求：直接输出完整的 Jekyll Markdown 文件内容，不要加任何额外说明。"""

    prompt = f"""请写一篇关于「{topic}」的技术博客文章。

要求：
1. 必须包含完整的 Jekyll front matter（layout: post、title、date、description、tag、categories）
   date 使用：{date} 10:00:00 +0800
   tag 使用：[{tags}]
2. front matter 后面紧跟目录：
   * Kramdown table of contents
   {{:toc .toc}}
3. 正文 1500 字以上，使用中文
4. 包含至少 3 个代码示例（用 ```语言 代码块）
5. 包含至少 2 个表格（对比/参数说明等）
6. 章节结构清晰：背景介绍 → 核心概念 → 实战示例 → 总结
7. 结尾有总结段落

直接输出 Markdown 内容，从 --- 开始。"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text, slug


def save_post(content: str, slug: str, date: str) -> str:
    """保存文章到 _posts 目录，返回文件路径。"""
    os.makedirs(POSTS_DIR, exist_ok=True)
    filename = f"{date}-{slug}.md"
    filepath = os.path.join(POSTS_DIR, filename)
    # 若同名文件已存在，加后缀避免覆盖
    if os.path.exists(filepath):
        filepath = os.path.join(POSTS_DIR, f"{date}-{slug}-2.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[✓] 生成文章：{filepath}")
    return filepath


def git_commit_and_pr(filepaths: list[str], date: str) -> None:
    """创建分支、提交文件、推送并用 gh 创建 PR。"""
    branch = f"blog/auto-{date}"
    run = lambda cmd: subprocess.run(cmd, shell=True, check=True)

    run(f"git checkout -b {branch}")
    for fp in filepaths:
        run(f"git add {fp}")
    run(f'git commit -m "自动生成每日博客：{date} ({len(filepaths)} 篇)"')
    run(f"git push -u origin {branch}")

    titles = []
    for fp in filepaths:
        with open(fp, encoding="utf-8") as f:
            for line in f:
                m = re.match(r'^title:\s*["\']?(.+?)["\']?\s*$', line)
                if m:
                    titles.append(m.group(1).strip())
                    break

    body_lines = ["## 今日自动生成文章\n"]
    for t in titles:
        body_lines.append(f"- {t}")
    body_lines.append("\n> 由 GitHub Actions + Claude API 自动生成")
    body = "\n".join(body_lines)

    run(
        f'gh pr create --title "📝 每日博客 {date}：{\" · \".join(titles)}" '
        f'--body "{body}" --base master'
    )
    print(f"[✓] PR 已创建，分支：{branch}")


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("缺少环境变量 ANTHROPIC_API_KEY")

    client = anthropic.Anthropic(api_key=api_key)
    topics = pick_topics(n=2)
    saved = []

    for topic, tags in topics:
        print(f"[~] 正在生成：{topic}")
        content, slug = generate_post(client, topic, tags, TODAY)
        fp = save_post(content, slug, TODAY)
        saved.append(fp)

    git_commit_and_pr(saved, TODAY)


if __name__ == "__main__":
    main()
