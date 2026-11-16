#!/usr/bin/env bash
set -Eeuo pipefail

readonly IMAGE='python@sha256:bf44cdfcb76cd3b41e879bc058fc37ec5872002ccfde7fcb765e218cde0cd79c'
readonly TEST_COMMAND='python -m unittest discover'

fail() { printf 'BLOCKED: %s\n' "$1" >&2; exit 2; }

[[ "${BOUNTY_ID:-}" =~ ^[A-Za-z0-9_-]{1,64}$ ]] || fail 'invalid bounty id'
[[ "${BASELINE_REF:-}" =~ ^[0-9a-fA-F]{40}$ ]] || fail 'baseline ref must be a full commit SHA'
[[ "${PATCHED_REF:-}" =~ ^[0-9a-fA-F]{40}$ ]] || fail 'patched ref must be a full commit SHA'
[[ "$BASELINE_REF" != "$PATCHED_REF" ]] || fail 'baseline and patched refs must differ'
[[ "${REPOSITORY_URL:-}" =~ ^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(\.git)?$ ]] || fail 'only public GitHub HTTPS repositories are allowed'

[[ ! -e work && ! -e evidence ]] || fail 'work/ or evidence/ already exists; run in a clean directory to avoid overwriting files'
mkdir -p work/repo work/baseline work/patched evidence
git clone --filter=blob:none --no-checkout "$REPOSITORY_URL" work/repo
git -C work/repo fetch --depth=1 origin "$BASELINE_REF" "$PATCHED_REF"
git -C work/repo archive "$BASELINE_REF" | tar -x -C work/baseline
git -C work/repo archive "$PATCHED_REF" | tar -x -C work/patched

tree_hash() {
  local dir="$1"
  find "$dir" -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum | awk '{print $1}'
}

run_suite() {
  local label="$1" dir="$2"
  local out="evidence/${label}.stdout.log" err="evidence/${label}.stderr.log"
  set +e
  docker run --rm --pull=never \
    --network=none --read-only --user=1000:1000 --cap-drop=ALL \
    --security-opt=no-new-privileges:true --pids-limit=128 --memory=1g --cpus=1 \
    --tmpfs=/tmp:rw,noexec,nosuid,size=128m \
    --env=PYTHONDONTWRITEBYTECODE=1 --env=HOME=/tmp \
    --mount "type=bind,source=$(pwd)/${dir},target=/workspace,readonly" \
    --workdir=/workspace "$IMAGE" python -m unittest discover >"$out" 2>"$err"
  local code=$?
  set -e
  local count
  count=$(grep -Eo 'Ran [0-9]+ tests?' "$err" | tail -1 | grep -Eo '[0-9]+' || true)
  [[ -n "$count" && "$count" -gt 0 ]] || fail "$label suite ran zero tests"
  printf '%s,%s\n' "$code" "$count"
}

docker image inspect "$IMAGE" >/dev/null 2>&1 || docker pull "$IMAGE"
baseline_result=$(run_suite baseline work/baseline)
patched_result=$(run_suite patched work/patched)
IFS=, read -r baseline_code baseline_count <<<"$baseline_result"
IFS=, read -r patched_code patched_count <<<"$patched_result"

[[ "$baseline_code" -ne 0 ]] || fail 'baseline unexpectedly passes; reproduction not demonstrated'
[[ "$patched_code" -eq 0 ]] || fail 'patched test run failed'
[[ "$baseline_count" -eq "$patched_count" ]] || fail 'test count changed between baseline and patched refs'

python3 scripts/write-evidence.py \
  --output evidence/evidence.json \
  --bounty-id "$BOUNTY_ID" --repository-url "$REPOSITORY_URL" \
  --baseline-ref "${BASELINE_REF,,}" --patched-ref "${PATCHED_REF,,}" \
  --baseline-code "$baseline_code" --patched-code "$patched_code" \
  --test-count "$patched_count" --image "$IMAGE" --command "$TEST_COMMAND" \
  --baseline-tree "$(tree_hash work/baseline)" --patched-tree "$(tree_hash work/patched)"

python3 scripts/validate-evidence.py evidence/evidence.json
