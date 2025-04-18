# set environment variables

cat >> ~/.profile << EOF
export POSTGIS_GDAL_ENABLED_DRIVERS=GTiff
export POSTGIS_ENABLE_OUTDB_RASTERS=1
EOF

#remove any locks

sudo killall apt apt-get
sudo rm /var/lib/apt/lists/lock
sudo rm /var/cache/apt/archives/lock
sudo rm /var/lib/dpkg/lock*
sudo dpkg --configure -a

# update apt-get repository

sudo apt-get update

# install add-apt-repository tool

sudo apt-get install -y --no-install-recommends software-properties-common
sudo apt-get install build-essential
# add PPAs

sudo add-apt-repository -y ppa:ubuntu-toolchain-r/test
# sudo add-apt-repository -y ppa:jonathonf/python-2.7 #not compa

# update apt-get repository

sudo apt-get update

# install base dependencies

sudo apt-get install -y --no-install-recommends \
   python python-dev \

sudo apt-get install -y --no-install-recommends \
    g++-6 pkg-config libcurl4-openssl-dev redis-server\
    libpq-dev libfreetype6-dev libpng-dev libffi-dev
echo 'New libs:'
sudo apt-get install -y --no-install-recommends \
    ibgeos-c1 liblwgeom-2.2-5

sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt trusty-pgdg main" >> /etc/apt/sources.list'
wget --quiet -O - http://apt.postgresql.org/pub/repos/apt/ACCC4CF8.asc | sudo apt-key add -
sudo apt update
sudo apt install -y postgresql-10
sudo apt install -y postgresql-10-postgis-2.4
sudo apt install -y postgresql-10-postgis-scripts
sudo apt install -y postgis
sudo apt install -y postgresql-10-pgrouting


##Lines from vagrant file:
#sudo apt-get install -y --no-install-recommends \
#    python python-dev \
#    g++-6 pkg-config libcurl4-openssl-dev git redis-server \
#    libpq-dev postgresql-9.5-postgis-2.2 postgresql-9.5-postgis-2.2-scripts postgresql-contrib-9.5 \
#    libfreetype6-dev libpng-dev libffi-dev

# set GCC 6 as default

sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-6 60 --slave /usr/bin/g++ g++ /usr/bin/g++-6

# sudo -H pip install pipenv
# sudo apt-get install -y pkg-config

# install skylines and the python dependencies
apt-get install -y libcurl4-openssl-dev libfreetype6-dev
sudo apt-get install -y libpq-dev
sudo pipenv install --verbose  gitflask
sudo pipenv install --verbose  babel
sudo pipenv install --verbose  flask-caching
sudo pipenv install --verbose  flask-migrate
sudo pipenv install --verbose  flask_script
sudo pipenv install --verbose  flask-sqlalchemy
sudo pipenv install --verbose  psycopg2
sudo pipenv install --verbose  geoalchemy2
sudo pipenv install --verbose  shapely
sudo pipenv install --verbose  crc16
sudo pipenv install --verbose  pytz
sudo pipenv install --verbose  celery
sudo pipenv install --verbose  redis
sudo pipenv install --verbose  xcsoar
sudo pipenv install --verbose  aerofiles
sudo pipenv install --verbose  enum34
sudo pipenv install --verbose  pyproj
sudo pipenv install --verbose  gevent
sudo pipenv install --verbose  webargs
sudo pipenv install --verbose  flask-oauthlib
sudo pipenv install --verbose  requests-oauthlib
sudo pipenv install --verbose  sentry-sdk
sudo pipenv install --verbose  mapproxy
sudo pipenv install --verbose  gunicorn
sudo pipenv install --verbose  fabric
sudo pipenv install --verbose  pytest
sudo pipenv install --verbose  pytest-cov
sudo pipenv install --verbose  pytest-voluptuous
sudo pipenv install --verbose  mock
sudo pipenv install --verbose  faker
sudo pipenv install --verbose  flake8
sudo pipenv install --verbose  immobilus
sudo pipenv install --verbose  blinker
sudo pipenv install --verbose more-itertools


# sudo pipenv install --verbose --verbose --dev  --skip-lock #this doesn't work with skip-lock...seems to work without it, but can't lock anyway due to oauth dependency problems

# create PostGIS databases

# sudo sudo -u postgres createuser -s $USER

# sudo sudo -u postgres createdb skylines -O $USER
# sudo sudo -u postgres psql -d skylines -c 'CREATE EXTENSION postgis;'
# sudo sudo -u postgres psql -d skylines -c 'CREATE EXTENSION fuzzystrmatch;'

# sudo sudo -u postgres createdb skylines_test -O $USER
# sudo sudo -u postgres psql -d skylines_test -c 'CREATE EXTENSION postgis;'
# sudo sudo -u postgres psql -d skylines_test -c 'CREATE EXTENSION fuzzystrmatch;'

# sudo sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'secret123';"

# pipenv run ./manage.py db create

# create folder for downloaded files
mkdir -p htdocs/files
mkdir -p htdocs/srtm
mkdir -p filesBackup

# Front end
#add-apt-repository may not be present on some Ubuntu releases:
sudo apt-get install python-software-properties

sudo add-apt-repository -y -r ppa:chris-lea/node.js
sudo rm -f /etc/apt/sources.list.d/chris-lea-node_js-*.list
sudo rm -f /etc/apt/sources.list.d/chris-lea-node_js-*.list.save
curl -sSL https://deb.nodesource.com/gpgkey/nodesource.gpg.key | sudo apt-key add -
VERSION=node_12.x
DISTRO="$(lsb_release -s -c)"
echo "deb https://deb.nodesource.com/$VERSION $DISTRO main" | sudo tee /etc/apt/sources.list.d/nodesource.list
sudo apt-get update
sudo apt-get install -y nodejs

curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
echo "deb-src https://deb.nodesource.com/$VERSION $DISTRO main" | sudo tee -a /etc/apt/sources.list.d/nodesource.list

sudo apt-get update && sudo apt-get install -y yarn
sudo npm install -y -g bower
sudo npm install -y -g ember-cli

cd ember
yarn -d #npm packages including dev
sudo bower install --allow-root
cd ../
sudo chown $USER -R ~/.config/*

# management

echo "Initialize git.  Before committing run these:"
git lfs track "*.custom" "*.tar.gz" "*.7z" "*.zip" "*.gzip"


#pipenv run ./manage.py import welt2000 --commit

## elevation data.  Make sure that you have 48 GB extra available for postgresql to grow!
## don't want to do the download and extracting each time. Importing takes a long time
#wget -i tiles.txt -P downloads -c --quiet
#unzip -j -d unzipped "downloads/*.zip"
##import to database.  Make sure disks are not saturated by other usage.  Will run while database is running
#raster2pgsql -a -e -s 4326 -t 100x100 /media/sf_srtmSkylinesCondor/*.hgt elevations | psql -d skylines > elevationsImportLog.txt
##if have this elevations dump, it might be faster, but I'm not sure it can run when the database is running:
#pg_restore -d skylines  --data-only  -t elevations /media/sf_srtm/srtmElevDump.custom


# production server
# sudo ufw enable
# systemctl status nginx

#pgadmin

