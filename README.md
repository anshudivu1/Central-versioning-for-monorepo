# Automated Version Management and CI/CD Optimization in Large-Scale Python Monorepos

> Based on the research paper by **Divyanshu Sharma** and **Preeti Saini**, Department of Computer Science and Engineering, Chitkara University, Punjab, India.

---

## Overview

This repository is a working implementation of the **centralized version orchestration framework** proposed in the paper. The core idea is simple: instead of each package maintaining its own version number in source code, a single authoritative version is declared in `workspace.yml` at the repo root. At build time, the CI/CD pipeline reads that version and injects it into every package — leaving source files clean and conflict-free.

### The Problem (Why This Exists)

In a large Python monorepo where every package manages its own semantic version:

- Engineers must create, review, and merge one version-bump commit **per package** before every release (up to 70 PRs in a 70-package repo)
- Concurrent teams updating shared transitive dependencies cause **merge conflicts on every release cycle**
- Different CI/CD runs resolve dependencies at different times, producing **non-deterministic builds**
- Dependency resolution failures are frequent and hard to reproduce locally

### The Solution

A **sentinel versioning strategy** combined with a **build-time injection pipeline**:

- Every `pyproject.toml` in source control always carries `version = "0.0.0.dev0"` (the sentinel)
- The single source of truth for the real version is `workspace.yml`
- The CI/CD pipeline runs `versioning/inject_version.py` before building, which stamps the real version into all packages — only in the build workspace, never in source control

---

## Repository Structure

```
.
├── workspace.yml                   # Single authoritative version declaration
├── VERSION                         # Plain-text version file (for tooling compatibility)
├── packages/
│   ├── package_a/                  # Core utilities library
│   │   ├── pyproject.toml          # version = "0.0.0.dev0" (sentinel)
│   │   └── src/package_a/
│   │       └── __init__.py
│   ├── package_b/                  # Data processing library (depends on package_a)
│   │   ├── pyproject.toml          # version = "0.0.0.dev0" (sentinel)
│   │   └── src/package_b/
│   │       └── __init__.py
│   └── package_c/                  # Reporting library (depends on package_a + package_b)
│       ├── pyproject.toml          # version = "0.0.0.dev0" (sentinel)
│       └── src/package_c/
│           └── __init__.py
└── versioning/
    ├── inject_version.py           # Zero-dependency build-time injection script
    └── pipeline.yml                # GitHub Actions CI/CD workflow
```

### Package Dependency Graph (DAG)

```
package_a
    └── package_b
            └── package_c
```

All inter-package dependencies are **path-based** in source and are replaced with pinned `==RELEASE_VERSION` constraints in released artifacts. The dependency graph is a valid **Directed Acyclic Graph (DAG)** — cycle detection is performed before any injection.

---

## How It Works

### 1. Single Version Authority — `workspace.yml`

```yaml
version: "1.0.0"
```

This is the **only file that changes** during a release. One line. One PR. No per-package version bumps.

### 2. Sentinel Versioning in Source

Every `pyproject.toml` in the repository always reads:

```toml
[tool.poetry]
name = "package-a"
version = "0.0.0.dev0"
```

The sentinel `0.0.0.dev0` is a development placeholder. It is **never published**. A pre-commit hook (described in the paper, Section III-B) prevents any non-sentinel version from being committed.

### 3. Build-Time Injection — `inject_version.py`

At build time the CI/CD pipeline runs:

```bash
python versioning/inject_version.py
```

The script (Algorithm 1 from the paper):

1. Reads `version` from `workspace.yml`
2. Discovers all `pyproject.toml` files under `packages/`
3. Asserts each file still carries the sentinel (`0.0.0.dev0`)
4. Replaces the sentinel with the release version
5. Writes the file back — **in the pipeline workspace only, not in source control**

Time complexity is **O(P)** where P = number of packages. For 70 packages this completes in under 750 ms.

### 4. CI/CD Pipeline — `pipeline.yml`

The GitHub Actions workflow in `versioning/pipeline.yml` triggers automatically **whenever `workspace.yml` is pushed to `main`**:

```
workspace.yml updated → pipeline triggers → inject_version.py runs →
all packages stamped with new version → Poetry builds each package →
artifacts (.whl / .tar.gz) uploaded
```

---

## Releasing a New Version

The entire release process is:

```bash
# 1. Edit workspace.yml — change the version
version: "1.2.0"

# 2. Commit and push to main
git add workspace.yml
git commit -m "release: bump version to 1.2.0"
git push origin main

# 3. The pipeline fires automatically — nothing else to do
```

No per-package commits. No coordinating across teams. No manual version alignment.

---

## Running the Injection Script Locally

Requires only Python 3.10+ (zero external dependencies):

```bash
# From the repo root
python versioning/inject_version.py
```

**Expected output:**
```
Release version read from workspace.yml: 1.0.0
Scanning packages in: .../packages

  OK    package_a: 0.0.0.dev0 -> 1.0.0
  OK    package_b: 0.0.0.dev0 -> 1.0.0
  OK    package_c: 0.0.0.dev0 -> 1.0.0

Done. 3 package(s) processed.
```

Running the script a second time (idempotency guard):
```
  SKIP  package_a: sentinel '0.0.0.dev0' not found (already injected ...)
  SKIP  package_b: sentinel '0.0.0.dev0' not found (already injected ...)
  SKIP  package_c: sentinel '0.0.0.dev0' not found (already injected ...)
```

---

## Empirical Results (from the Paper)

The framework was evaluated over **12 months** across **5 real-world Python monorepos** (12–70 packages):

| Metric | Before | After | Improvement |
|---|---|---|---|
| Version-related merge conflicts | 14.7 / sprint | 1.9 / sprint | **87% reduction** |
| Build reproducibility | 70.4% | 98.4% | **+28 percentage points** |
| Dependency resolution failures | 105 / quarter | 11 / quarter | **89.5% reduction** |
| CI/CD pipeline duration (Repo E, 70 pkgs) | 25.6 min | 16.3 min | **36.3% faster** |
| Total release cycle time | 13.0 days | 7.0 days | **46% reduction** |
| Developer release confidence (survey, 1–10) | — | — | **81% improvement** |
| Perceived release velocity (survey, 1–10) | — | — | **88% improvement** |

### Pipeline Duration Breakdown (70-package repo)

| Phase | Baseline | Proposed | Reduction |
|---|---|---|---|
| Dependency Resolution | 8.4 min | 1.2 min | 85.7% |
| Version Injection | 0.0 min | 0.4 min | — (new step) |
| Build & Package | 6.1 min | 5.9 min | 3.3% |
| Unit Tests | 7.2 min | 7.1 min | 1.4% |
| Integration Tests | 9.8 min | 8.6 min | 12.2% |
| Publication | 1.1 min | 1.0 min | 9.1% |
| **Total** | **25.6 min** | **16.3 min** | **36.3%** |

The dominant win is dependency resolution: resolving once for the whole monorepo instead of once per package (70 → 1 SAT-solver invocations).

---

## Framework Architecture

```
┌─────────────────────┐        ┌──────────────────┐
│  Git Repository     │        │  workspace.yml   │
│  (Source Control)   │──push─▶│  version: 1.0.0  │
└─────────────────────┘        └────────┬─────────┘
                                        │ triggers
                               ┌────────▼─────────┐
                               │   CI/CD Pipeline  │
                               │  (GitHub Actions) │
                               └──┬────────────┬───┘
                                  │            │
                    ┌─────────────▼──┐   ┌─────▼──────────────┐
                    │ Version        │   │ Dependency         │
                    │ Injector       │   │ Synchronizer       │
                    │ (build-time)   │   │ (DAG, Kahn's algo) │
                    └───────┬────────┘   └──────────┬─────────┘
                            │                       │
                    ┌───────▼───────────────────────▼─────────┐
                    │         Package Artifacts                │
                    │         (.whl / .tar.gz)                 │
                    └─────────────────────────────────────────┘
```

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| Sentinel `0.0.0.dev0` in source | Eliminates version-bump commits entirely; PEP 440 compliant development version |
| Plain `workspace.yml` with one field | Minimal surface area = minimal human error; trivially machine-parseable |
| Zero-dependency injection script | Runs in any CI environment without bootstrapping extra tools |
| Path-based deps in source → pinned in artifacts | Supports local development with `develop = true` while guaranteeing exact versions in releases |
| Kahn's topological sort for cycle detection | Guarantees DAG validity before any artifact is produced; fails fast with a descriptive error |

---

## Authors

- **Divyanshu Sharma** — divyanshu1538.be22@chitkara.edu.in
- **Preeti Saini** — preeti.saini@chitkara.edu.in

Department of Computer Science and Engineering, Chitkara University, Punjab, India
