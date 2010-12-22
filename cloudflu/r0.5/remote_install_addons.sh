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
##
## See http://sourceforge.net/apps/mediawiki/cloudflu
##
## Author : Alexey Petrov
##


#--------------------------------------------------------------------------------------
# This command sequence adjusts cloud instance ssh server configuration
set -x 
export DEBIAN_FRONTEND=noninteractive

# For Bug fixing
sudo apt-get update
sudo apt-get -y upgrade

# For NFS configuration
sudo apt-get install -y nfs-common portmap nfs-kernel-server 

# For CloudFlu installation external prerequisites
sudo apt-get -y install python-setuptools
sudo apt-get -y install python-all-dev

# To be able compile custom OpenFOAM solvers
sudo apt-get -y install g++

# To speed-up CloudFlu installation
sudo apt-get -y install python-paramiko # difficult to install by easy_install
sudo easy_install workerpool
sudo easy_install pexpect
sudo easy_install boto

# Just for lexury
sudo apt-get -y install mc


#--------------------------------------------------------------------------------------
