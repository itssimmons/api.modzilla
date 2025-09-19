create table if not exists rooms (
    id text not null primary key,
    name text not null,
    description text null,
    logo text null,
    max_members integer not null default 100,
    is_private integer not null default 0,
    secret_key text null,
    owner_id integer not null,
    created_at text not null default current_timestamp,
    updated_at text null,
    
    foreign key(owner_id) references users(id)
);

-- Many-to-Many relationship between users and rooms

create table if not exists room_members (
    room_id text not null,
    user_id integer not null,
    joined_at text not null default current_timestamp,
    
    primary key(room_id, user_id),
    foreign key(room_id) references rooms(id) on delete cascade,
    foreign key(user_id) references users(id) on delete cascade
);

create table if not exists friendships (
    user_id integer not null,
    friend_id integer not null,
    created_at text not null default current_timestamp,
    
    primary key(user_id, friend_id),
    foreign key(user_id) references users(id) on delete cascade,
    foreign key(friend_id) references users(id) on delete cascade
);

-- Voice/Video Call Tables

create table if not exists room_calls (
    id integer primary key autoincrement,
    room_id text not null,
    started_by integer not null,
    started_at text not null default current_timestamp,
    ended_at text null,
    
    foreign key(room_id) references rooms(id) on delete cascade,
    foreign key(started_by) references users(id) on delete cascade
);

create table if not exists call_participants (
    call_id integer not null,
    user_id integer not null,
    joined_at text not null default current_timestamp,
    left_at text null,
    
    primary key(call_id, user_id),
    foreign key(call_id) references room_calls(id) on delete cascade,
    foreign key(user_id) references users(id) on delete cascade
);