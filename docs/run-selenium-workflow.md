# Run Selenium Tests Workflow

## Purpose
This document describes the reusable GitHub Actions workflow for running Selenium tests on a Kubernetes-deployed application, and how to call it from a top-level workflow.

## Files
- Top-level workflow: `.github/workflows/myFirstWorkflow.yml` (calls reusable workflows)
- Reusable workflow (example location): `ReusableWorkflow/.github/workflows/run_selenium_test.yml`

## High-level flow
1. Build and publish image (CI pipeline)
2. Deploy to Kubernetes using the `kubernetis_kubectl.yml` reusable workflow
3. Run Selenium tests on a self-hosted runner that can access the cluster

## Reusable workflow: inputs & secrets
Example `workflow_call` contract (reusable workflow):

```yaml
on:
  workflow_call:
    inputs:
      ENVIRONMENT:
        description: "Deployment Environment (e.g., staging, production)"
        required: true
        type: string
      NAMESPACE:
        description: "Kubernetes Namespace to deploy the application"
        required: true
        type: string
    secrets:
      KUBECONFIG:
        description: "Kubeconfig file content for accessing the Kubernetes cluster"
        required: true
```

Required environment variables (examples):
- `APP_BASE_URL` (set as a repository `vars` or environment variable) — base URL for Selenium to target.
- `vars.NAMESPACE` — namespace used by deployment workflow.

Required secrets:
- `KUBECONFIG` — cluster access
- (Optional) credentials for images or other services used by tests

## Reusable workflow: job steps (recommended)
- `checkout` — `actions/checkout@v5`
- `setup-python` — `actions/setup-python@v6` (Python 3.10 used in examples)
- Install Chrome (on self-hosted Ubuntu runner) using apt repositories
- Install Python dependencies: `pip install -r requirements-tests.txt` (ensure `pytest` and `pytest-html` are present)
- Ensure `reports/` exists: `mkdir -p reports`
- Run `pytest tests/ --html=reports/selenium-report.html --self-contained-html`
- Upload report via `actions/upload-artifact@v3`

Example job body (inside reusable workflow):

```yaml
jobs:
  run-selenium-tests:
    environment: ${{ inputs.ENVIRONMENT }}
    runs-on: self-hosted
    steps:
      - name: Checkout code
        uses: actions/checkout@v5

      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: "3.10"

      - name: Install Chrome Browser
        run: |
          sudo apt-get update
          sudo apt-get install -y wget gnupg ca-certificates
          wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
          echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
          sudo apt-get update
          sudo apt-get install -y google-chrome-stable

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-tests.txt

      - name: Run Selenium Tests
        env:
          APP_BASE_URL: ${{ vars.APP_BASE_URL }}
        run: |
          mkdir -p reports
          pytest tests/ --html=reports/selenium-report.html --self-contained-html

      - name: Upload Selenium Test Report
        uses: actions/upload-artifact@v3
        with:
          name: selenium-test-report
          path: reports/selenium-report.html
```

## Top-level workflow: calling the reusable workflow
Call the reusable workflow using the `uses:` syntax from a job in the top-level workflow. Example excerpt from `myFirstWorkflow.yml`:

```yaml
jobs:
  run-selenium-tests:
    needs: deploy-with-kubectl
    uses: arnavbhatiamait/ReusableWorkflow/.github/workflows/run_selenium_test.yml@main
    with:
      ENVIRONMENT: STAGING
      NAMESPACE: ${{ vars.NAMESPACE }}
    secrets:
      KUBECONFIG: ${{ secrets.KUBECONFIG }}
```

Note: If you need to run the job directly inside the top-level repo (instead of using the external reusable repo), use a normal `jobs.<name>.runs-on` job with the same steps.

## Runner requirements and recommendations
- Use an Ubuntu self-hosted runner (or runner image that supports `apt`) with `sudo` for package installs.
- Ensure the runner has network access to the Kubernetes cluster (or mount the kubeconfig and use `kubectl port-forward` if tests need pod access).
- Install a matching ChromeDriver version, or prefer Python packages like `webdriver-manager` to auto-manage drivers.
- Run headless Chrome for CI: configure tests to use `--headless=new` or appropriate ChromeOptions to avoid display issues.

## Dependencies
- `pytest`
- `pytest-html` (for `--html=`)
- `selenium` (or `playwright`/other tooling depending on your tests)
- Optionally `webdriver-manager` to install chromedriver automatically:

```bash
pip install webdriver-manager
```

Then in tests:

```python
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver

driver = webdriver.Chrome(ChromeDriverManager().install())
```

## Troubleshooting
- If Chrome install fails on the runner, verify `apt` sources and `sudo` rights.
- If chromedriver mismatch occurs, use `webdriver-manager` or pin Chrome and driver versions.
- If `reports/selenium-report.html` is missing, ensure `mkdir -p reports` runs before pytest.
- Ensure `KUBECONFIG` secret contains a valid kubeconfig and the runner can reach the cluster's API server.

## Example quick checklist before running
- Confirm `vars.APP_BASE_URL` and `vars.NAMESPACE` are set in repository `Settings > Variables`.
- Add `KUBECONFIG` to repository secrets (or pass via environment in reusable workflow caller).
- Confirm self-hosted runner labels match `runs-on` selection.

---
Generated by repository tooling to document the Selenium run workflow and reuse pattern.
