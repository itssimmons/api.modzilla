create table if not exists chats (
    id text not null primary key,
    sender_id integer not null,
    room_id text not null,
    message text not null,
    created_at text not null default current_timestamp,
    modified_at text null,

    foreign key(sender_id) references users(id),
    foreign key(room_id) references rooms(id)
)
