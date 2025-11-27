# TCP-AW: Test Case Prioritization Automation Workflows

This repository contains an experimental framework for test case prioritization using quantum-inspired particle swarm optimization. 

Automates test case management, prioritization, and fault detection reporting via GitHub Actions and Google Apps Script integration.

## 🚀 Getting Started: Step-by-Step Guide

Follow these instructions to set up the full workflow from forking to automated test case prioritization.

---

### 1. **Use This Template**

- Click the [**Use this template**](https://github.com/new?template_name=TCP-AW&template_owner=megat-z) button at the top-right of this repository page to create a new repository based on this template.
- *(Optional)* Alternatively, click the **Fork** button to create a fork of this repository under your account.
- *(Optional)* You can also `git clone` this repository and push it to a new repository if you prefer manual setup.

---

### 2. **Generate a Personal Access Token (PAT)**

- Go to [GitHub > Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
- Click "Generate new token".
- Select scope: `repo` (at minimum).
- Copy the generated token (you’ll need it in step 5).

---

### 3. **Set Up Google Apps Script with Code.gs**

- Create a new project in [Google Apps Script](https://script.google.com).
- Copy the contents of `Code.gs` from this repository.
- Paste it into your Apps Script editor.

---

### 4. **Configure Script Properties**

- In Apps Script, go to `Project Settings` > `Script Properties`.
- Add the following properties:
  - `GITHUB_PAT`: Paste your Personal Access Token from step 2.
  - `DISPATCH_URL`: Paste the dispatch URL:
    ```
    https://api.github.com/repos/<your-username>/<your-repo-name>/dispatches
    ```
    Replace `<your-username>` and `<your-repo-name>` accordingly.

---

### 5. **Deploy as a Web App**

- In the Apps Script editor, click `Deploy` > `New deployment`.
- Choose "Web app".
- Set access to "Anyone" or "Anyone, even anonymous".
- Deploy.  
- Copy the deployment URL (you’ll need it for the webhook).

---

### 6. **Add a Webhook to Your GitHub Repo**

- Go to your forked repo’s **Settings** > **Webhooks** > **Add webhook**.
- Paste your Web App URL from step 5.
- Set **Content type** to `application/json`.
- Activate the webhook (enable it).
- Save.

---

## 📚 References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Google Apps Script Documentation](https://developers.google.com/apps-script/)
- [RapidFuzz Documentation](https://maxbachmann.github.io/RapidFuzz/)

---

## 👩‍🔬 About the Project

This framework aims to push the boundaries of automated test prioritization in CI/CD environments, leveraging quantum-inspired PSO for optimal APFD. Contributions and research feedback welcome!
