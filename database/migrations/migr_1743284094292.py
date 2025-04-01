from config.database import Builder


def up():
    Builder.raw_query(
        sql="""alter table users
add column sid text null"""
    )
