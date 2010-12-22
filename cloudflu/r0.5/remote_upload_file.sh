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
# This command sequence adjusts cloud instance user profile
set -x 
export DEBIAN_FRONTEND=noninteractive

a_source="$1"
an_is_get_request=`echo ${a_source} | grep -E "?" > /dev/null && echo x`
if [ "${an_is_get_request}" == "x" ] ; then
    a_file_path=`echo ${a_source} | sed -e 's%^http:/\([^?]*\).*%\1%g'`
else
    a_file_path=`echo ${a_source} | sed -e 's%^http:/%%g'`
fi

a_folder=`dirname ${a_file_path}`
mkdir --parents ${a_folder}

if [ "${an_is_get_request}" == "x" ] ; then
    curl "${a_source}" > ${a_file_path}
else
    wget ${a_source} --directory-prefix=${a_folder}
fi

source /tmp/.aws_credentialsrc

a_study_name=`basename ${a_file_path}`

cloudflu-study-book --study-name=${a_study_name} | amazon_upload_start.py ${a_file_path} | amazon_upload_resume.py


#--------------------------------------------------------------------------------------
