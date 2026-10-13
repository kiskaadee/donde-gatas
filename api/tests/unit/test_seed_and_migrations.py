import importlib.util
import math
from pathlib import Path

from api.database.seed import INITIAL_SCULPTURES, INITIAL_USER, generate_normalized_embedding


def test_normalized_embedding_properties():
    vec = generate_normalized_embedding(seed_int=42, dimensions=1280)
    assert len(vec) == 1280

    # Verify L2 norm == 1.0
    l2_norm = math.sqrt(sum(x * x for x in vec))
    assert math.isclose(l2_norm, 1.0, rel_tol=1e-3)

    # Determinism
    vec_repeat = generate_normalized_embedding(seed_int=42, dimensions=1280)
    assert vec == vec_repeat


def test_initial_sculptures_data_validity():
    assert len(INITIAL_SCULPTURES) == 3

    for item in INITIAL_SCULPTURES:
        # Geographic bounds for Cali, Colombia
        assert 3.30 <= item["latitude"] <= 3.60
        assert -76.60 <= item["longitude"] <= -76.40
        assert item["year"] >= 1996
        assert len(item["name"]) > 0
        assert len(item["artist"]) > 0
        assert item["status"] in ("on-site", "moved", "missing")


def test_initial_user_data_validity():
    assert "@" in INITIAL_USER["email"]
    assert 0.0 <= INITIAL_USER["trust_score"] <= 1.0
    assert len(INITIAL_USER["name"]) > 0


def test_migration_001_structure():
    migration_file = Path(__file__).parents[2] / "alembic" / "versions" / "001_initial_schema.py"
    assert migration_file.is_file()

    spec = importlib.util.spec_from_file_location("migration_001", str(migration_file))
    assert spec is not None
    assert spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    assert hasattr(mod, "upgrade")
    assert callable(mod.upgrade)
    assert hasattr(mod, "downgrade")
    assert callable(mod.downgrade)
    assert mod.revision == "001_initial_schema"
