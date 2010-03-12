# Spaciblō: A Toolkit for Social Spaces on the Web

The main site for this project is http://spaciblo.org/

This project is licensed under the Apache 2 license.  See COPYING.txt for more information.

The correct pronunciation of the name of this project is spah-see-blow.
To get the full effect of the name, it helps to fake an Italian accent and wave your hands. 

The current code wrangler is Trevor F. Smith: http://trevor.smith.name/
He can be reached via email at trevor at spaciblo dot org

Project status: Not Even Alpha!
The code is very early and is not currently recommended for use outside of development.  We are still laying down the infrastructure for web based simulation and there is no 3D renderer.

## Installation:

To install you will need the following:

- OS X or Linux
- Python 2.5+
- Django 1.1+
- PostgreSQL 8.4+
- psycopg2
- South from Aeracode: http://south.aeracode.org/  (just use Trunk)
- simplejson
- git
- A WebGL and WebSockets enabled browser: http://www.khronos.org/webgl/wiki/Getting_a_WebGL_Implementation

### Example installation commands

> # create the database
> echo "create database spaciblo; grant all on database spaciblo to postgres;" | psql -U postgres

> # get the code
> git clone http://github.com/Spaciblo/spaciblo.git

> # set up Django
> cd spaciblo/spaciblo
> cp local_settings.py.example local_settings.py
> # Then edit the local settings to reflect your environment

> # populate the database
> ./manage.py syncdb # you will need to create your admin username and pass
> ./manage.py migrate
> ./manage.py load_example_spaces

## Running:

> # run the web service
> cd spaciblo/spaciblo
> ./manage.py runserver 0.0.0.0:8000

> # run the simulators (in another shell)
> cd spaciblo/spaciblo
> ./manage.py run_sim_server

## Using Spaciblo:

> Point your browser at http://127.0.0.1:8000/ and login.
> Now on the front page you should see a list of available spaces.
> Click "The Hills".

Check the Issues section of the GitHub project for current development direction:
https://github.com/Spaciblo/spaciblo

