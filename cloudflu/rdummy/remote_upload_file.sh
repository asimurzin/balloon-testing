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
# This command sequence adjusts cloud instance user profile
set -x 

a_source="$1"

a_file_path=`echo ${a_source} | sed -e 's%^http:/%%g'`
a_folder=`dirname ${a_file_path}`
mkdir --parents ${a_folder}
wget ${a_source} --directory-prefix=${a_folder}

a_study_name=`basename ${a_file_path}`
source /mnt/.aws_credentialsrc

amazon_upload_start.py --study-name=${a_study_name} ${a_file_path} | amazon_upload_resume.py


#--------------------------------------------------------------------------------------
