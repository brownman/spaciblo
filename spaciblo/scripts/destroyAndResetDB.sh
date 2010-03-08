#!/bin/bash

echo "drop database spaciblo; create database spaciblo; grant all on database spaciblo to postgres;" | psql -U postgres
./manage.py syncdb --noinput
echo "insert into auth_user values (0, 'trevor', 'Trevor', 'Smith', 'trevor@trevor.smith.name', 'sha1\$64d58\$08a2ea90e0ea7de360d266e544400dd0d02f05ee', true, true, true, now(), '2010-01-01');" | psql -U postgres spaciblo
echo "update django_site set domain = '127.0.0.1:8000', name = 'Spaciblo' where id = 1;" | psql -U postgres spaciblo
./manage.py migrate
./manage.py load_example_spaces
