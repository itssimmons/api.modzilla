insert into users
    (
        name,
        username,
        email,
        password_hash,
        avatar,
        color
    )
values
    (
        'Assistant',
        'assistant',
        'assistant@acme.com',
        -- password is 'averysecurepassword123!'
        '$2b$12$iOl.YAVeHRPXDrdH5KBtzeciPRJobuXqdjKmTDXjdjxHvbJoS25Be',
        'https://ui-avatars.com/api/?background=CEA2FD&name=Assistant&length=1',
        '#CEA2FD'
    );