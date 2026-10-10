"""Gate B - production dataset identity (read-only).

Runs only SELECT statements, prints no URLs or credentials (DB host shown as a
12-char SHA-256 fingerprint), and rolls back before closing.
Run via systemd-run so the environment is loaded exactly as for the service.
"""

import hashlib

from sqlalchemy import inspect, text
from sqlalchemy.engine import make_url

from app.core.config import settings
from app.core.database import SessionLocal
from app.services.discovery.chain_service import DiscoveryChainService

u = make_url(settings.database_url)
print("db_name:", u.database,
      "| host_fp:", hashlib.sha256((u.host or "").encode()).hexdigest()[:12],
      "| env:", settings.environment)

s = SessionLocal()
try:
    print("alembic:", s.execute(text("select version_num from alembic_version")).scalar())
    insp = inspect(s.bind)
    print("tables:", sorted(t for t in insp.get_table_names()
                            if "material" in t or t == "elements"))
    print("materials:", s.execute(text("select count(*) from materials")).scalar())
    print("materials without element rows:", s.execute(text(
        "select count(*) from materials m where not exists "
        "(select 1 from material_elements me where me.material_id = m.id)")).scalar())

    cols = [c["name"] for c in insp.get_columns("materials")]
    want = [c for c in ("id", "mp_id", "formula", "pretty_formula") if c in cols]
    row = s.execute(text(f"select {', '.join(want)} from materials where id = 5")).mappings().first()
    print("material 5:", dict(row or {}))

    svc = DiscoveryChainService(s)
    em = svc._get_material_elements_map()
    fam = [c for c in svc._get_family_result(5)["related_materials"]
           if not (c.get("mp_id") or "").startswith("mp-test")]
    lim = svc.EXPANSION_LIMIT
    print("EXPANSION_LIMIT:", lim, "| family size (5):", len(fam))
    print(f"first {lim}:", [(c["material_id"], c.get("pretty_formula")) for c in fam[:lim]])
    print(f"Li in first {lim}:", sum("Li" in em.get(c["material_id"], []) for c in fam[:lim]))
    for el in ("Na", "K"):
        hits = [(i + 1, c["material_id"], c.get("pretty_formula"))
                for i, c in enumerate(fam) if el in em.get(c["material_id"], [])]
        print(f"{el}: {len(hits)} in family; first positions:", hits[:5])
    no_elements = sum(1 for c in fam if not em.get(c["material_id"]))
    print("family members without element rows:", no_elements)
finally:
    s.rollback()
    s.close()
