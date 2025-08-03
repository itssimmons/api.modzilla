create table if not exists chat_reactions (
    id integer primary key autoincrement,
    chat_id text not null,
    sender_id integer not null,
    emoji text not null,
    count integer not null default 0,
    created_at text not null default current_timestamp,

    foreign key(chat_id) references chats(id),
    foreign key(sender_id) references users(id)
)