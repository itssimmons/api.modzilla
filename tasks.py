from invoke import task

import cli

@task
def serve(c):
    c.run("python .")

@task
def lint(c):
    c.run("pylint app")

@task
def format(c):
    c.run("black app")


@task(name="db:migrate")
def db_migrate(c):
    cli.run_sql_at("migrations")


@task(name="db:seed")
def db_seed(c):
    cli.run_sql_at("seeders")


@task(name="db:rollback")
def db_rollback(c):
    cli.db_rollback()


@task(name="db:wipe")
def db_wipe(c):
    cli.db_wipe()


@task(name="mk:migration")
def mk_migration(c):
    cli.generate_file("migrations")


@task(name="mk:seeder")
def mk_seeder(c):
    cli.generate_file("seeders")
