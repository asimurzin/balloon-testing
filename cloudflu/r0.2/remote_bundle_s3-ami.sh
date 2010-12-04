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

source /mnt/.aws_credentialsrc

sudo apt-get -y install ec2-ami-tools
sudo apt-get -y install ec2-api-tools

codename=lucid
release=10.04
tag=server

if [ $(uname -m) = 'x86_64' ]; then
  arch=x86_64
else
  arch=i386
fi

now=$(date +%Y%m%d-%H%M)
prefix=ubuntu-${release}-${codename}-${arch}-${tag}-${now}
bucket=bucket-${prefix}

sudo -E ec2-bundle-vol -r ${arch} --destination /mnt --prefix ${prefix} --user ${AWS_USER_ID} --privatekey ${EC2_PRIVATE_KEY} --cert ${EC2_CERT} --size 10240 --exclude /mnt,/root/.ssh

ec2-upload-bundle --bucket ${bucket} --manifest /mnt/${prefix}.manifest.xml --access-key ${AWS_ACCESS_KEY_ID} --secret-key ${AWS_SECRET_ACCESS_KEY}

ec2-register --private-key ${EC2_PRIVATE_KEY} --cert ${EC2_CERT} ${bucket}/${prefix}.manifest.xml --name ${prefix}


#--------------------------------------------------------------------------------------
