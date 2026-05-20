## Summary

<!-- 1-3 bullet points. What changed and why. -->

## Checklist

- [ ] `ruff check .` passes
- [ ] `ruff format --check .` passes
- [ ] `mypy src/` passes
- [ ] `pytest` passes locally; CI coverage gate (see `ci.yml`) will enforce the threshold
- [ ] CHANGELOG.md `[Unreleased]` updated if user-visible
- [ ] No `.coverage`, `.env`, secrets, or build artifacts committed

## Type of change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] CI / tooling
- [ ] Security
