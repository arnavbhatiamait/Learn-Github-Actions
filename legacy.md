# Legacy: Installing GitHub Actions Runners in Kubernetes

This document captures a concise, legacy-style quickstart for installing GitHub self-hosted runners in a Kubernetes cluster using Actions Runner Controller (ARC).

## Overview

Use Actions Runner Controller (ARC) to run GitHub Actions self-hosted runners inside Kubernetes. You can deploy ARC via Helm or kubectl and configure it with a GitHub Personal Access Token (PAT).

## Prerequisites

- A Kubernetes cluster and `kubectl` access.
- `helm` (optional, for Helm install).
- A GitHub Personal Access Token (PAT) with `repo`, `admin:repo_hook`, and `workflow` scopes (repository-level) or appropriate org-level scopes.

## Install cert-manager (if not present)

Run:

```
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.8.2/cert-manager.yaml
```

## Deploy and Configure ARC

Choose Helm or kubectl.

### Helm (recommended)

1. Add the ARC Helm repo:

```
helm repo add actions-runner-controller https://actions-runner-controller.github.io/actions-runner-controller
helm repo update
```

1. Install the chart (replace `REPLACE_YOUR_TOKEN_HERE`):

```
helm upgrade --install --namespace actions-runner-system --create-namespace \
  --set=authSecret.create=true \
  --set=authSecret.github_token="REPLACE_YOUR_TOKEN_HERE" \
  --wait actions-runner-controller actions-runner-controller/actions-runner-controller
```

> Note: You may also configure the token via a Kubernetes secret instead of embedding it in Helm values.

### Kubectl (manifest)

1. Deploy ARC directly (adjust version as needed):

```
kubectl apply -f https://github.com/actions/actions-runner-controller/releases/download/v0.22.0/actions-runner-controller.yaml
```

1. Create the controller secret with your PAT:

```
kubectl create secret generic controller-manager \
  -n actions-runner-system \
  --from-literal=github_token=REPLACE_YOUR_TOKEN_HERE
```

Replace `REPLACE_YOUR_TOKEN_HERE` with your PAT.

## Create a RunnerDeployment (example)

Create a file named `runnerdeployment.yaml` with the following contents (update `repository` to your repo):

```
apiVersion: actions.summerwind.dev/v1alpha1
kind: RunnerDeployment
metadata:
  name: example-runnerdeploy
spec:
  replicas: 1
  template:
    spec:
      repository: mumoshu/actions-runner-controller-ci
```

Apply it:

```
kubectl apply -f runnerdeployment.yaml
```

## Verify and Troubleshoot

Check runners and pods:

```
kubectl get runners
kubectl get pods -n actions-runner-system
```

Get controller logs (replace pod name as appropriate):

```
kubectl logs <actions-runner-controller-pod> -n actions-runner-system
```

Example observed output:

```
kubectl get runners
NAME                             REPOSITORY                             STATUS
example-runnerdeploy2475h595fr   mumoshu/actions-runner-controller-ci   Running

kubectl get pods
NAME                           READY   STATUS    RESTARTS   AGE
example-runnerdeploy2475ht2qbr 2/2     Running   0          1m
```

Useful log command from your notes:

```
kubectl logs actions-runner-controller-6b775bb94f-gmj4r -n actions-runner-system
```

## Notes & Tips

- Replace repository names and tokens before applying manifests.
- Prefer creating Kubernetes secrets and referencing them rather than embedding tokens in manifests.
- ARC supports `RunnerDeployment`, `RunnerSet`, and `Runner` CRDs for different scaling patterns.
- See the upstream quickstart for more options: <https://github.com/actions/actions-runner-controller/blob/master/docs/quickstart.md>

---
Generated as a legacy quick-reference for installing ARC in Kubernetes.
