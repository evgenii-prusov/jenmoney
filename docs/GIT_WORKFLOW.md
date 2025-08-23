# Git Workflow Guide

## Overview

This project follows a feature branch workflow with pull requests for all changes. Direct commits to `master` are discouraged.

## Branch Naming Convention

Use descriptive branch names with appropriate prefixes:

- `feat/` - New features (e.g., `feat/user-authentication`)
- `fix/` - Bug fixes (e.g., `fix/account-balance-calculation`)
- `refactor/` - Code refactoring (e.g., `refactor/optimize-database-queries`)
- `docs/` - Documentation updates (e.g., `docs/api-endpoints`)
- `test/` - Test additions or fixes (e.g., `test/account-crud-coverage`)
- `chore/` - Maintenance tasks (e.g., `chore/update-dependencies`)

## Workflow Steps

### 1. Start New Work

```bash
# Ensure you're on master and up to date
git checkout master
git pull origin master

# Create and switch to a new feature branch
git checkout -b feat/your-feature-name
```

### 2. Make Changes

```bash
# Make your changes
# ... edit files ...

# Check what you've changed
git status
git diff

# Stage and commit changes
git add .
git commit -m "feat: Add account export functionality"
```

### 3. Keep Branch Updated

```bash
# Periodically sync with master to avoid conflicts
git fetch origin
git rebase origin/master
```

### 4. Push to Remote

```bash
# Push your branch to GitHub
git push -u origin feat/your-feature-name
```

### 5. Create Pull Request

1. Go to GitHub repository
2. Click "Compare & pull request" button
3. Fill in the PR template
4. Request reviews if needed
5. Wait for CI checks to pass

### 6. After PR Merge

```bash
# Switch back to master
git checkout master
git pull origin master

# Delete local feature branch
git branch -d feat/your-feature-name

# Delete remote feature branch (optional, can be done via GitHub)
git push origin --delete feat/your-feature-name
```

## Commit Message Format

Follow conventional commits specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, missing semicolons, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```bash
# Simple feature
git commit -m "feat: Add CSV export for accounts"

# Bug fix with scope
git commit -m "fix(api): Correct balance calculation in account updates"

# Breaking change
git commit -m "feat!: Change API response format for accounts

BREAKING CHANGE: The accounts endpoint now returns a paginated response"
```

## Pull Request Guidelines

### Before Creating PR

- [ ] All tests pass (`make test`)
- [ ] Code is formatted (`make format`)
- [ ] Linting passes (`make lint`)
- [ ] Type checking passes (`make typecheck`)
- [ ] Branch is up to date with master
- [ ] Commit messages follow convention

### PR Title Format

Use the same format as commit messages:
- `feat: Add user authentication`
- `fix: Resolve database connection timeout`
- `docs: Update API documentation`

### PR Description Template

```markdown
## Summary
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added (if applicable)

## Checklist
- [ ] Code follows project style
- [ ] Self-review completed
- [ ] Documentation updated (if needed)
```

## Handling Conflicts

```bash
# If you have conflicts during rebase
git rebase origin/master

# Fix conflicts in your editor
# After fixing each file:
git add <fixed-file>
git rebase --continue

# If something goes wrong
git rebase --abort
```

## Quick Commands

```bash
# View branch history
git log --oneline --graph --branches

# See what changed in your branch
git diff master...HEAD

# Squash commits before PR (interactive rebase)
git rebase -i origin/master

# Rename your branch
git branch -m old-name new-name
```

## Protected Branch Rules (GitHub Settings)

Recommended settings for `master` branch:
- ✅ Require pull request reviews before merging
- ✅ Dismiss stale pull request approvals when new commits are pushed
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- ✅ Include administrators in restrictions

## Tips

1. **Keep PRs small**: Easier to review and less likely to have conflicts
2. **One feature per PR**: Don't mix unrelated changes
3. **Update frequently**: Rebase often to avoid large conflicts
4. **Write good descriptions**: Help reviewers understand your changes
5. **Test locally first**: Always run tests before pushing
6. **Use draft PRs**: For work in progress that needs early feedback