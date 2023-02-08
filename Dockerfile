FROM python:3.8-slim-buster
ENV DEBIAN_FRONTEND noninteractive
ENV TERM linux

# Airflow
ARG AIRFLOW_VERSION=2.5.1
ARG AIRFLOW_INSTALL_VERSION="==2.5.1"
ARG PYTHON_MAJOR_MINOR_VERSION=3.8
ARG AIRFLOW_CONSTRAINTS_REFERENCE="constraints-2.5.1"
ARG CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_MAJOR_MINOR_VERSION}.txt"
ARG AIRFLOW_USER_HOME=/usr/local/airflow
ARG AIRFLOW_DEPS=""
ARG PYTHON_DEPS=""
ENV AIRFLOW_HOME=${AIRFLOW_USER_HOME}

# Define en_US.
ENV LANGUAGE en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8
ENV LC_MESSAGES en_US.UTF-8

# GDAL
ARG GDAL_SOURCE_DIR=/usr/local/src/python-gdal
ENV GDAL_VERSION 3.0.4

RUN set -ex \
    && buildDeps=' \
        freetds-dev \
        libkrb5-dev \
        libsasl2-dev \
        libssl-dev \
        libffi-dev \
        libpq-dev \
        krb5-user \
        ldap-utils \
        libffi6 \
        libsasl2-2 \
        libsasl2-modules \
        libssl1.1 \
        locales  \
        lsb-release \
        sasl2-bin \
        sqlite3 \
        unixodbc \
    ' \
    && apt-get update -yqq \
    && apt-get upgrade -yqq \
    && apt-get install -yqq --no-install-recommends \
        $buildDeps \
        freetds-bin \
        build-essential \
        default-libmysqlclient-dev \
        apt-utils \
        curl \
        rsync \
        unixodbc-dev \
        netcat \
        git \
        # locales \
        \
        # Packages for GDAL
        automake libtool pkg-config libsqlite3-dev sqlite3 \
        wget \
        python3-dev \
        gdal-bin \
        libgdal-dev \
    && sed -i 's/^# en_US.UTF-8 UTF-8$/en_US.UTF-8 UTF-8/g' /etc/locale.gen \
    && locale-gen \
    && update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 \
    && useradd -ms /bin/bash -d ${AIRFLOW_USER_HOME} airflow \
    && pip install -U pip setuptools wheel \
    && pip install pytz \
    && pip install pyOpenSSL \
    && pip install ndg-httpsclient \
    && pip install pyasn1

# apt-get and system utilities
RUN apt-get update && apt-get install -y \
	curl apt-transport-https debconf-utils \
    && rm -rf /var/lib/apt/lists/*

# adding custom MS repository
RUN apt-get update && apt-get install -y gnupg2 \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    # Find some error when install msodbcsql17, removing apt/lists helped to avoid error
    && rm -rf /var/lib/apt/lists/* \
    && apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && echo "[SQL Server]\nDescription=Microsoft ODBC Driver 17 for SQL Server\nDriver=/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.2.so.0.1\nUsageCount=1\n" >> /etc/odbcinst.ini \
    && apt-get autoremove -y && apt-get clean all

# PROJ and GDAL download & extract
RUN wget "http://download.osgeo.org/proj/proj-6.0.0.tar.gz" \
    && tar -xzf "proj-6.0.0.tar.gz" \
    && mv proj-6.0.0 proj \
    && echo "#!/bin/sh" > proj/autogen.sh \
    && chmod +x proj/autogen.sh \
    && cd proj \
    && ./autogen.sh \
    && CXXFLAGS='-DPROJ_RENAME_SYMBOLS' CFLAGS='-DPROJ_RENAME_SYMBOLS' ./configure --disable-static --prefix=/usr/local \
    && make -j"$(nproc)" \
    && make -j"$(nproc)" install \
    # Rename the library to libinternalproj
    && mv /usr/local/lib/libproj.so.15.0.0 /usr/local/lib/libinternalproj.so.15.0.0 \
    && rm /usr/local/lib/libproj.so* \
    && rm /usr/local/lib/libproj.la \
    && ln -s libinternalproj.so.15.0.0 /usr/local/lib/libinternalproj.so.15 \
    && ln -s libinternalproj.so.15.0.0 /usr/local/lib/libinternalproj.so \
    \
    # GDAL
    && mkdir -p "${GDAL_SOURCE_DIR}" \
    && cd "${GDAL_SOURCE_DIR}" \
    && wget "http://download.osgeo.org/gdal/${GDAL_VERSION}/gdal-${GDAL_VERSION}.tar.gz" \
    && tar -xvf "gdal-${GDAL_VERSION}.tar.gz"

# GDAL install
RUN pip install --upgrade pip \
    && pip install setuptools==57.5.0 \
    && cd "${GDAL_SOURCE_DIR}" \
    && cd gdal-${GDAL_VERSION} \
    && export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH \
    && ./configure \
        --with-python \
        --with-curl \
        --without-libtool \
        --with-proj=/usr/local \
    && make -j"$(nproc)" \
    && make install \
    && ldconfig

# Getting GDAL pip package
RUN pip install GDAL==${GDAL_VERSION} \
    && cd /usr/local

################ Install packages ##############
ADD ./requirements_torch.txt /usr/src/requirements_torch.txt
RUN pip install -r /usr/src/requirements_torch.txt
ADD ./requirements.txt /usr/src/requirements.txt
RUN pip install -r /usr/src/requirements.txt
RUN  pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}" \
&& pip install apache-airflow[crypto,celery,postgres,hive,jdbc,mysql,ssh${AIRFLOW_DEPS:+,}${AIRFLOW_DEPS}]==${AIRFLOW_VERSION} \
&& pip install "apache-airflow[postgres,crypto,jdbc,mysql,ssh]==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}" \
&& pip install 'redis==3.2'


################ Install  encryption ##############
RUN apt-get update && \
    apt-get install -y \
        wget gnupg gnupg2 gnupg1 unzip psmisc

################ Install chrome ##############
ARG CHROME_VERSION="google-chrome-stable"
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
&& echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
&& apt-get update -qqy \
&& apt-get -qqy install \
${CHROME_VERSION:-google-chrome-stable} \
&& rm /etc/apt/sources.list.d/google-chrome.list \
&& rm -rf /var/lib/apt/lists/* /var/cache/apt/*

############### Install chrome driver #########
# Получим последнюю стабильную версию драйвера chrome:
RUN CHROME_DRIVER_VERSION=`curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE` \
# Установим Chrome driver:
&& wget -N https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip -P ~/ \
&& unzip ~/chromedriver_linux64.zip -d ~/ \
&& rm ~/chromedriver_linux64.zip \
&& mv -f ~/chromedriver /usr/local/bin/chromedriver \
&& chown root:root /usr/local/bin/chromedriver \
&& chmod 0755 /usr/local/bin/chromedriver


COPY script/entrypoint.sh /entrypoint.sh
COPY config/airflow.cfg ${AIRFLOW_USER_HOME}/airflow.cfg

############### Create dags #########
RUN mkdir /usr/local/airflow/dags \
    && cd /usr/local/airflow/dags

############### Install nano, ping, top #########
RUN apt-get update \
    && apt-get -y install nano \
    && apt-get -y install iputils-ping \
    && apt-get -y install procps

RUN chown -R airflow: ${AIRFLOW_USER_HOME}
EXPOSE 8080 5555 8793
USER airflow
WORKDIR ${AIRFLOW_USER_HOME}

############### Launch airflow ################
ENTRYPOINT ["/entrypoint.sh"]
CMD ["webserver"]