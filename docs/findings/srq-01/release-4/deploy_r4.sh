#!/usr/bin/env bash
# Release 4 guarded backend switch (SRQ-01 PR-B). Run on the server as ubuntu:
#   bash /tmp/mg-r4/deploy_r4.sh
# Every check runs immediately before the switch; any failure stops the script.
# A failure after checkout but before restart restores the Release 3 checkout,
# so the running service (still Release 3 code) is never restarted onto an
# unverified tree.
set -euo pipefail

EXPECTED=bf0e702f88615d6de7f3cb62bfe225902c4fe0b1   # release-3, currently deployed
TARGET=50dd3eda31bbb1930dcc2782e3ec777af3c35244     # reviewed Release 4 commit

cd /opt/materialgraph
umask 022
git fetch origin

stop() { echo "STOP: $1"; exit 1; }
if git symbolic-ref -q HEAD >/dev/null; then stop "checkout is not detached"; fi
[ "$(git rev-parse HEAD)" = "$EXPECTED" ] || stop "HEAD is not release-3 ($EXPECTED)"
[ -z "$(git status --porcelain --untracked-files=no)" ] || stop "tracked files are modified"
git cat-file -e "$TARGET^{commit}" 2>/dev/null || stop "target commit not present after fetch"
[ "$(git rev-parse "$TARGET^{commit}")" = "$TARGET" ] || stop "target does not resolve to the reviewed commit"
git merge-base --is-ancestor "$EXPECTED" "$TARGET" || stop "release-3 is not an ancestor of the target"
git diff --quiet "$EXPECTED" "$TARGET" -- requirements-production.lock requirements-production.in pyproject.toml alembic materialgraph.service materialgraph.nginx frontend \
  || stop "dependency, migration, unit, Nginx or frontend files differ: not a backend-only release"

# Dependency checks BEFORE checkout. The lock is identical in both commits
# (checked above), so the current tree verifies the target's environment.
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip check
python scripts/check_dependency_contract.py --check-installed
echo "ALL PRECONDITIONS PASSED"

restore() {
  echo "FAILURE before restart: restoring the release-3 checkout"
  git switch --detach "$EXPECTED"
  echo "HEAD now $(git rev-parse HEAD); service was not restarted"
}
trap restore ERR
git switch --detach "$TARGET"
[ "$(git rev-parse HEAD)" = "$TARGET" ]
[ -z "$(git status --porcelain --untracked-files=no)" ]
trap - ERR

echo "restart at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
sudo systemctl restart materialgraph
sleep 3
systemctl is-active materialgraph
curl -sS --fail http://127.0.0.1:8000/health; echo
echo "DEPLOYED $(git rev-parse HEAD) at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
