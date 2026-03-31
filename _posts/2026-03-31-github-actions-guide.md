---
layout: post
title: "GitHub Actions 实战指南"
date: 2026-03-31 10:00:00 +0800
description: 从零掌握 GitHub Actions 的核心概念与实战配置，覆盖 CI 构建、自动化测试、Docker 发布到生产部署的完整流水线。
tag: [GitHub Actions, CI/CD, DevOps, Docker, 现代开发者工具箱]
categories: [DevOps]
series: 现代开发者工具箱
series_index: 3
---

> **「现代开发者工具箱」系列** — 第 3 篇 / 共 3 篇
> [① Claude 入门](/blog/2026/03/29/claude-getting-started/) · [② Harness CI/CD](/blog/2026/03/29/harness-cicd-guide/) · [③ GitHub Actions 实战](/blog/2026/03/31/github-actions-guide/)

* Kramdown table of contents
{:toc .toc}


# 什么是 GitHub Actions

GitHub Actions 是 GitHub 官方推出的 CI/CD 与自动化平台，于 2019 年正式发布。它直接内嵌在 GitHub 仓库中，无需额外部署任何服务，代码推送即可触发流水线。

<img src="{{ site.baseurl }}/assets/images/github-actions/overview.png" alt="GitHub Actions 工作流概览" style="width: 90%; margin: 20px auto; display: block; border-radius: 8px;">

与其他 CI/CD 工具相比，GitHub Actions 的核心优势在于：

- **零运维成本**：托管在 GitHub，无需维护 Jenkins Master/Slave
- **免费额度充裕**：公开仓库完全免费，私有仓库每月 2000 分钟免费时长
- **生态丰富**：GitHub Marketplace 有超过 2 万个现成 Action 可直接复用
- **原生集成**：与 PR、Issues、Releases、Packages 深度集成，工作流触发方式极为灵活

## GitHub Actions 与 Harness 的定位差异

| 维度 | GitHub Actions | Harness |
|------|----------------|---------|
| 适用规模 | 个人 / 小中型团队 | 中大型企业 |
| 部署策略 | 基础滚动更新 | 蓝绿、金丝雀、自动回滚 |
| 运维成本 | 极低（GitHub 托管）| 低（SaaS）|
| 学习曲线 | 低 | 中 |
| 价格 | 免费起 | 按量计费 |
| 合规审计 | 基础 | 完整 |

简单说：**个人项目和大多数团队首选 GitHub Actions**；有复杂多环境部署需求、强合规要求的企业团队选 Harness。


# 核心概念

在写第一个 Workflow 之前，先理解这几个关键词：

```
Repository
└── .github/workflows/
    └── ci.yml              ← Workflow（工作流）
        ├── on: [push]      ← 触发条件（Event）
        └── jobs:
            └── build:      ← Job（任务）
                └── steps:
                    ├── uses: actions/checkout@v4   ← Action（复用动作）
                    └── run: mvn test               ← Run（Shell 命令）
```

## Workflow（工作流）

Workflow 是一个完整的自动化流程，定义在 `.github/workflows/*.yml` 文件中。一个仓库可以有多个 Workflow（如 `ci.yml`、`release.yml`、`deploy.yml`）。

## Event（触发事件）

Workflow 由事件触发，常用触发方式：

```yaml
on:
  push:                         # 推送代码时
    branches: [main, develop]
  pull_request:                 # PR 创建/更新时
    branches: [main]
  schedule:                     # 定时任务（cron）
    - cron: '0 2 * * 1'        # 每周一凌晨 2 点
  workflow_dispatch:            # 手动触发（UI 上点按钮）
  release:
    types: [published]          # 发布 Release 时
```

## Job（任务）

Job 是 Workflow 的执行单元，**默认并行运行**，可以通过 `needs` 定义依赖关系变为串行。每个 Job 运行在独立的虚拟机中。

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    # ...

  build:
    runs-on: ubuntu-latest
    needs: test          # test 通过后才运行
    # ...

  deploy:
    runs-on: ubuntu-latest
    needs: [test, build] # test 和 build 都通过后才运行
```

## Runner（运行器）

Runner 是执行 Job 的虚拟机，GitHub 提供以下托管 Runner：

| Runner | 规格 | 适用场景 |
|--------|------|---------|
| `ubuntu-latest` | 2 核 7GB | 推荐，最常用 |
| `windows-latest` | 2 核 7GB | Windows 构建 |
| `macos-latest` | 3 核 14GB | iOS/macOS 构建 |

也可以注册**自托管 Runner**（Self-hosted Runner），运行在自己的服务器上，适合需要访问内网资源或特殊硬件的场景。

## Action（复用动作）

Action 是可复用的步骤单元，来自：
- **官方**：`actions/checkout`、`actions/setup-java`、`actions/upload-artifact`
- **社区**：GitHub Marketplace 上的第三方 Action
- **本地**：仓库内 `.github/actions/` 目录下自定义


# 实战一：Java Spring Boot CI 流水线

这是最常见的使用场景——代码推送后自动构建并运行测试。

<img src="{{ site.baseurl }}/assets/images/github-actions/ci-pipeline.png" alt="GitHub Actions CI 流水线执行界面" style="width: 90%; margin: 20px auto; display: block; border-radius: 8px;">

## 基础 CI 配置

创建 `.github/workflows/ci.yml`：

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    name: Build & Test
    runs-on: ubuntu-latest

    steps:
      # 1. 拉取代码
      - name: Checkout code
        uses: actions/checkout@v4

      # 2. 配置 JDK
      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: maven          # 自动缓存 Maven 依赖

      # 3. 构建并运行测试
      - name: Build with Maven
        run: mvn clean verify

      # 4. 上传测试报告
      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()            # 即使测试失败也上传
        with:
          name: test-results
          path: target/surefire-reports/
          retention-days: 7
```

## 多 JDK 版本矩阵测试

GitHub Actions 支持矩阵策略，一次配置多环境并行测试：

```yaml
jobs:
  test:
    strategy:
      matrix:
        java-version: [11, 17, 21]
        os: [ubuntu-latest, windows-latest]

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          java-version: ${{ matrix.java-version }}
          distribution: 'temurin'
          cache: maven

      - run: mvn clean test
```

以上配置会同时触发 **6 个并行 Job**（3 个 JDK 版本 × 2 个操作系统），大幅节省等待时间。


# 实战二：Docker 镜像构建与推送

构建 Docker 镜像并推送到 GitHub Container Registry（GHCR）：

```yaml
name: Docker Build & Push

on:
  push:
    branches: [main]
  release:
    types: [published]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}   # 如 xuanyimo/my-app

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write    # 允许推送到 GHCR

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      # 登录 GHCR
      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}   # 自动注入，无需配置

      # 自动生成镜像标签（branch 名、PR 编号、Git tag、commit SHA）
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=sha,prefix=sha-

      # 开启 BuildKit 缓存加速
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha        # 使用 GitHub Actions 缓存
          cache-to: type=gha,mode=max
```


# 实战三：自动化部署到 Kubernetes

结合 `kubectl` 将应用部署到 K8s 集群：

```yaml
name: Deploy to K8s

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production    # 启用 Environment 保护规则（支持审批）

    steps:
      - uses: actions/checkout@v4

      # 配置 kubectl（从 Secret 读取 kubeconfig）
      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          method: kubeconfig
          kubeconfig: ${{ secrets.KUBECONFIG }}

      # 替换镜像版本并应用
      - name: Deploy to cluster
        run: |
          IMAGE_TAG=sha-${{ github.sha }}
          sed -i "s|IMAGE_TAG|ghcr.io/${{ github.repository }}:${IMAGE_TAG}|g" k8s/deployment.yaml
          kubectl apply -f k8s/
          kubectl rollout status deployment/my-app -n production --timeout=5m

      # 部署失败时自动回滚
      - name: Rollback on failure
        if: failure()
        run: kubectl rollout undo deployment/my-app -n production
```

## Environment 审批保护

对于生产环境部署，可以在 GitHub 仓库 → Settings → Environments 中配置：

- **Required reviewers**：指定审批人，部署前需人工确认
- **Wait timer**：延迟 N 分钟后自动部署
- **Deployment branches**：只允许特定分支触发

配置后，Workflow 运行到 `environment: production` 的 Job 时会自动暂停等待审批。


# 常用技巧

## Secrets 与环境变量管理

敏感信息（API Key、数据库密码）统一存放在 Secrets，避免明文出现在代码中：

```yaml
# 在 Settings → Secrets 中添加 DATABASE_URL
steps:
  - name: Run migration
    env:
      DATABASE_URL: ${{ secrets.DATABASE_URL }}
      APP_ENV: production
    run: ./scripts/migrate.sh
```

Secrets 有三个级别：
- **Repository secrets**：仅当前仓库可用
- **Environment secrets**：绑定特定 Environment（如 production）
- **Organization secrets**：组织内所有仓库共享

## 条件执行

```yaml
steps:
  # 只在 main 分支推送时执行（不在 PR 中执行）
  - name: Deploy
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    run: ./deploy.sh

  # 只在测试失败时发送通知
  - name: Notify on failure
    if: failure()
    uses: slackapi/slack-github-action@v1
    with:
      payload: '{"text":"Build failed on ${{ github.ref }}"}'
    env:
      SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

## 构建缓存

```yaml
# Maven 缓存
- uses: actions/setup-java@v4
  with:
    java-version: '17'
    distribution: 'temurin'
    cache: maven              # 自动缓存 ~/.m2

# Node.js 缓存
- uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: npm                # 自动缓存 node_modules

# 自定义缓存
- uses: actions/cache@v4
  with:
    path: ~/.gradle/caches
    key: gradle-${{ hashFiles('**/*.gradle') }}
    restore-keys: gradle-
```

## 可复用 Workflow

将常用流程抽取为可复用 Workflow，供多仓库调用：

```yaml
# .github/workflows/reusable-java-ci.yml
on:
  workflow_call:
    inputs:
      java-version:
        required: false
        default: '17'
        type: string
    secrets:
      MAVEN_TOKEN:
        required: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: ${{ inputs.java-version }}
          distribution: temurin
          cache: maven
      - run: mvn verify
        env:
          MAVEN_TOKEN: ${{ secrets.MAVEN_TOKEN }}
```

调用方式：

```yaml
# 在另一个 Workflow 或仓库中调用
jobs:
  ci:
    uses: myorg/shared-workflows/.github/workflows/reusable-java-ci.yml@main
    with:
      java-version: '21'
    secrets:
      MAVEN_TOKEN: ${{ secrets.MAVEN_TOKEN }}
```


# 完整示例：从提交到部署的全链路流水线

将上面所有实践整合为一条完整流水线：

```yaml
name: Full Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  # ① 单元测试（所有分支都跑）
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: temurin
          cache: maven
      - run: mvn clean verify
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results
          path: target/surefire-reports/

  # ② 代码质量扫描
  code-quality:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0    # SonarQube 需要完整历史
      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: temurin
          cache: maven
      - name: SonarQube Scan
        run: mvn sonar:sonar
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}

  # ③ 构建并推送镜像（仅 main 分支）
  build-image:
    runs-on: ubuntu-latest
    needs: [test, code-quality]
    if: github.ref == 'refs/heads/main'
    permissions:
      contents: read
      packages: write
    outputs:
      image-tag: ${{ steps.meta.outputs.version }}
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: type=sha,prefix=
      - uses: docker/setup-buildx-action@v3
      - uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # ④ 部署到生产（需要人工审批）
  deploy-prod:
    runs-on: ubuntu-latest
    needs: build-image
    environment: production
    steps:
      - uses: actions/checkout@v4
      - uses: azure/k8s-set-context@v3
        with:
          method: kubeconfig
          kubeconfig: ${{ secrets.KUBECONFIG }}
      - name: Deploy
        run: |
          kubectl set image deployment/my-app \
            app=ghcr.io/${{ github.repository }}:${{ needs.build-image.outputs.image-tag }} \
            -n production
          kubectl rollout status deployment/my-app -n production
      - name: Rollback on failure
        if: failure()
        run: kubectl rollout undo deployment/my-app -n production
```

这条流水线的执行顺序：

```
push to main
    │
    ▼
① test ──────────────┐
                     ▼
② code-quality ──────┤
                     ▼
③ build-image ───────┤
                     ▼
             [等待人工审批]
                     ▼
④ deploy-prod
```


# 费用与配额

| 账户类型 | 免费时长/月 | 存储 |
|----------|------------|------|
| 公开仓库 | 无限制 | 无限制 |
| 个人免费版 | 2,000 分钟 | 500MB |
| Pro | 3,000 分钟 | 1GB |
| Team | 3,000 分钟 | 2GB |
| Enterprise | 50,000 分钟 | 50GB |

Runner 消耗系数：
- Linux：1×（基准）
- Windows：2×
- macOS：10×

> **省钱技巧**：能用 Linux 就别用 macOS；善用缓存减少重复依赖下载；对非关键分支的 PR 可设置 `paths` 过滤，只在相关文件变更时才触发。


# 总结

GitHub Actions 是目前**上手门槛最低、与 GitHub 工作流集成最紧密**的 CI/CD 工具。从一个简单的 `ci.yml` 开始，到多阶段流水线、Docker 发布、K8s 部署，你只需要关注 YAML 配置本身，不需要维护任何额外的服务器。

**推荐学习路径：**

1. 先写一个最简单的 `ci.yml`，让测试在每次 PR 自动跑起来
2. 添加 Docker Build & Push，让镜像自动发布到 GHCR
3. 配置 Environment 和 Secrets，实现有保护的生产部署
4. 抽取可复用 Workflow，在多个仓库间共享流水线逻辑

至此，「现代开发者工具箱」系列已完结：用 **Claude** 提升开发效率，用 **GitHub Actions** 搭建轻量 CI/CD，遇到复杂多云部署场景再引入 **Harness**——三个工具组合，覆盖从个人项目到企业级交付的全部场景。
