import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_ROOT = PROJECT_ROOT / ".github" / "workflows"
LOCAL_HOOK = PROJECT_ROOT / ".githooks" / "pre-commit"

FULL_COMMIT_SHA = re.compile(r"^[0-9a-f]{40}$")
GITLEAKS_IMAGE = re.compile(
    r"ghcr\.io/gitleaks/gitleaks:v[0-9]+\.[0-9]+\.[0-9]+"
    r"@sha256:[0-9a-f]{64}"
)


def workflow_action_references() -> list[tuple[Path, int, str]]:
    references = []
    for workflow in sorted(WORKFLOW_ROOT.glob("*.y*ml")):
        for line_number, line in enumerate(
            workflow.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            match = re.match(r"\s*-?\s*uses:\s*([^\s#]+)", line)
            if match:
                references.append((workflow, line_number, match.group(1)))
    return references


def validate_action_references() -> list[str]:
    errors = []
    for workflow, line_number, reference in workflow_action_references():
        if reference.startswith("./"):
            continue
        _, separator, revision = reference.rpartition("@")
        if not separator or not FULL_COMMIT_SHA.fullmatch(revision):
            relative = workflow.relative_to(PROJECT_ROOT)
            errors.append(
                f"{relative}:{line_number}: third-party action is not pinned "
                "to a full commit SHA"
            )
    return errors


def configured_gitleaks_images() -> list[str]:
    files = [*sorted(WORKFLOW_ROOT.glob("*.y*ml")), LOCAL_HOOK]
    images = []
    for path in files:
        images.extend(GITLEAKS_IMAGE.findall(path.read_text(encoding="utf-8")))
    return images


def validate_gitleaks_images() -> list[str]:
    images = configured_gitleaks_images()
    if len(images) != 2:
        return ["expected exactly two pinned Gitleaks image references"]
    if len(set(images)) != 1:
        return ["CI and local hook Gitleaks image references differ"]
    return []


def main() -> int:
    errors = validate_action_references() + validate_gitleaks_images()
    for error in errors:
        print(f"automation_pin_error: {error}")
    if errors:
        return 1
    print("automation_pins_valid=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
