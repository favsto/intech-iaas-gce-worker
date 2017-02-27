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

apt-get install libmysqlclient-dev

export PATH=$PATH:/usr/local/mysql/bin

easy_install pip

pip install virtualenv

cd /usr/local/intech

virtualenv intech

source intech/bin/activate

pip install -r init/requirements.txt
