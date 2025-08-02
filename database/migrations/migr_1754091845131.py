from config.database import Builder


def up():
    Builder.raw_query(
        sql="""create table if not exists message_reactions (
id integer primary key autoincrement,
message_id text not null,
sender_id integer not null,
emoji text not null,
count integer not null default 0,
created_at text not null default current_timestamp,

foreign key(message_id) references messages(id),
foreign key(sender_id) references users(id)
)"""
    )