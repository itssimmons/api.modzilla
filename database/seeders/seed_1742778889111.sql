insert into roles (slug) values ('staff'), ('default');

insert into user_roles (user_id, role_id)
select u.id, r.id
from users u, roles r
where u.username = 'Assistant' and r.slug = 'staff';