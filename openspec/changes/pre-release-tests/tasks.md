## 1. Release script

- [x] 1.1 Add `pytest` to the tool availability check in `release.sh`
- [x] 1.2 Add test + coverage step after pre-flight checks, before version bump
- [x] 1.3 Verify: failing tests abort the release (`set -euo pipefail` ensures non-zero pytest exit aborts)

## 2. Documentation

- [x] 2.1 Update README release section to mention the test gate
