create table if not exists users (
    id integer primary key autoincrement,
    username text not null,
    avatar text not null,
    color text not null,
    status text not null default 'offline',
    role text not null default 'user',
    created_at text not null default current_timestamp
)
