create table if not exists reactions (
    chat_id text not null,
    sender_id integer not null,
    emoji text not null,
    created_at text not null default current_timestamp,
    
    primary key(chat_id, sender_id, emoji),
    foreign key(chat_id) references chats(id),
    foreign key(sender_id) references users(id)
)