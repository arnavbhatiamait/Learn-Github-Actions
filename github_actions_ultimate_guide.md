# GitHub Actions Ultimate Master Guide

# Table of Contents

1. Introduction
2. GitHub Actions Architecture
3. Workflow Basics
4. Workflow Syntax
5. Events & Triggers
6. Jobs
7. Steps
8. Actions
9. Runners
10. Variables & Secrets
11. Expressions & Contexts
12. Matrix Builds
13. Caching
14. Artifacts
15. Services & Containers
16. Docker Integration
17. Docker Compose
18. AWS ECS Deployments
19. AWS EC2 Deployments
20. Kubernetes Deployments
21. Helm Deployments
22. Terraform Automation
23. GitOps & ArgoCD
24. Monorepo Workflows
25. Self Hosted Runners
26. Security Best Practices
27. CI/CD Architectures
28. Blue Green Deployment
29. Canary Deployment
30. Rollback Strategies
31. Testing Pipelines
32. AI & Automation Pipelines
33. Monitoring & Observability
34. Debugging
35. Performance Optimization
36. Best Practices
37. Real World Production Pipelines

---

# 1. Introduction

GitHub Actions is GitHub's CI/CD automation platform.

It allows:
- Continuous Integration (CI)
- Continuous Deployment (CD)
- Infrastructure Automation
- Security Automation
- Testing Automation
- DevOps Pipelines

GitHub Actions workflows are defined inside:

```bash
.github/workflows/
```

Example:

```bash
.github/workflows/ci.yml
.github/workflows/deploy.yml
```

---

# 2. GitHub Actions Architecture

Main Components:

- Workflow
- Jobs
- Steps
- Actions
- Runners
- Events

Flow:

```text
GitHub Event -> Workflow -> Job -> Step -> Action
```

---

# 3. Workflow Basics

Example workflow:

```yaml
name: CI Pipeline

on:
  push:
    branches:
      - main

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Print Hello
        run: echo "Hello GitHub Actions"
```

Explanation:

```yaml
name:
```
Workflow name.

```yaml
on:
```
Trigger event.

```yaml
jobs:
```
Defines jobs.

```yaml
runs-on:
```
Runner OS.

```yaml
steps:
```
Tasks executed sequentially.

---

# 4. Workflow Syntax

Complex workflow:

```yaml
name: Production Pipeline

on:
  push:
    branches:
      - main

env:
  NODE_ENV: production

jobs:
  build:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [18, 20]

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}

      - run: npm ci
      - run: npm run build
      - run: npm test
```

---

# 5. Events & Triggers

## Push Event

```yaml
on: push
```

## Pull Request

```yaml
on: pull_request
```

## Scheduled Cron

```yaml
on:
  schedule:
    - cron: "0 0 * * *"
```

## Manual Trigger

```yaml
on: workflow_dispatch
```

## Multiple Events

```yaml
on:
  push:
  pull_request:
  workflow_dispatch:
```

---

# 6. Jobs

Jobs run independently.

```yaml
jobs:
  build:
    runs-on: ubuntu-latest

  test:
    runs-on: ubuntu-latest
```

Dependency:

```yaml
needs: build
```

Example:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Build"

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploy"
```

---

# 7. Steps

Steps run sequentially.

```yaml
steps:
  - run: echo "Step 1"

  - run: echo "Step 2"
```

Named step:

```yaml
- name: Install Dependencies
  run: npm install
```

---

# 8. Actions

## Official Actions

### Checkout

```yaml
- uses: actions/checkout@v4
```

### Setup Node

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: 20
```

### Setup Python

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: "3.12"
```

---

# 9. Runners

## GitHub Hosted

- ubuntu-latest
- windows-latest
- macos-latest

## Self Hosted

```yaml
runs-on: self-hosted
```

---

# 10. Variables & Secrets

## Environment Variables

```yaml
env:
  APP_ENV: production
```

## Secrets

GitHub:
Settings → Secrets → Actions

Usage:

```yaml
env:
  API_KEY: ${{ secrets.API_KEY }}
```

---

# 11. Expressions & Contexts

## GitHub Context

```yaml
${{ github.repository }}
${{ github.actor }}
${{ github.ref }}
```

## Conditions

```yaml
if: github.ref == 'refs/heads/main'
```

---

# 12. Matrix Builds

```yaml
strategy:
  matrix:
    node-version: [18, 20]
```

---

# 13. Caching

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: npm-${{ hashFiles('package-lock.json') }}
```

---

# 14. Artifacts

Upload:

```yaml
- uses: actions/upload-artifact@v4
  with:
    name: build
    path: dist
```

Download:

```yaml
- uses: actions/download-artifact@v4
  with:
    name: build
```

---

# 15. Services & Containers

## PostgreSQL Service

```yaml
services:
  postgres:
    image: postgres:15
    env:
      POSTGRES_PASSWORD: password
```

---

# 16. Docker Integration

## Docker Build

```yaml
- name: Build Docker Image
  run: docker build -t my-app .
```

## Docker Push

```yaml
- name: Push Docker Image
  run: docker push my-app
```

## Docker Login

```yaml
- uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKER_USERNAME }}
    password: ${{ secrets.DOCKER_PASSWORD }}
```

---

# 17. Docker Compose

```yaml
- name: Start Containers
  run: docker compose up -d
```

---

# 18. AWS ECS Deployments

## ECS Deployment Pipeline

```yaml
name: ECS Deploy

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-region: us-east-1
          role-to-assume: arn:aws:iam::123456789:role/github-role

      - uses: aws-actions/amazon-ecr-login@v2

      - name: Build Image
        run: |
          docker build -t my-app .
          docker tag my-app:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/my-app:latest

      - name: Push Image
        run: |
          docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/my-app:latest

      - name: Deploy ECS
        run: |
          aws ecs update-service \
            --cluster my-cluster \
            --service my-service \
            --force-new-deployment
```

---

# 19. AWS EC2 Deployments

## SSH Deployment

```yaml
- name: Setup SSH
  run: |
    mkdir -p ~/.ssh
    echo "${{ secrets.EC2_KEY }}" > ~/.ssh/id_rsa
    chmod 600 ~/.ssh/id_rsa
```

## Deploy

```yaml
- name: Deploy
  run: |
    ssh ubuntu@HOST "
      cd /app
      git pull
      docker compose up -d --build
    "
```

---

# 20. Kubernetes Deployments

## Setup kubectl

```yaml
- uses: azure/setup-kubectl@v4
```

## Deploy

```yaml
- name: Deploy Kubernetes
  run: |
    kubectl apply -f k8s/
```

---

# 21. Helm Deployments

```yaml
- uses: azure/setup-helm@v4
```

Deploy:

```yaml
- name: Helm Deploy
  run: |
    helm upgrade --install myapp ./helm-chart
```

---

# 22. Terraform Automation

## Terraform Init

```yaml
- name: Terraform Init
  run: terraform init
```

## Terraform Plan

```yaml
- name: Terraform Plan
  run: terraform plan
```

## Terraform Apply

```yaml
- name: Terraform Apply
  run: terraform apply -auto-approve
```

---

# 23. GitOps & ArgoCD

## ArgoCD Sync

```yaml
- name: Trigger ArgoCD Sync
  run: |
    argocd app sync my-app
```

GitOps Flow:

```text
Git Push -> GitHub Actions -> Update Manifests -> ArgoCD Detects Changes -> Deploy
```

---

# 24. Monorepo Workflows

Example:

```yaml
on:
  push:
    paths:
      - "frontend/**"
```

Backend:

```yaml
on:
  push:
    paths:
      - "backend/**"
```

---

# 25. Self Hosted Runners

## Install Runner

```bash
./config.sh --url https://github.com/owner/repo --token TOKEN
```

Run:

```bash
./run.sh
```

Workflow:

```yaml
runs-on: self-hosted
```

---

# 26. Security Best Practices

- Never hardcode secrets
- Use OIDC
- Rotate tokens
- Use environment protection
- Use least privilege IAM roles

---

# 27. CI/CD Architectures

## Basic Pipeline

```text
Code -> Build -> Test -> Deploy
```

## Advanced Pipeline

```text
Code
 -> Lint
 -> Unit Tests
 -> Integration Tests
 -> Security Scan
 -> Docker Build
 -> Push Registry
 -> Deploy Staging
 -> E2E Tests
 -> Production Deploy
```

---

# 28. Blue Green Deployment

Blue = Current Production

Green = New Version

Switch traffic after validation.

Benefits:
- Zero downtime
- Instant rollback

---

# 29. Canary Deployment

Deploy to small subset of users first.

Example:
- 10%
- 25%
- 50%
- 100%

---

# 30. Rollback Strategies

## Kubernetes Rollback

```bash
kubectl rollout undo deployment/myapp
```

## ECS Rollback

```bash
aws ecs update-service --force-new-deployment
```

---

# 31. Testing Pipelines

## Unit Testing

```yaml
- run: npm test
```

## Integration Testing

```yaml
- run: npm run test:integration
```

## E2E Testing

```yaml
- run: npm run test:e2e
```

---

# 32. AI & Automation Pipelines

Use GitHub Actions for:

- AI model training
- LLM evaluation
- Data preprocessing
- Auto deployments
- AI validation pipelines

---

# 33. Monitoring & Observability

## Prometheus

```yaml
- name: Deploy Monitoring
  run: kubectl apply -f monitoring/
```

## Grafana

```yaml
- name: Deploy Grafana
  run: helm install grafana grafana/grafana
```

---

# 34. Debugging

## Enable Debug

```yaml
env:
  ACTIONS_STEP_DEBUG: true
```

## Print Variables

```yaml
- run: env
```

---

# 35. Performance Optimization

- Use cache
- Parallel jobs
- Matrix builds
- Reusable workflows
- Composite actions

---

# 36. Best Practices

- Use reusable workflows
- Use semantic versioning
- Pin action versions
- Use environments
- Protect production deployments
- Use approvals

---

# 37. Real World Production Pipeline

```yaml
name: Full Production Pipeline

on:
  push:
    branches:
      - main

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run lint

  test:
    runs-on: ubuntu-latest
    needs: lint

    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm test

  docker:
    runs-on: ubuntu-latest
    needs: test

    steps:
      - uses: actions/checkout@v4

      - uses: docker/setup-buildx-action@v3

      - uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - run: docker build -t myapp .

      - run: docker push myapp

  deploy:
    runs-on: ubuntu-latest
    needs: docker

    steps:
      - uses: actions/checkout@v4

      - uses: azure/setup-kubectl@v4

      - run: kubectl apply -f k8s/
```

---

# Final Notes

Mastering GitHub Actions requires:
- Building projects
- Writing workflows daily
- Understanding CI/CD deeply
- Learning cloud deployments
- Automating infrastructure

Recommended Learning Order:

1. Workflow Basics
2. Jobs & Steps
3. Docker
4. AWS Deployments
5. Kubernetes
6. Terraform
7. GitOps
8. Security
9. Production Pipelines
10. Scaling CI/CD Systems

