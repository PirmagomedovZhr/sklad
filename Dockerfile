FROM python:2
ENV PYTHONUNBUFFERED 1

ENV NGINX_VERSION="1.12.0" \
    NGINX_OPTS="--with-http_ssl_module \
                --with-http_gzip_static_module \
                --prefix=/usr/share/nginx \
                --sbin-path=/usr/sbin/nginx \
                --conf-path=/etc/nginx/nginx.conf \
                --pid-path=/var/run/nginx.pid \
                --http-log-path=/var/log/nginx/access.log \
                --error-log-path=/var/log/nginx/error.log \
                --user=www-data \
                --group=www-data \
                --add-module=/tmp/modules/nginx_requestid-master"

ENV XAPIAN_VERSION="1.2.21"

COPY requirements.txt /opt/app/requirements.txt

RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get  install -y --no-install-recommends apt-utils \
    libxml2 \
    xz-utils \
    uuid-dev \
    python-xapian \
    memcached \
    supervisor \
    cron \
    make && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \

    pip install --upgrade pip && \
    pip install --no-cache-dir --no-deps -r /opt/app/requirements.txt && \

    # Download additional nginx modules
    mkdir -p /tmp/modules && \
    cd /tmp/modules && \
    wget -O nginx-requestid.tar.gz https://github.com/hhru/nginx_requestid/archive/master.tar.gz && \
    tar xvzf nginx-requestid.tar.gz && \
    # Download and compile nginx
    cd /tmp && \
    wget http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz && \
    tar xzvf nginx-${NGINX_VERSION}.tar.gz && \
    cd nginx-${NGINX_VERSION} && \
    ./configure ${NGINX_OPTS} && \
    make && \
    make install && \

    # Delete build dependencies after use
    cd /tmp \

    && rm -rf \
        modules \
        nginx-${NGINX_VERSION} \
        nginx-${NGINX_VERSION}.tar.gz \
        /var/cache/apt/* \
        /root/.cache \

    # Patch Djapian
    && rm /usr/local/lib/python2.7/site-packages/djapian/resultset.py

COPY conf/djapian-patch/resultset.py /usr/local/lib/python2.7/site-packages/djapian/resultset.py

# Install xapian from source
RUN cd /tmp && \
    curl -O https://oligarchy.co.uk/xapian/${XAPIAN_VERSION}/xapian-core-${XAPIAN_VERSION}.tar.xz && \
    tar -xvf xapian-core-${XAPIAN_VERSION}.tar.xz && \
    cd xapian-core-${XAPIAN_VERSION} && \
    ./configure && \
    make && \
    make install && \
    cd /tmp && \
    curl -O https://oligarchy.co.uk/xapian/${XAPIAN_VERSION}/xapian-bindings-${XAPIAN_VERSION}.tar.xz && \
    tar -xvf xapian-bindings-${XAPIAN_VERSION}.tar.xz && \
    cd xapian-bindings-${XAPIAN_VERSION} && \
    ./configure --with-python && \
    make && \
    make install && \
    rm -rf xapian-*

#ADD . /opt/app
#VOLUME ["/opt/app/public_html"]
WORKDIR /opt/app

# Nginx config
RUN rm -v /etc/nginx/nginx.conf
ADD /conf/nginx.conf /etc/nginx/

# Add crontab file in the cron directory
ADD /conf/crontab /etc/cron.d/sklad-cron

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/sklad-cron

EXPOSE 80


CMD ["conf/docker/entrypoint_prod.sh"]
