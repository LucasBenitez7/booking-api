# Contributing to BookingAPI

## Conventional Commits

This project follows [Conventional Commits](https://www.conventionalcommits.org/). Every commit message must follow this format:

```
<type>(<scope>): <description>
```

### Types

| Type       | When to use                 |
| ---------- | --------------------------- |
| `feat`     | New feature                 |
| `fix`      | Bug fix                     |
| `chore`    | Maintenance, deps updates   |
| `docs`     | Documentation changes       |
| `test`     | Adding or updating tests    |
| `refactor` | Code change, no feature/fix |
| `ci`       | CI/CD changes               |
| `perf`     | Performance improvements    |

### Examples

```
feat(bookings): add create booking endpoint
fix(auth): resolve token expiration issue
chore(deps): update fastapi to 0.115
docs(readme): add local setup instructions
test(domain): add time slot overlap tests
ci(github): add bandit security scan
```

### Scopes

Use the layer or module affected: `auth`, `bookings`, `spaces`, `domain`, `api`, `workers`, `cache`, `ci`, `deps`, `k8s`

## Branch Naming

```
feat/fase-0-setup
feat/booking-domain
fix/auth-token-expiry
```

## Pull Requests

- One PR per phase or feature
- PR title must also follow Conventional Commits format
- CI must pass before merging
