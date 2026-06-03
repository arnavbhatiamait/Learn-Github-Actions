**Deployment Using kubectl — Reusable Workflow**

This document describes a one-stop reusable GitHub Actions workflow that deploys a Kubernetes manifest using `kubectl` and `yq`. It includes the reusable workflow YAML, a caller workflow example, prerequisites, step-by-step instructions, and estimated timings for a demo session.

**Overview**: Reusable workflow that accepts `NAMESPACE` and `IMAGE_NAME` as inputs and uses the `KUBECONFIG` secret to authenticate to the cluster. Designed to run on a self-hosted runner with `kubectl` and `yq` available (the workflow installs them if needed).

**Files**: - Manifest files live in `manifest/` (e.g., `manifest/deployment.yaml`).

**Reusable Workflow (kubernetes_kubectl.yml)**

```yaml
name: Deployment using kubectl

on:
  workflow_call:
    inputs:
      NAMESPACE:
        description: 'Kubernetes Namespace to deploy the application'
        required: true
        type: string
      IMAGE_NAME:
        description: 'Docker Image Name to deploy'
        required: true
        type: string
    secrets:
      KUBECONFIG:
        description: 'Kubeconfig file content for accessing the Kubernetes cluster'
        required: true

jobs:
  deploy:
    env:
      NAMESPACE: ${{ inputs.NAMESPACE }}
    runs-on: self-hosted
    needs: ci-pipeline-jon
    steps:
      - name: Checkout the code
        uses: actions/checkout@v3

      - name: Install kubectl
        run: |
          curl -LO "https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl"
          chmod +x ./kubectl
          sudo mv ./kubectl /usr/local/bin/kubectl
          kubectl version --client

      - name: Configure kubeconfig
        run: |
          mkdir -p ~/.kube
          echo "${{ secrets.KUBECONFIG }}" > ~/.kube/config
          chmod 600 ~/.kube/config
          kubectl version --client
          kubectl get nodes || true

      - name: Install yq
        run: |
          sudo curl -sL "https://github.com/mikefarah/yq/releases/download/v4.25.1/yq_linux_amd64" -o /usr/local/bin/yq
          sudo chmod +x /usr/local/bin/yq
          yq --version

      - name: Update image in deployment.yaml
        run: |
          IMAGE_TAG="${{ github.run_id }}-${GITHUB_SHA::7}"
          IMAGE="${{ inputs.IMAGE_NAME }}:${IMAGE_TAG}"
          export IMAGE
          yq e -i '.spec.template.spec.containers[0].image = strenv(IMAGE)' manifest/deployment.yaml

      - name: Create namespace if not exists
        run: |
          kubectl get namespace $NAMESPACE || kubectl create namespace $NAMESPACE

      - name: Deploy to Kubernetes Cluster
        run: |
          kubectl apply -f manifest/ -n $NAMESPACE

      - name: Verify the deployment
        run: |
          kubectl rollout status deployment/app1-deployment -n $NAMESPACE
          kubectl get all -n $NAMESPACE
```

**Caller workflow (my-first-workflow.yml)**
This workflow runs CI (reusable `ci-pipeline.yml`) then calls the reusable kubectl workflow to deploy.

```yaml
name: my-first-workflow

# Grant permissions required by the called reusable workflow's jobs
permissions:
  contents: read
  actions: read
  security-events: write
  packages: write

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  ci-pipeline-jon:
    uses: arnavbhatiamait/ReusableWorkflow/.github/workflows/ci-pipeline.yml@main
    with:
      run_codeql: false
      run_sonarqube: false
      run_build: true
      run_ghcr_publish: true
    secrets:
      SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
      DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
      DOCKERHUB_TOKEN: ${{ secrets.DOCKERHUB_TOKEN }}

  deploy-with-kubectl:
    needs: ci-pipeline-jon
    uses: arnavbhatiamait/ReusableWorkflow/.github/workflows/kubernetis_kubectl.yml@main
    with:
      NAMESPACE: ${{ vars.NAMESPACE }}
      IMAGE_NAME: ghcr.io/arnavbhatiamait/myapp
    secrets:
      KUBECONFIG: ${{ secrets.KUBECONFIG }}
    environment: STAGING
```

---

**Step-by-step guide**

- **Prerequisites (Demonstration — 8 min)**
  - A GitHub repo (this repo) with `manifest/` containing `deployment.yaml`.
  - A self-hosted runner (or runner that allows installing `kubectl` and `yq`).
  - Secrets: add `KUBECONFIG` (file contents) and any registry credentials (`DOCKERHUB_*` or `GHCR_TOKEN`) in repo or org secrets.

- **Adding Kubernetes manifests (9 min)**
  - Keep `manifest/deployment.yaml` with placeholders for image, e.g.:

  ```yaml
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: app1-deployment
  spec:
    replicas: 1
    selector:
      matchLabels:
        app: app1
    template:
      metadata:
        labels:
          app: app1
      spec:
        containers:
          - name: app1
            image: ghcr.io/owner/myapp:latest
            ports:
              - containerPort: 80
  ```

- **Add Secret for kubeconfig (6 min)**
  - On GitHub, go to Settings → Secrets (repo or org) and add `KUBECONFIG` with the full kubeconfig file content.

- **Install & Configure kubectl (7 min)**
  - The reusable workflow includes installation steps. Locally you can test with:

  ```bash
  curl -LO "https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl"
  chmod +x ./kubectl && sudo mv ./kubectl /usr/local/bin/kubectl
  kubectl version --client
  ```

- **Install `yq` (included in workflow)**
  - `yq` is used to update the image in `manifest/deployment.yaml`.

- **Update Image Tag in Manifest (9 min)**
  - The workflow computes `IMAGE_TAG` using `github.run_id` and `GITHUB_SHA` and updates the image field with `yq`.
  - Example command used in the workflow:

  ```bash
  IMAGE_TAG="${{ github.run_id }}-${GITHUB_SHA::7}"
  IMAGE="ghcr.io/owner/myapp:${IMAGE_TAG}"
  yq e -i '.spec.template.spec.containers[0].image = strenv(IMAGE)' manifest/deployment.yaml
  ```

- **Apply Manifests (12 min)**
  - Workflow runs `kubectl apply -f manifest/ -n $NAMESPACE` and then `kubectl rollout status` for the deployment.

- **Create reusable workflow for deployment (5 min)**
  - Add the reusable workflow YAML (see `kubernetes_kubectl.yml` section) under `.github/workflows/` in a reusable-workflows repo or the same repo.

- **Configure workflow to use reusable workflow (14 min)**
  - The caller workflow (`my-first-workflow.yml`) demonstrates using `uses:` to call the reusable workflow and passing inputs + secrets.

- **Merge PR & Delete Branch (2 min)**
  - After testing, merge the PR and optionally delete the feature branch to keep the repo tidy.

**Checklist — quick (one-stop) deployment flow**

- [ ] Add `manifest/deployment.yaml` to repo
- [ ] Add `KUBECONFIG` to repo/org secrets
- [ ] Publish container image (CI job) and ensure `IMAGE_NAME` is correct
- [ ] Create reusable workflow file under `.github/workflows/`
- [ ] Create caller workflow that runs CI and calls reusable workflow
- [ ] Push, open PR, merge to `main` to trigger deployment

**Troubleshooting**

- If `kubectl get nodes` fails: verify `KUBECONFIG` contents and permissions.
- If `yq` is not executable: confirm `/usr/local/bin/yq` permissions.
- If deployment rollout stalls: inspect `kubectl describe pod` and `kubectl logs`.

**Next steps / Optional improvements**

- Use a dedicated GitHub Actions runner image with `kubectl` and `yq` preinstalled to speed up runs.
- Add a rollback step or health-check probes to the deployment manifest.
- Use image digests for stronger immutability guarantees.

---

If you want, I can: create the reusable workflow YAML file in `.github/workflows/`, or update the existing `myFirstWorkflow.yml` to call it. Tell me which action to take next.
