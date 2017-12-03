#!/bin/sh

service postgresql start
export FLASK_APP="run.py"
export SECRET="sir3n.sn@gmail.com"
export APP_SETTINGS="development"
export DATABASE_URI="postgresql://localhost/challenge_3_api"
python3 manage.py db init
python3 manage.py db migrate
python3 manage.py db upgrade
