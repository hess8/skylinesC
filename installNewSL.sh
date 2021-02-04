#on Ubuntu 18.04


sudo apt --fix-broken install
sudo apt upgrade
sudo dpkg --configure -a
sudo apt install software-properties-common
sudo apt install python3.9 #2.7 was already on machine

cat >> ~/.profile << EOF
export POSTGIS_GDAL_ENABLED_DRIVERS=GTiff
export POSTGIS_ENABLE_OUTDB_RASTERS=1
EOF

#pip and pipenv are already installed
cd skylinesNew
pipenv shell
exit
#note Pipfile has Python 2.7 requirement, so no separate install for that.
sudo pipenv install --verbose --dev | tee pipenvInstall.log #removed dev header o

# If get error E: Could not get lock /var/lib/dpkg/lock-frontend - open (11: Resource temporarily unavailable) [duplicate]

# sudo killall apt apt-get
# sudo rm /var/lib/apt/lists/lock
# sudo rm /var/cache/apt/archives/lock
# sudo rm /var/lib/dpkg/lock*
# sudo dpkg --configure -a

#
#sudo apt-get --purge remove postgresql\* if need to get rid of it
pipenv shell
sudo apt install -y postgresql-10