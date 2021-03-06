#!/bin/bash
#
# Copyright 2017 Fausto Fusaro - Injenia Srl
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


# base packages and MySQL libs
apt-get install build-essential -y
apt-get install libpq-dev python-dev libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev libffi-dev liblzma-dev -y
apt-get install libmysqlclient-dev -y
export PATH=$PATH:/usr/local/mysql/bin
apt-get install mysql-client -y


# Python package manager
easy_install pip


# py virtualenv
pip install virtualenv


# prepare InTech environment
cd /usr/local/intech
virtualenv intech
source intech/bin/activate
pip install -r init/requirements.txt


# prepare Google Cloud SQL proxy
cd /usr/local
mkdir cloud_sql
cd cloud_sql
sudo wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64
sudo mv cloud_sql_proxy.linux.amd64 cloud_sql_proxy
sudo chmod +x cloud_sql_proxy
