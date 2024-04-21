#!/usr/bin/env bash

# The output of all these installation steps is noisy. With this utility
# the progress report is nice and concise.
function install {
    echo installing $1
    shift
    apt-get -y install "$@" >/dev/null 2>&1
}

# Add repositories

if ! command -v psql; then
	sudo add-apt-repository "deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main"
	wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
fi
	
# Update/Install packages

sudo apt-get -y update

if ! command -v psql; then	
	install 'PostgreSQL' postgresql-9.6 libpq-dev
	cp /vagrant/conf/vagrant/pg_hba.conf /etc/postgresql/9.6/main/
	/etc/init.d/postgresql reload
fi

install 'development tools' \
	build-essential \
	python-dev libffi-dev libssl-dev \
	libxml2 libxml2-dev libxslt-dev \
	libcurl4-openssl-dev libjpeg-dev \
	xz-utils uuid-dev \
	zlib1g zlib1g-dev \
	sshpass \
	git	
	
install 'Memcached'	memcached

install 'Python packages' \
	python-pycurl \
	python-lxml \
	python-pip \
	libxapian-dev python-xapian \
	python-virtualenv \
	python-xapian

# Create virtualenv	
	
HOME='/home/vagrant'
VENV_HOME="$HOME/.venv"	
VENV="$VENV_HOME/sklad51"
VENV_USENAME='vagrant'
PYTHON_PATH=/usr/local/lib/python2.7.13/bin/python

echo "make virtualenv $VENV"

sudo -u $VENV_USENAME rm -rf $VENV_HOME
sudo -u $VENV_USENAME mkdir $VENV_HOME
sudo -u $VENV_USENAME virtualenv --python=$PYTHON_PATH $VENV
sudo -u $VENV_USENAME $VENV/bin/pip install --upgrade pip
sudo -u $VENV_USENAME $VENV/bin/pip install --no-cache-dir --no-deps -r /vagrant/requirements.txt
sudo -u $VENV_USENAME $VENV/bin/pip install --no-cache-dir --no-deps -r /vagrant/requirements-dev.txt

sudo -u vagrant cp /vagrant/mir_mebeli/local_settings.py.prod-example /vagrant/mir_mebeli/local_settings.py

# Install xapian from source

XAPIAN_VERSION="1.2.21"
XAPIAN_LIB=/usr/local/lib/xapian/
XAPIAN_PYTHON_LIB=$VENV/lib/python2.7/site-packages/

cd /home/ubuntu/ 
wget https://oligarchy.co.uk/xapian/${XAPIAN_VERSION}/xapian-core-${XAPIAN_VERSION}.tar.xz
tar -xvf xapian-core-${XAPIAN_VERSION}.tar.xz
cd xapian-core-${XAPIAN_VERSION}
./configure
make
make install

cd /home/ubuntu/
wget https://oligarchy.co.uk/xapian/${XAPIAN_VERSION}/xapian-bindings-${XAPIAN_VERSION}.tar.xz
tar -xvf xapian-bindings-${XAPIAN_VERSION}.tar.xz
cd xapian-bindings-${XAPIAN_VERSION}
./configure --prefix=$XAPIAN_LIB PYTHON_LIB=$XAPIAN_PYTHON_LIB --with-python  --without-ruby --without-php --without-tcl
make
make install
#rm -rf xapian-*

# Patch Djapian

# Create database if does not exist

if ! [[ $(psql -U postgres -lqt | cut -d \| -f 1 | grep new_sklad51) ]]; then

  echo 'download database dump'
  
  #SKLAD51_HOST=194.58.122.224
  #echo "enter password from host $SKLAD51_HOST: "
  #read SKLAD51_PASS
  #echo $SKLAD51_PASS
  #cd /vagrant
  #sudo -u vagrant sshpass -p "OvqE!tciq21iPG" ssh -o StrictHostKeyChecking=No -i YourPublicKey.pem root@$SKLAD51_HOST uptime
  #sudo -u vagrant sshpass -p "OvqE!tciq21iPG" ssh root@$SKLAD51_HOST 'cat /opt/new_sklad51/backup/2017.06.07.021319.sql' > /vagrant/2017.06.07.021319.sql

  echo 'create database'
  
  sudo -u postgres mkdir /var/lib/postgresql/9.6/main/pg_tblspc/sklad51
  
  psql -U postgres <<TSQL
  \x
  CREATE USER new_sklad51 WITH password 'new_sklad51';
  \x
  CREATE TABLESPACE sklad51
	OWNER new_sklad51
	LOCATION '/var/lib/postgresql/9.6/main/pg_tblspc/sklad51';
  \x
  CREATE DATABASE new_sklad51
  WITH OWNER = new_sklad51
       ENCODING = 'UTF8'
       TABLESPACE = sklad51
       CONNECTION LIMIT = -1;
TSQL

  psql -U postgres -d new_sklad51 < /vagrant/2017.06.07.021319.sql
  #rm /vagrant/2017.06.07.021319.sql
fi