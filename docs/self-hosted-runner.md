# Self-hosted GitHub Actions Runner (Linux)

This guide explains how to create, configure, use, and remove a self-hosted GitHub Actions runner on a Linux machine for the repository `arnavbhatiamait/Learn-Github-Actions`.

> IMPORTANT
>
> - Never commit runner tokens. Always copy a fresh token from the GitHub UI when registering a runner.
> - Replace any example tokens below with the token generated in your repository settings.

---

## Overview

A self-hosted runner is a machine you manage that runs GitHub Actions jobs. Use this when you need custom hardware, network access, or specialized software that GitHub-hosted runners don't provide.

This guide covers:

- Registering a runner in the GitHub UI and getting the registration token
- Downloading and installing the runner package on Linux
- Configuring and running the runner
- Running the runner as a service
- Using the runner in workflows (single and multiple labels)
- Removing the runner
- Security and troubleshooting notes

---

## Prerequisites

- A Linux machine (VM or physical) with Internet access
- A user account on that machine (do not run the runner as root)
- Repository admin or maintainer access to `arnavbhatiamait/Learn-Github-Actions` to create a runner
- `curl`, `tar`, and common shell utilities installed

---

## 1) Create the runner in GitHub and obtain the token

1. Go to your repository on GitHub: `https://github.com/arnavbhatiamait/Learn-Github-Actions`
2. Click `Settings` → `Actions` → `Runners`
3. Click **Add runner** (select `Linux` as the OS)
4. Copy the registration commands shown in the UI — you'll get a repository URL and a short-lived token. Use those in the steps below.

---

## 2) Install the runner package (on the Linux machine)

On your Linux machine, open a terminal and run the commands provided by GitHub. Example commands (use the actual version and token from the UI):

```bash
# Create a folder
mkdir actions-runner && cd actions-runner

# Download the runner package (example version used here)
curl -o actions-runner-linux-x64-2.334.0.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.334.0/actions-runner-linux-x64-2.334.0.tar.gz

# Optional: Validate the hash (replace with the hash provided in the UI/docs)
echo "048024cd2c848eb6f14d5646d56c13a4def2ae7ee3ad12122bee960c56f3d271  actions-runner-linux-x64-2.334.0.tar.gz" | shasum -a 256 -c

# Extract the installer
tar xzf ./actions-runner-linux-x64-2.334.0.tar.gz
```

Notes:

- Use the version the GitHub UI suggests if it differs from the example above.
- Validate checksums when possible.

---

## 3) Configure the runner

From the `actions-runner` folder, run the config script with your repository URL and token (replace the token below with the token you copied from the UI):

```bash
./config.sh --url https://github.com/arnavbhatiamait/Learn-Github-Actions --token <YOUR_TOKEN_HERE>
```

During configuration you'll be prompted for:

- Runner name (or press Enter to accept default)
- Runner labels (comma-separated; e.g., `linux,x64,my-label`)
- Whether to run as a service (you can install as a service later)

Save the token only in memory and never commit it to source control.

---

## 4) Start the runner

To run interactively (for testing):

```bash
./run.sh
```

To run as a background service (recommended for persistent runners):

```bash
sudo ./svc.sh install
sudo ./svc.sh start
```

On systems using `systemd` the above script installs a `systemd` service; use `systemctl` to inspect status:

```bash
sudo systemctl status actions.runner.*  # service name may include repo/runner details
sudo journalctl -u actions.runner.* -f
```

---

## 5) Use the self-hosted runner in workflows

Example workflow showing one job on `ubuntu-latest` (GitHub-hosted) and one job on your self-hosted runner:

```yaml
name: self-hosted-runner-demo
on:
  push:
    branches:
      - dev
jobs:
  demo-1:
    name: Demo Job 1
    runs-on: ubuntu-latest
    steps:
      - name: Display the System Information
        run: |
          echo "Hostname: $(hostname)"
          echo "Operating System: "
          lsb_release -a || cat /etc/os-release
          echo "Runner Name : ${{ runner.name }}"
          echo "Runner OS : ${{ runner.os }}"

  demo-2:
    name: Demo Job 2
    runs-on: self-hosted
    steps:
      - name: Display the System Information
        run: |
          echo "Hostname: $(hostname)"
          echo "Operating System: "
          lsb_release -a || cat /etc/os-release
          echo "Runner Name : ${{ runner.name }}"
          echo "Runner OS : ${{ runner.os }}"
```

### Using multiple labels

If you registered your runner with labels (for example `linux` and `x64`), you can target only runners matching all labels using a list:

```yaml
runs-on: [self-hosted, linux, x64]
```

This job will only run on a self-hosted runner that has the `linux` and `x64` labels.

---

## 6) Deleting / removing a self-hosted runner

You can remove the runner from the machine and from GitHub in two ways.

A) From the runner machine (preferred when the machine is available):

```bash
# From the actions-runner folder
./config.sh remove --token <YOUR_TOKEN_HERE>
```

B) From the GitHub UI:

1. Go to `Settings` → `Actions` → `Runners` on the repository.
2. Click the runner and choose **Remove runner**.

Note: Tokens used for removal are short-lived. If the script errors due to token expiry, generate a new token from the UI and re-run the removal.

---

## 7) Security and best practices

- Run the runner under a dedicated non-root user with minimal privileges.
- Limit the runner to a single repository if possible (choose repository-level runner vs organization-level runner).
- Keep the runner OS and the actions runner package up-to-date.
- Use firewall rules to restrict incoming connections to the runner machine.
- Do not store tokens in files or the repo. Tokens are one-time/short-lived tokens provided by the GitHub UI during registration.
- Consider using ephemeral self-hosted runners (provision on demand) for untrusted code.

---

## 8) Troubleshooting

- Runner not picking up jobs: verify labels match and runner is `online` in the GitHub UI.
- Check runner logs in the `actions-runner/_diag` folder or via `journalctl` when installed as a service.
- If `./run.sh` shows errors, re-run `./config.sh` with a fresh token.
- Use `sudo ./svc.sh status` (or `systemctl status`) to check service health.

---

## 9) Quick reference (commands)

```bash
# Download and extract
mkdir actions-runner && cd actions-runner
curl -o actions-runner-linux-x64-2.334.0.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.334.0/actions-runner-linux-x64-2.334.0.tar.gz
tar xzf ./actions-runner-linux-x64-2.334.0.tar.gz

# Configure (replace token)
./config.sh --url https://github.com/arnavbhatiamait/Learn-Github-Actions --token <YOUR_TOKEN>

# Run interactively
./run.sh

# Install and start as a service
sudo ./svc.sh install
sudo ./svc.sh start

# Remove runner
./config.sh remove --token <YOUR_TOKEN>
```

---

## Related files in this repository

See the example workflow: [.github/workflows/self-hosted-runner-demo.yml](.github/workflows/self-hosted-runner-demo.yml)

---

If you want, I can:

- Commit this file to your `dev` branch and open a PR against `main`.
- Add a small `systemd` example unit file for custom setups.
- Walk through installing and configuring a runner on WSL or an Ubuntu VM interactively.
