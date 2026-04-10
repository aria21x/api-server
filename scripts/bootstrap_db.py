from pathlib import Path
from core.db.postgres import get_conn


def main() -> None:
    schema = Path("core/db/schema.sql").read_text(encoding="utf-8")
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(schema)
    print("Database bootstrapped.")


if __name__ == "__main__":
    main()
