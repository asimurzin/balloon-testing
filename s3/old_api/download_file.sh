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
   prepare_testing_data ${an_old_api_number} && a_study_name=`get_result`

   an_output_dir=${TEST_CLOUDFLU_CASE_DIR_NAME}.out
   a_list_filenames=`create_list_filenames_in_casedir`
   a_filename=`python -c "temp='${a_list_filenames}';_list=temp.split(' '); print _list[ 2 ]" `
   
   if [ ${an_old_api_number} \> "0.2" ] && [ ${an_old_api_number} != "dummy" ]; then
      a_downloading_file=${a_filename}
   else
       a_downloading_file=`python -c "import os; print os.path.abspath(\"${case_dir}/${a_filename}\")"`
   fi
   
   process_script "cloudflu-download --study-name=${a_study_name} --located-files=${a_downloading_file} --output-dir=${an_output_dir} --fresh" ${an_old_api_number}
   if [ ! -e ${an_output_dir}/${a_downloading_file} ]; then
       process_error "There is no downloading file '${a_downloading_file}', in '${an_output_dir}' folder" ${an_old_api_number}
   fi

   echo '----------------------------------- OK -----------------------------------------'
}


#-----------------------------------------------------------------------------------------

