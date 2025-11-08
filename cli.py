from typing import Literal

DATABASE_PATH = "database/db.sqlite3"

def generate_file(dest_folder: str):
    from pathlib import Path
    from time import time

    ms = round(time() * 1000)
    file_name = ""

    if dest_folder == "migrations":
        file_name = f"migr_{ms}.sql"
    elif dest_folder == "seeders":
        file_name = f"seed_{ms}.sql"

    db_path = Path(DATABASE_PATH)
    migrations_dir = db_path.parent / dest_folder
    migrations_dir.mkdir(parents=True, exist_ok=True)

    path = migrations_dir / file_name

    with path.open("w") as f:
        f.write(
            """insert into <table>
    (a, b, c, d)
values
    (
        ?, ?, ?, ?
    )
"""
        )

    print(f"{dest_folder[:-1].capitalize()} created at: {dest_folder}/{file_name} 🎨")


def db_wipe():
    from pathlib import Path

    path = Path(DATABASE_PATH)

    if path.exists():
        Path(DATABASE_PATH).unlink()

    Path(DATABASE_PATH).touch()
    print("Database wiped successfully 🧹")


def db_rollback():
    """
    TODO: The entire function
    """

    print("Rollback not implemented yet 😔")


def run_sql_at(level: Literal["migrations", "seeders"]):
    """
    Looping over all migrations and run the up command individually
    """
    label = level[:-1]

    from pathlib import Path

    db_path = Path(DATABASE_PATH)
    dir = db_path.parent / level

    pathlist = list(dir.glob("*.sql"))
    
    from addons.builder import Builder

    for file_path in pathlist:
        from time import time

        start = time()

        print(f"Running {label}: {file_path.name} ⏳")

        raw_sql = file_path.read_text()
        Builder.raw_query(script=raw_sql)

        end = time()
        print(
            f"{label.capitalize()} {file_path.name}"
            f" ran successfully in {((end - start) * 1000):.2f}ms ✨\n"
        )
