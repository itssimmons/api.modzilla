def db_migrate():
    """
    TODO: Loop over all migrations and run the up command
    """

    from database.migrations.migr_1739411674942 import up as up_1
    from database.migrations.migr_1739411696796 import up as up_2
    from database.migrations.migr_1743284094292 import up as up_3

    up_1()
    up_2()
    up_3()


def db_seed():
    """
    TODO: Loop over all seeders and run the up command
    """

    from database.seeders.seed_1742778889111 import up as up_1

    up_1()


def db_rollback():
    """
    TODO: The entire function
    """

    pass


def db_wipe():
    from pathlib import Path
    from config.database import DATABASE_PATH

    path = Path(DATABASE_PATH)

    if path.exists():
        Path(DATABASE_PATH).unlink()

    Path(DATABASE_PATH).touch()


def generate_file(file_folder: str):
    from pathlib import Path
    from config.database import DATABASE_PATH
    from time import time

    ms = round(time() * 1000)
    file_name = ""

    if file_folder == "migrations":
        file_name = f"migr_{ms}.py"
    elif file_folder == "seeders":
        file_name = f"seed_{ms}.py"

    db_path = Path(DATABASE_PATH)
    migrations_dir = db_path.parent / file_folder
    migrations_dir.mkdir(parents=True, exist_ok=True)

    path = migrations_dir / file_name

    with path.open("w") as f:
        f.write(
            """from config.database import Builder

def up():
    Builder.raw_query(
        sql=\"\"\"YOUR QUERY HERE...\"\"\"
    )"""
        )

    print(f"{file_folder[:-1].capitalize()} created at: {file_folder}/{file_name} ✨")


from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument(
    "command",
    choices=["db:migrate", "db:seed", "db:wipe", "create:migration", "create:seeder"],
)
args = parser.parse_args()

if args.command == "db:migrate":
    db_migrate()

if args.command == "db:seed":
    db_seed()

if args.command == "db:wipe":
    db_wipe()

if args.command == "create:migration":
    generate_file("migrations")

if args.command == "create:seeder":
    generate_file("seeders")
