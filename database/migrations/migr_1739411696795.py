from config.database import Builder


def up():
    Builder.raw_query(
        sql="""create table if not exists rooms (
id text not null primary key,
name text not null,
description text not null,
logo text null,
created_at text not null default current_timestamp,
modified_at text null
)"""
    )