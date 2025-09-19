create table if not exists punishments (
    id integer primary key autoincrement,
    user_id integer not null,
    reason text not null,
    type text not null,
    issued_by integer not null,
    created_at text default current_timestamp,
    updated_at text default current_timestamp,
    expires_at text,

    foreign key (user_id) references users(id) on delete cascade,
    foreign key (issued_by) references users(id) on delete cascade
);