# Documentation

## Available Guides

- [Git Workflow Guide](./GIT_WORKFLOW.md) - Complete guide for using feature branches and pull requests
- Branch protection setup (see below)

## Setting Up Branch Protection (GitHub)

To protect the `master` branch from direct commits, configure these settings in your GitHub repository:

1. Go to **Settings** → **Branches**
2. Click **Add rule**
3. Enter `master` as the branch name pattern
4. Enable these protection rules:

### Recommended Settings

#### Pull Request Requirements
- ✅ **Require a pull request before merging**
  - ✅ Require approvals (1-2 reviewers)
  - ✅ Dismiss stale pull request approvals when new commits are pushed
  - ✅ Require review from CODEOWNERS (optional)

#### Status Checks
- ✅ **Require status checks to pass before merging**
  - ✅ Require branches to be up to date before merging
  - Add required status checks:
    - `pre-commit` (if using GitHub Actions)
    - `tests` (if using GitHub Actions)

#### Additional Restrictions
- ✅ **Require conversation resolution before merging**
- ✅ **Require signed commits** (optional, for enhanced security)
- ✅ **Include administrators** (enforce rules for admins too)
- ⚠️ **Do not allow bypassing** (unless absolutely necessary)

#### Force Push Protection
- ✅ **Do not allow force pushes**
- ✅ **Do not allow deletions**

### Setting Up via GitHub CLI

If you have GitHub CLI installed, you can set up branch protection:

```bash
# Install GitHub CLI if needed
# macOS: brew install gh
# Linux: See https://github.com/cli/cli#installation

# Authenticate
gh auth login

# Create branch protection rule
gh api repos/:owner/:repo/branches/master/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["continuous-integration"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}' \
  --field restrictions=null \
  --field allow_force_pushes=false \
  --field allow_deletions=false
```

## Quick Start for New Contributors

1. **Clone the repository**
   ```bash
   git clone https://github.com/evgenii-prusov/jenmoney.git
   cd jenmoney
   ```

2. **Set up the project**
   ```bash
   make setup
   ```

3. **Create a feature branch**
   ```bash
   make branch-new name=my-feature
   ```

4. **Make your changes and test**
   ```bash
   # Make changes...
   make pr-check  # Run all checks
   ```

5. **Commit and push**
   ```bash
   git add .
   git commit -m "feat: Add my new feature"
   git push -u origin feat/my-feature
   ```

6. **Create a pull request**
   - Go to GitHub
   - Click "Compare & pull request"
   - Fill in the PR template
   - Submit for review