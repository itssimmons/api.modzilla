from config.database import Builder


def up():
    Builder.raw_query(
        sql="""insert into users
(username, avatar, color, status, role)
values
    (
        'Assistant',
        'https://ui-avatars.com/api/?background=CEA2FD&name=Assistant&length=1',
        '#CEA2FD',
        'online',
        'staff'
    )"""
    )
