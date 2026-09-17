import json
import os

from dotenv import load_dotenv

from app.services.material.project_service import MaterialsProjectService


def main() -> int:
    configured_env_file = os.getenv("MATERIALGRAPH_ENV_FILE")
    if configured_env_file != "":
        load_dotenv(configured_env_file or ".env")
    api_key = os.getenv("MATERIALS_PROJECT_API_KEY")
    if not api_key:
        raise ValueError("MATERIALS_PROJECT_API_KEY is not configured")
    release = MaterialsProjectService(api_key).get_database_version()
    print(json.dumps({"source_release": release}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
