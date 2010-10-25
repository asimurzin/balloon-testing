#!/usr/bin/env bash

#--------------------------------------------------------------------------------------
## Copyright 2010 Alexey Petrov
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.


#--------------------------------------------------------------------------------------
# This command sequence adjusts cloud instance ssh server configuration
set -x 

sudo apt-get -y install python-software-properties
sudo add-apt-repository ppa:cae-team/ppa
sudo apt-get update

if [ $(uname -m) = 'x86_64' ]; then
  arch=amd64
else
  arch=i386
fi

a_source=http://garr.dl.sourceforge.net/project/foam/foam/1.7.1/openfoam171_0-1_${arch}.deb
wget ${a_source}

a_file_path=`echo ${a_source} | sed -e 's%^http:/%%g'`
a_file_path=./`basename ${a_file_path}`

sudo dpkg --install ${a_file_path}
sudo apt-get -y -f install


#--------------------------------------------------------------------------------------
