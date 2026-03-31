---
layout: post
title: "Harness CI/CD 平台全面解析"
date: 2026-03-29 14:00:00 +0800
description: 深入讲解 Harness 持续集成与持续交付平台的核心概念、架构设计与实战配置，帮助团队构建现代化 DevOps 流水线。
tag: [Harness, CI/CD, DevOps, Kubernetes, 现代开发者工具箱]
categories: [DevOps]
series: 现代开发者工具箱
series_index: 2
---

> **「现代开发者工具箱」系列** — 第 2 篇 / 共 3 篇
> [① Claude 入门](/blog/2026/03/29/claude-getting-started/) · [② Harness CI/CD](/blog/2026/03/29/harness-cicd-guide/) · [③ GitHub Actions 实战](/blog/2026/03/31/github-actions-guide/)

* Kramdown table of contents
{:toc .toc}

# 什么是 Harness

Harness 是一个企业级的软件交付平台（Software Delivery Platform），覆盖了从代码提交到生产部署的完整软件交付生命周期。它由 Jyoti Bansal（AppDynamics 创始人）于 2017 年创立，目标是让持续交付变得更智能、更安全、更高效。

<img src="{{ site.baseurl }}/assets/images/harness/harness-overview.png" alt="Harness 平台全景" style="width: 90%; margin: 20px auto; display: block;">

与 Jenkins、GitLab CI 等传统 CI/CD 工具相比，Harness 的核心差异在于：

- **AI 驱动**：内置 AI/ML 能力，自动识别部署异常，智能回滚
- **云原生优先**：原生支持 Kubernetes、Helm、Terraform 等现代基础设施工具
- **策略即代码**：通过 OPA（Open Policy Agent）集中管控部署策略和合规要求
- **全平台统一**：CI、CD、Feature Flags、CCM（云成本管理）、STO（安全测试）统一在一个平台

## Harness 的模块组成

```
Harness Platform
├── CI  - 持续集成（构建、测试）
├── CD  - 持续交付（部署到各环境）
├── FF  - Feature Flags（功能开关）
├── CCM - Cloud Cost Management（云成本优化）
├── STO - Security Testing Orchestration（安全测试）
├── SRM - Service Reliability Management（服务可靠性）
└── IDP - Internal Developer Portal（开发者门户）
```

本文重点介绍最核心的 **CI** 和 **CD** 模块。


# 核心概念详解

在深入使用之前，必须先理解 Harness 的核心概念体系：

<img src="{{ site.baseurl }}/assets/images/harness/harness-concepts.png" alt="Harness 核心概念层次结构" style="width: 85%; margin: 20px auto; display: block;">

## Organization 与 Project

Harness 采用三层资源组织结构：

```
Account（账户）
└── Organization（组织）
    └── Project（项目）
        ├── Pipelines（流水线）
        ├── Services（服务）
        ├── Environments（环境）
        └── Connectors（连接器）
```

- **Account**：最顶层，对应一个企业或团队
- **Organization**：业务线或部门级别的隔离，例如「后端团队」「前端团队」
- **Project**：具体项目，权限可以独立控制

## Pipeline（流水线）

Pipeline 是 Harness 的核心执行单元，定义了一个完整的 CI/CD 工作流。每条 Pipeline 由若干 **Stage** 组成。

## Stage（阶段）

Stage 是 Pipeline 的逻辑分组，代表一个独立的执行阶段。Harness 提供多种 Stage 类型：

| Stage 类型 | 用途 |
|------------|------|
| Build | 构建和测试代码（CI 阶段） |
| Deploy | 将服务部署到目标环境 |
| Approval | 等待人工审批 |
| Custom Stage | 自定义脚本逻辑 |
| Security | 集成安全扫描工具 |

## Step（步骤）

Step 是 Stage 内部的最小执行单元，代表一个具体操作，如：运行 Maven 构建、推送 Docker 镜像、执行 kubectl 命令等。

Steps 可以组织成 **Step Group**，方便复用和条件控制。

## Service 与 Environment

- **Service**：代表一个可部署的应用，包含其制品配置（镜像、Chart）和运行时变量
- **Environment**：代表部署目标，如 dev、staging、production，每个环境可以关联不同的基础设施配置（Infrastructure Definition）

## Connector（连接器）

Connector 是 Harness 与外部系统交互的凭证配置，包括：

- **代码仓库**：GitHub、GitLab、Bitbucket
- **制品仓库**：Docker Hub、ECR、Nexus、Harbor
- **云平台**：AWS、GCP、Azure、阿里云
- **Kubernetes 集群**：直连或通过 Delegate 代理

## Delegate

Delegate 是部署在用户基础设施内的代理进程（Java 应用），负责执行 Harness 下发的任务。这种架构的好处是 Harness SaaS 不需要直接访问用户的内网资源，安全性更高。

```
Harness SaaS ──── (HTTPS 长连接) ────> Delegate（运行在用户 K8s 或 VM 中）
                                              │
                                              ├── 访问 K8s API Server
                                              ├── 拉取 Git 仓库
                                              └── 推送/拉取镜像仓库
```


# 持续集成（CI）详解

## CI 流水线的工作原理

<img src="{{ site.baseurl }}/assets/images/harness/harness-ci-flow.png" alt="Harness CI 流程图" style="width: 90%; margin: 20px auto; display: block;">

Harness CI 的每次构建运行在独立的容器中（基于 Kubernetes Pod 或 Docker），保证环境隔离。整体流程：

1. 代码 Push 或 PR 触发 Webhook
2. Harness 拉取代码
3. 在容器中顺序执行各 Step
4. 构建产物（JAR、Docker 镜像）上传到制品仓库
5. 发布构建报告（测试结果、覆盖率、安全扫描）

## CI Pipeline YAML 示例

Harness 支持通过 YAML 定义流水线（Pipeline as Code），以下是一个完整的 Java Spring Boot 项目 CI 配置：

```yaml
pipeline:
  name: springboot-ci
  identifier: springboot_ci
  projectIdentifier: my_project
  orgIdentifier: default

  stages:
    - stage:
        name: Build and Test
        identifier: build_and_test
        type: CI
        spec:
          # 使用 Kubernetes 基础设施运行构建
          infrastructure:
            type: KubernetesDirect
            spec:
              connectorRef: k8s_cluster_connector
              namespace: harness-ci

          execution:
            steps:
              # Step 1: 拉取代码（Harness 自动处理）

              # Step 2: Maven 构建与单元测试
              - step:
                  name: Maven Build
                  identifier: maven_build
                  type: Run
                  spec:
                    connectorRef: dockerhub_connector
                    image: maven:3.9-eclipse-temurin-17
                    command: |
                      mvn clean package -DskipTests=false \
                        -Dmaven.test.failure.ignore=false
                    reports:
                      type: JUnit
                      spec:
                        paths:
                          - "target/surefire-reports/**/*.xml"

              # Step 3: 代码覆盖率上传
              - step:
                  name: Upload Coverage
                  identifier: upload_coverage
                  type: Run
                  spec:
                    image: maven:3.9-eclipse-temurin-17
                    command: |
                      mvn jacoco:report
                      curl -s https://codecov.io/bash | bash

              # Step 4: 构建并推送 Docker 镜像
              - step:
                  name: Build and Push Docker Image
                  identifier: build_push_docker
                  type: BuildAndPushDockerRegistry
                  spec:
                    connectorRef: dockerhub_connector
                    repo: myorg/springboot-app
                    tags:
                      - <+pipeline.sequenceId>
                      - latest
                    dockerfile: Dockerfile
                    buildArgs:
                      JAR_FILE: target/app.jar
```

## 关键特性：Test Intelligence

Harness CI 内置了 **Test Intelligence（测试智能）**功能，通过分析代码变更，只运行受影响的测试用例，大幅减少构建时间：

```yaml
- step:
    name: Run Tests with Intelligence
    type: RunTests
    spec:
      language: Java
      buildTool: Maven
      args: test
      runOnlySelectedTests: true  # 开启智能测试选择
      enableTestSplitting: true   # 并行分片执行
      testAnnotations: "@Test,@ParameterizedTest"
```

在实际项目中，Test Intelligence 通常能将测试执行时间减少 **40%~80%**。

## 缓存加速

构建缓存是提升 CI 速度的关键手段：

```yaml
- step:
    name: Restore Maven Cache
    type: RestoreCacheS3
    spec:
      connectorRef: aws_connector
      region: ap-northeast-1
      bucket: harness-cache
      key: maven-<+hashFiles("pom.xml")>
      archiveFormat: Tar

# ... 构建步骤 ...

- step:
    name: Save Maven Cache
    type: SaveCacheS3
    spec:
      connectorRef: aws_connector
      region: ap-northeast-1
      bucket: harness-cache
      key: maven-<+hashFiles("pom.xml")>
      sourcePaths:
        - ~/.m2/repository
```


# 持续交付（CD）详解

## CD 流水线架构

<img src="{{ site.baseurl }}/assets/images/harness/harness-cd-flow.png" alt="Harness CD 多环境部署流程" style="width: 90%; margin: 20px auto; display: block;">

Harness CD 的核心设计理念是将**部署对象（What）**、**部署目标（Where）**与**部署策略（How）**分离：

- **Service**：定义 What（部署什么镜像、使用什么 Chart）
- **Environment + Infrastructure**：定义 Where（部署到哪个 K8s 集群的哪个 namespace）
- **Execution Steps**：定义 How（滚动更新、蓝绿、金丝雀）

## 部署策略

### 滚动更新（Rolling Update）

最常用的策略，逐步替换旧版本 Pod：

```yaml
- step:
    name: Rolling Deployment
    type: K8sRollingDeploy
    spec:
      skipDryRun: false
      pruningEnabled: true
```

### 蓝绿部署（Blue-Green）

同时维护两套环境，通过切换流量实现零停机发布：

```yaml
- step:
    name: Blue Green Deploy
    type: K8sBlueGreenDeploy
    spec:
      skipDryRun: false

- step:
    name: Swap Traffic to Green
    type: K8sBGSwapServices
    spec:
      skipDryRun: false
```

### 金丝雀发布（Canary）

逐步将流量切换到新版本，通过指标验证后再全量发布：

```yaml
- step:
    name: Canary Deploy 10%
    type: K8sCanaryDeploy
    spec:
      instanceSelection:
        type: Percentage
        spec:
          percentage: 10  # 先将 10% 流量引到新版本

- step:
    name: Verify Metrics
    type: Verify           # 自动分析 APM/日志指标
    timeout: 30m

- step:
    name: Canary Delete / Promote
    type: K8sCanaryDelete
```

## 自动回滚

这是 Harness CD 最有价值的功能之一。通过集成 APM 工具（Datadog、AppDynamics、New Relic 等），Harness 可以在部署后自动分析服务健康状态，当检测到异常时触发自动回滚：

```yaml
- step:
    name: Verify Deployment Health
    type: Verify
    spec:
      isMultiServicesOrEnvs: false
      spec:
        monitoredService:
          type: Default
        type: Canary
        deploymentTag: <+artifact.tag>
      timeout: 30m
      failureStrategies:
        - onFailure:
            errors:
              - Verification
            action:
              type: StageRollback  # 验证失败时自动回滚
```

## Approval Gate（审批门禁）

在关键环境（如生产）部署前，可以插入审批步骤：

```yaml
- step:
    name: Production Approval
    type: HarnessApproval
    spec:
      approvalMessage: |
        本次部署版本：<+artifact.tag>
        变更内容：<+trigger.commitMessage>
        请确认后批准生产部署。
      includePipelineExecutionHistory: true
      approvers:
        userGroups:
          - org._all_org_users
        minimumCount: 2   # 至少 2 人审批
        disallowPipelineExecutor: true  # 不允许自己审批自己的部署
      approverInputs:
        - name: change_ticket
          defaultValue: ""
```


# 变量与表达式系统

Harness 使用 JEXL 表达式语言，通过 `<+...>` 语法引用动态值：

```yaml
# 常用内置变量
<+pipeline.name>              # 流水线名称
<+pipeline.sequenceId>        # 构建序号（自增）
<+pipeline.executionId>       # 本次执行的唯一 ID
<+stage.name>                 # 当前 Stage 名称
<+service.name>               # 服务名称
<+env.name>                   # 环境名称（dev / staging / prod）
<+artifact.tag>               # 制品 tag
<+trigger.commitSha>          # 触发提交的 SHA
<+trigger.sourceBranch>       # 触发的分支名

# 自定义变量（在 Pipeline 中定义）
<+pipeline.variables.DEPLOY_REGION>

# 密钥引用（从 Secrets Manager 读取）
<+secrets.getValue("db_password")>
```


# Harness 与 Jenkins 对比

很多团队在 Harness 和 Jenkins 之间做选型，以下是关键维度的对比：

| 维度 | Harness | Jenkins |
|------|---------|---------|
| 部署模式 | SaaS 或自托管 | 自托管 |
| 配置方式 | 图形化 + YAML | Groovy DSL（Jenkinsfile）|
| 学习曲线 | 中（概念较多）| 中（插件复杂）|
| 运维成本 | 低（SaaS 无需维护） | 高（自行维护 Master/Agent）|
| 原生 K8s 支持 | 强（原生 K8s 部署策略）| 需要插件 |
| CD 能力 | 强（内置蓝绿、金丝雀、验证）| 弱（依赖插件组合）|
| 自动回滚 | 原生支持（AI 驱动）| 需要自己实现 |
| 审计与合规 | 完整的审计日志和策略引擎 | 有限 |
| 成本 | 按使用量计费，有免费版 | 开源免费 |

**推荐选择 Harness 的场景：**
- 团队规模较大，Jenkins 运维成本高
- 需要多云、多环境的标准化部署
- 有合规审计要求（金融、医疗等行业）
- 需要自动化验证和智能回滚能力


# 快速上手：5 步创建第一条流水线

## 第 1 步：注册并创建项目

访问 [app.harness.io](https://app.harness.io) 注册账号（免费版足够入门使用），创建 Organization 和 Project。

## 第 2 步：安装 Delegate

在你的 Kubernetes 集群中安装 Delegate：

```bash
# 从 Harness UI 下载 Helm Chart 安装命令，类似：
helm install harness-delegate harness-delegate/harness-delegate \
  --namespace harness-delegate-ng \
  --create-namespace \
  --set delegateName=my-delegate \
  --set accountId=YOUR_ACCOUNT_ID \
  --set delegateToken=YOUR_TOKEN \
  --set managerEndpoint=https://app.harness.io
```

## 第 3 步：配置 Connectors

在 Project Settings → Connectors 中配置：
- GitHub/GitLab Connector（代码仓库）
- Docker Hub / ECR Connector（镜像仓库）
- Kubernetes Cluster Connector（部署目标）

## 第 4 步：定义 Service 和 Environment

**Service 配置（以 K8s 为例）：**

```yaml
service:
  name: my-spring-app
  identifier: my_spring_app
  serviceDefinition:
    type: Kubernetes
    spec:
      manifests:
        - manifest:
            identifier: k8s_manifests
            type: K8sManifest
            spec:
              store:
                type: Github
                spec:
                  connectorRef: github_connector
                  gitFetchType: Branch
                  branch: main
                  paths:
                    - k8s/
      artifacts:
        primary:
          primaryArtifactRef: primary
          sources:
            - identifier: primary
              spec:
                connectorRef: dockerhub_connector
                imagePath: myorg/springboot-app
                tag: <+input>
              type: DockerRegistry
```

## 第 5 步：创建并运行 Pipeline

通过 UI 拖拽或直接编辑 YAML 创建 Pipeline，点击 **Run** 执行。

<img src="{{ site.baseurl }}/assets/images/harness/harness-pipeline-run.png" alt="Harness Pipeline 执行界面" style="width: 90%; margin: 20px auto; display: block;">

执行过程中，可以实时查看每个 Step 的日志输出，部署完成后查看完整的审计记录。


# 总结

Harness 是一个功能完整、设计现代化的 DevOps 平台，特别适合有一定规模的工程团队：

**核心优势：**
- **统一平台**：CI、CD、安全、成本管理一体化，减少工具链复杂度
- **智能化**：AI 驱动的自动验证和回滚，降低生产事故风险
- **策略即代码**：通过 OPA 统一管控合规和安全策略
- **原生云原生支持**：Kubernetes 部署策略开箱即用

**适合的团队：**
- 使用 Kubernetes 作为主要部署平台
- 需要跨多环境（dev/staging/prod）的标准化交付流程
- 重视部署安全性和可观测性
- 希望减少 CI/CD 工具的自运维成本

对于刚开始探索 Harness 的团队，建议从免费版的 Harness CI 开始，先熟悉 Pipeline、Stage、Step 的核心概念，再逐步扩展到 CD 模块和高级功能。官方文档 [developer.harness.io](https://developer.harness.io) 提供了丰富的教程和示例，是最好的学习资源。
