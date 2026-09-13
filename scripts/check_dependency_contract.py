import argparse
import importlib.metadata
import re
import tomllib
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = (
    (
        PROJECT_ROOT / "requirements-production.in",
        PROJECT_ROOT / "requirements-production.lock",
    ),
    (
        PROJECT_ROOT / "requirements-audit.in",
        PROJECT_ROOT / "requirements-audit.lock",
    ),
)

PIN = re.compile(r"^([A-Za-z0-9_.-]+)(?:\[[^]]+\])?==([^\s;\\]+)")
HASH = re.compile(r"--hash=sha256:[0-9a-f]{64}")
UNSAFE_REFERENCE = re.compile(
    r"(^|\n)\s*-e\s|git\+|https?://|--trusted-host",
    re.IGNORECASE,
)


def canonical_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def input_pins(path: Path) -> dict[str, str]:
    pins = {}
    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = PIN.fullmatch(line)
        if not match:
            raise ValueError(f"{path.name}:{line_number}: expected one exact pin")
        name = canonical_name(match.group(1))
        if name in pins:
            raise ValueError(f"{path.name}:{line_number}: duplicate pin for {name}")
        pins[name] = match.group(2)
    return pins


def lock_pins(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if UNSAFE_REFERENCE.search(text):
        raise ValueError(f"{path.name}: unsafe external requirement reference")

    pins = {}
    current_name = None
    current_has_hash = False

    def finish_entry() -> None:
        if current_name is not None and not current_has_hash:
            raise ValueError(f"{path.name}: {current_name} has no SHA-256 hash")

    for line_number, line in enumerate(text.splitlines(), start=1):
        match = PIN.match(line)
        if match:
            finish_entry()
            name = canonical_name(match.group(1))
            if name in pins:
                raise ValueError(f"{path.name}:{line_number}: duplicate pin for {name}")
            pins[name] = match.group(2)
            current_name = name
            current_has_hash = bool(HASH.search(line))
        elif current_name is not None and HASH.search(line):
            current_has_hash = True

    finish_entry()
    if not pins:
        raise ValueError(f"{path.name}: no pinned requirements found")
    return pins


def validate_contracts() -> tuple[dict[str, str], list[str]]:
    errors = []
    production = {}
    production_direct = {}

    for input_path, lock_path in CONTRACTS:
        try:
            direct = input_pins(input_path)
            locked = lock_pins(lock_path)
        except (OSError, ValueError) as error:
            errors.append(str(error))
            continue

        if input_path.name == "requirements-production.in":
            production = locked
            production_direct = direct

        for name, version in direct.items():
            if locked.get(name) != version:
                errors.append(
                    f"{lock_path.name}: direct pin {name}=={version} is missing"
                )

    try:
        project = tomllib.loads(
            (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        )
        project_dependencies = project["project"]["dependencies"]
        project_pins = {}
        for dependency in project_dependencies:
            match = PIN.fullmatch(dependency)
            if not match:
                errors.append(f"pyproject.toml: dependency is not exact: {dependency}")
                continue
            project_pins[canonical_name(match.group(1))] = match.group(2)
        for name, version in project_pins.items():
            if production_direct.get(name) != version:
                errors.append(
                    f"requirements-production.in: project pin {name}=={version} "
                    "is missing"
                )
    except (KeyError, OSError, tomllib.TOMLDecodeError) as error:
        errors.append(f"pyproject.toml: cannot validate dependencies: {error}")

    return production, errors


def validate_installed(expected: dict[str, str]) -> list[str]:
    installed = {}
    errors = []
    for distribution in importlib.metadata.distributions():
        raw_name = distribution.metadata.get("Name")
        if not raw_name:
            continue
        name = canonical_name(raw_name)
        if name in installed and installed[name] != distribution.version:
            errors.append(f"multiple installed versions found for {name}")
        installed[name] = distribution.version

    installed.pop("materialgraph", None)

    for name in sorted(expected.keys() | installed.keys()):
        expected_version = expected.get(name)
        installed_version = installed.get(name)
        if expected_version != installed_version:
            errors.append(
                f"installed mismatch: {name} expected={expected_version or 'absent'} "
                f"actual={installed_version or 'absent'}"
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-installed", action="store_true")
    arguments = parser.parse_args()

    production, errors = validate_contracts()
    if arguments.check_installed and not errors:
        errors.extend(validate_installed(production))

    for error in errors:
        print(f"dependency_contract_error: {error}")
    if errors:
        return 1

    print("dependency_contract_valid=true")
    if arguments.check_installed:
        print("installed_environment_matches_lock=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
