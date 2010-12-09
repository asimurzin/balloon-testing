#!/bin/bash

#----------------------------------------------------------------------------------------
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
## Author : Andrey Simurzin
##


#----------------------------------------------------------------------------------------
if [ "${__LEVEL_0__}x" == 'x' ] ; then
    export __LEVEL_0__=../..
    export __LEVEL_1__=..
fi
source ${__LEVEL_1__}/common_s3.sh


#----------------------------------------------------------------------------------------
a_curdir_name=`python -c "import os; print os.path.basename( os.path.abspath( os.path.curdir ) )"`
TEST_CLOUDFLU_PATH_SCRIPT="${TEST_CLOUDFLU_PATH_SCRIPT}/${a_curdir_name}"


#----------------------------------------------------------------------------------------
run_old_api_script()
{
    for an_api in ${TEST_CLOUDFLU_LIST_OLD_API} ; do
	a_test_log_name=log.`basename ${0}`_${an_api}
	if [ -f ./${a_test_log_name} ]; then
	    a_script_name=${0}; 
	    a_user_log_name=`dirname ${0}`/${a_test_log_name}
	    echo "rm ${a_user_log_name} # before run '${a_script_name}' for '${an_api}' API"
	    continue
	else
	    a_function=${1}; ${a_function} ${an_api}
	fi
    done
}


#----------------------------------------------------------------------------------------
