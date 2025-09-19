create table if not exists chats (
    id integer primary key autoincrement,
    sender_id integer not null,
    room_id text not null,
    message text not null,
    type text not null default 'message',
    created_at text not null default current_timestamp,
    updated_at text null,
    deleted_at text null,

    foreign key(sender_id) references users(id),
    foreign key(room_id) references rooms(id)
);

create table if not exists attachments (
    id integer primary key autoincrement,
    chat_id integer not null,
    filename text not null,
    url text not null,
    filetype text not null,
    filesize integer not null,
    uploaded_at text not null default current_timestamp,

    foreign key(chat_id) references chats(id) on delete cascade
);