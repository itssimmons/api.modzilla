from config.database import Builder


def up():
    Builder.raw_query(
        sql="""create table if not exists chats (
id text not null primary key,
sender_id integer not null,
modified_id integer null,
message text not null,
created_at text not null default current_timestamp,
modified_at text null
)"""
    )
