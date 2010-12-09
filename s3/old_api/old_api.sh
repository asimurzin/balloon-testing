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


#-----------------------------------------------------------------------------------------
a_curdir_name=`python -c "import os; print os.path.basename( os.path.abspath( os.path.curdir ) )"`
TEST_CLOUDFLU_PATH_SCRIPT="${TEST_CLOUDFLU_PATH_SCRIPT}/${a_curdir_name}"


#----------------------------------------------------------------------------------------
calc_path_to_api()
{
  an_api_number=$1
  if [ x${an_api_number} != x ]; then
     echo "../../cloudflu/r${an_api_number}/cloudflu/amazon/apps/"
  else
     echo ''
  fi
}


#----------------------------------------------------------------------------------------
create_old_api_study()
{
  an_old_api_number=${1}
  a_path_to_api=`calc_path_to_api $an_old_api_number`
  a_list_filenames=`create_list_filenames_in_casedir`
  a_list_files=`create_list_case_files ${a_list_filenames}`
  a_study_name=`create_study_name`

  a_testing_script="${a_path_to_api}study_book.py --study-name=${a_study_name} | ${a_path_to_api}upload_start.py ${a_list_files}"

  process_script "${a_testing_script} | ${a_path_to_api}upload_resume.py" ${an_old_api_number}

  echo ${a_study_name} >> ${TEST_CLOUDFLU_FILE_STUDIES_STARTS}_${an_old_api_number}

  export a_result=${a_study_name}
}


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
