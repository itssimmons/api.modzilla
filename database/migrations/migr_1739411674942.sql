create table if not exists users (
    id integer primary key autoincrement,
    sid text null,
    modified_by integer null,
    username text not null,
    avatar text not null,
    color text not null,
    status text not null default 'offline',
    role text not null default 'user',
    created_at text not null default current_timestamp,
    
    foreign key(modified_by) references users(id)
)
