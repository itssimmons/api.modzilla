from invoke.tasks import task # type: ignore[misc]
from invoke.context import Context

import cli

@task
def serve(c: Context):
    c.run("python .")

@task
def lint(c: Context):
    c.run("pylint app")

@task
def format(c: Context):
    c.run("black app")


@task(name="db:migrate") # type: ignore[misc]
def db_migrate(c: Context):
    cli.run_sql_at("migrations")


@task(name="db:seed") # type: ignore[misc]
def db_seed(c: Context):
    cli.run_sql_at("seeders")


@task(name="db:rollback") # type: ignore[misc]
def db_rollback(c: Context):
    cli.db_rollback()


@task(name="db:wipe") # type: ignore[misc]
def db_wipe(c: Context):
    cli.db_wipe()
    

@task(name="mk:migration")  # type: ignore[misc]
def mk_migration(c: Context):
    cli.generate_file("migrations")


@task(name="mk:seeder") # type: ignore[misc]
def mk_seeder(c: Context):
    cli.generate_file("seeders")
