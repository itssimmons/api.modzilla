create table if not exists roles (
    id integer primary key autoincrement,
    slug text not null unique
);

create table if not exists user_roles (
    user_id integer not null,
    role_id integer not null,
    primary key (user_id, role_id)
);