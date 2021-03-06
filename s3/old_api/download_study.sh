#!/bin/bash

#-----------------------------------------------------------------------------------------
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
  prepare_testing_data ${an_old_api_number} && a_study_name=`get_result`

  an_output_dir=${case_dir}.out
  an_abspath_files=`python -c "import os; print os.path.abspath(\"${case_dir}\")"`

  process_script "cloudflu-download --study-name=${a_study_name} --output-dir=${an_output_dir} --fresh" ${an_old_api_number}

  
  if [ ${an_old_api_number} \> "0.2" ] && [ ${an_old_api_number} != "dummy" ]; then
     an_out_files_dir=${an_output_dir}
  else
     an_out_files_dir=${an_output_dir}/${an_abspath_files}/${a_file}
  fi
  
  a_list_filenames=`create_list_filenames_in_casedir`
  an_allright="True"
  for a_file in ${a_list_filenames} ; do
      if [ ! -e ${an_out_files_dir} ]; then
          an_allright="False"
          a_bad_file=${a_file}
          break
      fi
  done

  if [ "${an_allright}" = "False" ]; then
      process_error "There is no '${a_bad_file}' file, in output folder '${an_out_files_dir}'" ${an_old_api_number}
  fi
  rm -rf ${an_output_dir}
  echo '----------------------------------- OK -----------------------------------------'
}


#-----------------------------------------------------------------------------------------



