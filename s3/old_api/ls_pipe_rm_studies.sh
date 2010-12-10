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
source ./old_api.sh


#-----------------------------------------------------------------------------------------
test_hook()
{
  echo "********************************************************************************"
  echo $0 "'${1}'"

  a_script_name=`basename $0`
  an_old_api_number=${1}
  prepare_testing_data ${an_old_api_number} && a_study_name1=`get_result`
  prepare_new_testing_data ${an_old_api_number} && a_study_name2=`get_result`

  process_script "cloudflu-ls | grep -e ${a_study_name1} -e ${a_study_name2} | xargs cloudflu-study-rm" ${an_old_api_number}

  a_results=`cloudflu-ls 2>&1`
  count_entrances=`echo ${a_results} | grep -c -e ${a_study_name1} -e ${a_study_name2}`

  if [ ${count_entrances} -ne 0 ]; then
      process_error "There are study named ${a_study_name1} or ${a_study_name2} (may be both) in the S3" ${an_old_api_number}
  else
      unregister_study ${TEST_CLOUDFLU_FILE_STUDIES_STARTS}_${an_old_api_number} ${a_study_name1}
      unregister_study ${TEST_CLOUDFLU_FILE_STUDIES_STARTS}_${an_old_api_number} ${a_study_name2}
  fi
  
  echo '----------------------------------- OK -----------------------------------------'
}


#-----------------------------------------------------------------------------------------

