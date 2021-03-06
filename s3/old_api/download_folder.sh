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

  a_study_name=`create_study_name`

  a_testing_script="${CLOUDFLUPATH}/cloudflu-study-book --study-name=${a_study_name} | ${CLOUDFLUPATH}/cloudflu-upload-start ${case_dir}"

  process_script "${a_testing_script} | ${CLOUDFLUPATH}/cloudflu-upload-resume"
  
  an_output_dir=${case_dir}.out

  process_script "cloudflu-download --study-name=${a_study_name} --output-dir=${an_output_dir} --fresh --remove" ${an_old_api_number}
   
  a_diffing_dir=${an_output_dir}
  a_differences=`diff -r -q -i -x "*~" ${case_dir} ${a_diffing_dir}/${TEST_CLOUDFLU_CASE_DIR_NAME}`
  if [ "x${a_differences}" != "x" ]; then
      process_error "There are differences between '${case_dir}' and '${a_diffing_dir}':\n${a_differences}" ${an_old_api_number}
  else
      rm -rf ${an_output_dir}
  fi

  echo '----------------------------------- OK -----------------------------------------'
}


#-----------------------------------------------------------------------------------------

