create table if not exists users (
    id integer primary key autoincrement,
    username text not null,
    email text not null unique,
    password_hash text not null,
    name text not null,
    avatar text null,
    color text not null,
    created_at text not null default current_timestamp,
    updated_at text null
);

create table if not exists `sessions` (
    id integer primary key autoincrement,
    sid text null unique,
    user_id integer not null,
    connected_at text not null default current_timestamp,
    disconnected_at text null,
    foreign key (user_id) references users (id)
);

create table if not exists tokens (
    id integer primary key autoincrement,
    user_id integer not null,
    token text not null unique,
    ip_address text null,
    user_agent text null,
    created_at text not null default current_timestamp,
    expires_at text not null,
    
    foreign key (user_id) references users (id) on delete cascade
);