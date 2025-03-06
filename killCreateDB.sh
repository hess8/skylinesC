fuser -k 5000/tcp
sudo sudo -u postgres psql -d skylines_test -c 'drop database skylines;'
sudo sudo -u postgres createdb skylines -O $USER
sudo sudo -u postgres psql -d skylines -c 'CREATE EXTENSION postgis;'
sudo sudo -u postgres psql -d skylines -c 'CREATE EXTENSION fuzzystrmatch;'
#### generally want to do pgrestore now...it has the schema.  
#### below is for restoring just a few tables
#pipenv run ./manage.py db create
#pg_restore -d skylines  --data-only  -t airports -t models /home/bret/servers/database_backups/airportsModels.custom  
