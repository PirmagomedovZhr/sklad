PYTHON_DIR=/usr/local/lib/python2.7.13/

if [ -d "$PYTHON_DIR" ]; then
	exit 0
fi

sudo apt-get -y update

sudo apt-get install -y \
	build-essential \
	python-dev \
	zlib1g \
	zlib1g-dev \
	libffi-dev \
	libssl-dev \
	libxml2 \
	libxml2-dev \
	libxslt-dev \
	libcurl4-openssl-dev \
	libjpeg-dev \
	xz-utils \
	uuid-dev \
	autotools-dev \
	blt-dev \
	bzip2 \
	dpkg-dev \
	g++-multilib \
	gcc-multilib \
	libbluetooth-dev \
	libbz2-dev \
	libexpat1-dev \
	libffi-dev \
	libffi6 \
	libffi6-dbg \
	libgdbm-dev \
	libgpm2 \
	libncursesw5-dev \
	libreadline-dev \
	libsqlite3-dev \
	libssl-dev \
	libtinfo-dev \
	mime-support \
	net-tools \
	netbase \
	python-crypto \
	python-mox3 \
	python-pil \
	python-ply \
	quilt \
	tk-dev
	
sudo apt-get build-dep -y python2.7

cd /home/ubuntu/	
wget https://www.python.org/ftp/python/2.7.13/Python-2.7.13.tgz
tar xfz Python-2.7.13.tgz
cd Python-2.7.13/
sudo ./configure --prefix $PYTHON_DIR --enable-ipv6 --enable-unicode=ucs4
sudo make
sudo make install