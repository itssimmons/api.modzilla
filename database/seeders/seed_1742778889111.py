from config.database import Builder


def up():
    Builder.raw_query(
        sql="""INSERT INTO users
(username, avatar, color, status, role)
VALUES
    (
        'Assistant',
        'https://avatar.iran.liara.run/public/16',
        '#EB6134',
        'online',
        'assistant'
    )"""
    )
