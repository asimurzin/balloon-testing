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
  prepare_testing_data ${an_old_api_number} && a_study_name=`get_result`

  process_script "cloudflu-ls ${a_study_name}" ${an_old_api_number} && a_result=`get_result`

  an_allright="True"
  a_list_filenames=`create_list_filenames_in_casedir`
  for a_filename in ${a_list_filenames}; do
      count_entrances=`echo ${a_result} | grep -c ${a_filename}`
      if [ ${count_entrances} -eq 0 ]; then
          an_allright="False"
          a_not_exists_file=${a_filename}
          break
      fi
  done 

  if [ "${an_allright}" = "False" ]; then
      process_error "There is no '${a_not_exists_file}' file in the S3" ${an_old_api_number}
  fi

  echo '----------------------------------- OK -----------------------------------------'
}


#-----------------------------------------------------------------------------------------


