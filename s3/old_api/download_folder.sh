#!/bin/bash

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
## Author : Andrey Simurzin
##


#-----------------------------------------------------------------------------------------
cd ${0%/*} || exit 1 # run from this directory

if [ "${__LEVEL_0__}x" == 'x' ] ; then
    export __LEVEL_0__=../../..
    export __LEVEL_1__=../..
    export __LEVEL_2__=..
fi

source ${__LEVEL_2__}/old_api.sh


#-----------------------------------------------------------------------------------------
test_hook()
{
  echo "********************************************************************************"
  echo $0 "'${1}'"

  a_script_name=`basename $0`
  an_old_api_number=${1}
  a_path_to_api=`calc_path_to_api $an_old_api_number`
  
  a_study_name=`create_study_name`

  a_testing_script="${a_path_to_api}study_book.py --study-name=${a_study_name} | ${a_path_to_api}upload_start.py ${case_dir}"

  process_script "${a_testing_script} | ${a_path_to_api}upload_resume.py"
  
  an_output_dir=${case_dir}.out

  process_script "cloudflu-download --study-name=${a_study_name} --output-dir=${an_output_dir} --fresh" ${an_old_api_number}
   
  a_diffing_dir=${an_output_dir}
  a_differences=`diff -r -q -i -x "*~" ${case_dir} ${a_diffing_dir}/${TEST_CLOUDFLU_CASE_DIR_NAME}`
  if [ "x${a_differences}" != "x" ]; then
      process_error "There are differences between '${case_dir}' and '${a_diffing_dir}':\n${a_differences}" ${an_old_api_number}
  else
      unregister_study ${TEST_CLOUDFLU_FILE_STUDIES_STARTS} ${a_study_name}
      rm -rf ${an_output_dir}
  fi

  echo '----------------------------------- OK -----------------------------------------'
}


#-----------------------------------------------------------------------------------------

