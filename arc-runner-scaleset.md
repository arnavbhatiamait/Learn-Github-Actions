# ARC Runner Scale Set: Install & Scale Quickstart

This guide documents installing the Actions Runner Controller (ARC) scale-set charts and configuring Runner Scale Sets using Helm. It collects the commands you supplied and expands them with verification and safety tips so you can reproduce the installation later.

## Before you begin

- Kubernetes cluster with `kubectl` configured.
- `helm` 3+ installed.
- GitHub Personal Access Token (PAT) with appropriate scope for the target (repository or organization). For org-level installations prefer `admin:org`, `repo` and `workflow` scopes; for repo-level the `repo` and `workflow` scopes are typically required.
- (Optional) `cert-manager` installed if you need certificate management for webhook components.

Install cert-manager (if required):

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.8.2/cert-manager.yaml
```

## 1) Install the ARC Scale Set Controller

Use the OCI chart from GitHub Container Registry. Replace `${NAMESPACE}` as needed.

```bash
NAMESPACE="arc-systems"
helm install arc \
  --namespace "${NAMESPACE}" \
  --create-namespace \
  oci://ghcr.io/actions/actions-runner-controller-charts/gha-runner-scale-set-controller
```

Verify the controller is running:

```bash
helm ls -n "${NAMESPACE}"
kubectl get pods -n "${NAMESPACE}"
kubectl logs -n "${NAMESPACE}" deployment/arc-runner-scale-set-controller || true
```

If a pod name is required, list pods and inspect the controller pod's logs:

```bash
kubectl get pods -n "${NAMESPACE}"
kubectl logs <controller-pod-name> -n "${NAMESPACE}"
```

## 2) Install the Runner Scale Set chart (the actual runner provisioner)

This chart configures runner scale sets that attach to your GitHub repository/org/enterprise.

Set the installation name, namespace, and configuration values (replace placeholders):

```bash
INSTALLATION_NAME="arc-runner-set"
NAMESPACE="arc-runners"
GITHUB_CONFIG_URL="https://github.com/<your_enterprise/org/repo>"   # or https://github.com/<owner>/<repo>
GITHUB_PAT="<PAT>"

helm install "${INSTALLATION_NAME}" \
  --namespace "${NAMESPACE}" \
  --create-namespace \
  --set githubConfigUrl="${GITHUB_CONFIG_URL}" \
  --set githubConfigSecret.github_token="${GITHUB_PAT}" \
  oci://ghcr.io/actions/actions-runner-controller-charts/gha-runner-scale-set
```

Notes on values and secrets:

- Passing the PAT directly via `--set` works but exposes the secret in your shell history and in Helm release values. Prefer creating a Kubernetes `Secret` and referencing it in Helm values where the chart supports it.
- Example (safer): create a secret then pass its name (adjust chart value key per chart docs):

```bash
kubectl create secret generic arc-github-config --namespace "${NAMESPACE}" --from-literal=github_token="${GITHUB_PAT}"
# Then follow chart docs to reference this secret instead of --set githubConfigSecret.github_token
```

Consult the chart README for the exact key name to reference a pre-created secret.

## 3) Verify installation and runner creation

Check Helm release and pods:

```bash
helm ls -n "${NAMESPACE}"
kubectl get pods -n "${NAMESPACE}"
```

Check RunnerScaleSet / Runner resources (CRDs) and runners created by the controller:

```bash
# list RunnerScaleSet / Runner CRs in the cluster (CRD names may vary by chart version)
kubectl get runnerscalesets -A || kubectl get runners -A || true

# list runner pods associated with the chart
kubectl get pods -n "${NAMESPACE}" -l app.kubernetes.io/name=gha-runner-scale-set

# view controller logs for errors
kubectl logs -n "${NAMESPACE}" deployment/arc-runner-scale-set-controller
```

On the GitHub side, verify the runner(s) appear under the target repository or organization Settings → Actions → Runners.

## 4) Common operations

- Upgrade chart with new configuration:

```bash
helm upgrade "${INSTALLATION_NAME}" \
  --namespace "${NAMESPACE}" \
  --set githubConfigUrl="${GITHUB_CONFIG_URL}" \
  --set githubConfigSecret.github_token="${GITHUB_PAT}" \
  oci://ghcr.io/actions/actions-runner-controller-charts/gha-runner-scale-set
```

- Uninstall the runner scale set and controller:

```bash
helm uninstall "${INSTALLATION_NAME}" -n "${NAMESPACE}"
helm uninstall arc -n "arc-systems"
kubectl delete namespace "${NAMESPACE}" --ignore-not-found
kubectl delete namespace arc-systems --ignore-not-found
```

## 5) Security & best practices

- Never store PATs in plain text files or commit them. Use Kubernetes Secrets or external secrets managers.
- Limit PAT scope to the minimum required (repo-level vs org-level) and rotate it periodically.
- Use RBAC, network policies, and namespaces to isolate runner workloads.

## 6) Troubleshooting

- If runners do not appear in GitHub: check controller logs, check the secret configuration, and ensure the PAT is valid and has the required scopes.
- If pods crash or fail readiness: `kubectl describe pod <pod>` and `kubectl logs <pod>` will surface container errors.
- If Helm fails to pull OCI charts, ensure Docker/OCI registry access from your environment and that `helm` supports OCI (Helm 3+).

## References

- GitHub Docs: Get started with Actions Runner Controller — <https://docs.github.com/en/actions/tutorials/use-actions-runner-controller/get-started>
- ARC Charts (OCI): ghcr.io/actions/actions-runner-controller-charts

---
Add further steps or your environment-specific values below this file when ready.
