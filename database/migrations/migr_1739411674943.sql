create table if not exists user_status (
    id integer primary key autoincrement,
    user_id integer not null,
    status text not null default 'offline',
    last_seen text not null default current_timestamp,

    foreign key(user_id) references users(id)
);