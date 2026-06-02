<!--
Documentation: Reusable Workflows in GitHub Actions
Generated: concise but thorough guide based on user's caller and reusable workflows
-->
# Reusable Workflows in GitHub Actions

This document explains how to create, call, and troubleshoot reusable workflows in GitHub Actions using the provided example workflows in this repository.

## Contents

- **Overview**: What a reusable workflow is and when to use it
- **Caller workflow**: `my-first-workflow` (how to grant permissions and call a reusable workflow)
- **Reusable workflow**: `ci-pipeline` (inputs, secrets, jobs, and conditions)
- **Permissions & Troubleshooting**: Fixing common permission errors (e.g. nested job permissions)
- **Inputs & Conditions**: Examples for conditional runs and calling with inputs
- **Best Practices**: Tips for maintainability and security

---

## Overview

Reusable workflows allow you to extract common CI/CD logic into a workflow that other workflows or repositories can call. Use `workflow_call` in a workflow stored in `.github/workflows/` to make it reusable. Callers use the `uses:` syntax under `jobs` to invoke the reusable workflow.

Benefits:

- DRY: Share the same build/test/publish pipeline across repositories
- Centralized maintenance: Fix once in the reusable workflow
- Configurable: Expose inputs and secrets to customize behavior per-caller

---

## Caller workflow: `my-first-workflow`

This workflow demonstrates calling a reusable workflow and granting the required permissions.

File: [.github/workflows/myFirstWorkflow.yml](.github/workflows/myFirstWorkflow.yml)

Key points:

- You must grant repository-level `permissions` that cover what nested jobs request (e.g., `security-events: write` for CodeQL to upload results to the security tab, `packages: write` for pushing container images).
- Use the `uses:` syntax inside `jobs` to call the reusable workflow from the other repo or path.

Example (caller):

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
    branches:
      - main
  pull_request:
    branches:
      - main
jobs:
  ci-pipeline-jon:
    uses: arnavbhatiamait/ReusableWorkflow/.github/workflows/ci-pipeline.yml@main
    with:
      run_codeql: true
      run_sonarqube: true
      run_build: false
    secrets:
      SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
      DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
      DOCKERHUB_TOKEN: ${{ secrets.DOCKERHUB_TOKEN }}
```

Notes:

- The top-level `permissions` block controls what the workflow's `GITHUB_TOKEN` is allowed to do. If the reusable workflow or any nested job requires stronger scopes than the caller grants, you will get an error similar to:

  "The nested job 'codeql' is requesting 'actions: read, security-events: write', but is only allowed 'actions: none, security-events: none'."

  Fix: grant the required scopes in the caller workflow as shown above, or reduce the reusable workflow's requested scopes.

---

## Reusable workflow: `ci-pipeline`

This reusable workflow exposes inputs and secrets and contains multiple jobs guarded by conditionals so callers can choose which jobs to run.

Example (reusable workflow header):

```yaml
name: my-first-workflow
on:
  workflow_call:
    inputs:
      run_unit_tests:
        description: Whether to run the unit tests job
        required: false
        default: true
        type: boolean
      run_build:
        description: Whether to run the build job
        required: false
        default: true
        type: boolean
      run_sonarqube:
        description: Whether to run the sonarqube job
        required: false
        default: true
        type: boolean
      run_codeql:
        description: Whether to run the codeql job
        required: false
        default: true
        type: boolean
      run_dockerhub_publish:
        description: Whether to run the dockerhub publish job
        required: false
        default: true
        type: boolean
      run_ghcr_publish:
        description: Whether to run the github container registry publish job
        required: false
        default: true
        type: boolean

    secrets:
      SONAR_TOKEN:
        required: true
      DOCKERHUB_USERNAME:
        required: true
      DOCKERHUB_TOKEN:
        required: true
```

Jobs included (high-level):

- `unit-tests`: checks out code, sets up Python, installs dependencies, runs `pytest`, uploads reports as artifacts.
- `codeql`: runs CodeQL analysis. Requires `security-events: write` permission to upload results to the Security tab.
- `sonarqube`: downloads artifacts (test/coverage), runs SonarQube scan using `SONAR_TOKEN`.
- `build`: builds a Docker image using `docker/build-push-action` and saves it as an artifact.
- `publish-dockerhub`: downloads image artifact, logs into Docker Hub using caller-provided secrets, and pushes the image (requires `packages: write`).
- `publish-ghcr`: similar to publish-dockerhub but pushes to GitHub Container Registry (GHCR).

Each job uses an `if:` conditional relying on inputs, e.g. `if: ${{ inputs.run_codeql }}`.

Important snippet (CodeQL permissions inside the reusable workflow):

```yaml
codeql:
  if: ${{ inputs.run_codeql }}
  runs-on: ubuntu-latest
  permissions:
    actions: read
    contents: read
    security-events: write
```

If you call this workflow from another repository (or the same repo) make sure the caller grants matching or greater `permissions` for the `GITHUB_TOKEN`.

---

## Permissions & Troubleshooting

Common error:

  .github/workflows/myFirstWorkflow.yml (Line: 11, Col: 3): Error calling workflow '.../ci-pipeline.yml@main'. The nested job 'codeql' is requesting 'actions: read, security-events: write', but is only allowed 'actions: none, security-events: none'.

Why it happens:

- The reusable workflow declares a `permissions` block for some jobs. The effective permissions are the intersection of what the caller grants and what the job requests. If the caller grants less (or none), the nested job request is blocked.

Fixes:

1. Grant the needed scopes in the caller workflow (recommended when you trust the reusable workflow):

```yaml
permissions:
  contents: read
  actions: read
  security-events: write
  packages: write
```

1. Reduce the requested permissions inside the reusable workflow: avoid `security-events: write` unless you must upload CodeQL results.

2. For cross-repo calls, repository-level settings may restrict workflows from using `GITHUB_TOKEN` with elevated permissions. Check the organization or repository settings: "Allow GitHub Actions to create and approve pull requests" and "Allow GitHub Actions to access contents" and the policy for reusable workflows.

3. If a job needs to push to a registry, prefer giving it explicit credentials via secrets (e.g., `DOCKERHUB_TOKEN`) and ensure the caller passes the secret. However, pushing to GHCR often requires `packages: write` permission on the `GITHUB_TOKEN` or a PAT with appropriate scopes.

---

## Inputs & Conditions (Examples)

Caller chooses which jobs to enable by passing boolean inputs.

Example: call the reusable workflow but only run tests and CodeQL, not build or publish:

```yaml
jobs:
  ci-pipeline-jon:
    uses: arnavbhatiamait/ReusableWorkflow/.github/workflows/ci-pipeline.yml@main
    with:
      run_codeql: true
      run_sonarqube: false
      run_build: false
      run_dockerhub_publish: false
    secrets:
      SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
      DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
      DOCKERHUB_TOKEN: ${{ secrets.DOCKERHUB_TOKEN }}
```

Conditional job behavior inside the reusable workflow uses `if:` with the `inputs.*` values.

Example inside reusable workflow:

```yaml
publish-dockerhub:
  if: ${{ success() && inputs.run_dockerhub_publish }}
  needs: build
  permissions:
    contents: read
    packages: write
  steps: ...
```

---

## Calling workflows with extra conditions

You can also combine repository event context with inputs. For example, run publishing only for `push` to `main`:

```yaml
on:
  push:
    branches:
      - main

jobs:
  ci:
    uses: arnavbhatiamait/ReusableWorkflow/.github/workflows/ci-pipeline.yml@main
    with:
      run_build: true
      run_dockerhub_publish: ${{ github.ref == 'refs/heads/main' }}
    secrets: ...
```

Note: the `with:` values are evaluated as strings when passed; prefer using explicit booleans or handle conversion in the reusable workflow.

---

## Best Practices

- Keep inputs focused and minimal; expose only what callers need to configure.
- Prefer passing registry credentials via secrets rather than relying on `GITHUB_TOKEN` for external registries.
- Document required permissions in the README or comments in both the caller and reusable workflows.
- Use `continue-on-error` only where acceptable (e.g., optional quality gate checks).
- Pin actions to a commit SHA for maximum reproducibility where security is a concern; use tag versions for faster updates when acceptable.

---

## Verification & Troubleshooting Checklist

1. Confirm caller workflow includes a `permissions` block covering scopes requested by nested jobs.
2. Verify the caller passes required secrets in `secrets:` when invoking the reusable workflow.
3. For cross-repo calls, ensure repository and org settings allow workflow reuse and the requested permissions.
4. Inspect any workflow run failure logs — permission errors are explicit about requested vs allowed scopes.

---

If you want, I can:

- open the reusable workflow file and suggest permission reductions, or
- create a small example showing how to call the reusable workflow only for PRs, or
- push this doc to a different path or update the repo README to reference it.
