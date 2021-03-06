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


#-----------------------------------------------------------------------------------------
source ./old_api.sh


#-----------------------------------------------------------------------------------------
test_hook()
{
  echo "********************************************************************************"
  echo $0 "'${1}'"
  
  a_script_name=`basename $0`
  an_old_api_number=${1}
  prepare_new_testing_data ${an_old_api_number} && a_study_name=`get_result`
  
  a_list_filenames=`create_list_filenames_in_casedir`
  a_list_files=`create_list_case_files ${a_list_filenames}`
  
  if [ ${an_old_api_number} \> "0.2" ] && [ ${an_old_api_number} != "dummy" ]; then
     a_list_file_to_rm=${a_list_filenames}
  else
     a_list_file_to_rm=`python -c "temp='${a_list_files}';_list=temp.split(' '); import os; print os.path.abspath(_list[ 1 ] ),' ',os.path.abspath(_list[ 0 ] )" `
  fi
  
  process_script "cloudflu-rm --study-name=${a_study_name} ${a_list_file_to_rm}" ${an_old_api_number}

  a_results=`cloudflu-ls ${a_study_name} 2>&1`
  an_allright="True"
  for a_file in ${a_list_file_to_rm}; do
      count_entrances=`echo ${a_results} | grep -c ${a_file}`
      if [ ${count_entrances} -ne 0 ]; then
          an_allright="False"
          a_not_deleted_file=${a_file}
          break
      fi
  done

  if [ "${an_allright}" = "False" ]; then
      process_error "The '${a_not_deleted_file}' file have not been removed from the S3" ${an_old_api_number}
  else
      cloudflu-study-rm ${a_study_name} > /dev/null 2>&1
      unregister_study ${TEST_CLOUDFLU_FILE_STUDIES_STARTS}_${an_old_api_number} ${a_study_name}
  fi

  echo '----------------------------------- OK -----------------------------------------'
}


#-----------------------------------------------------------------------------------------

