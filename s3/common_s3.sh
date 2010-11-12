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


#------------------------------------------------------------------------------------------
if [ "${__LEVEL_0__}x" == 'x' ] ; then
    export __LEVEL_0__=..
fi
source ${__LEVEL_0__}/common.sh

a_case_dir_name='case'

a_list_old_api="dummy 0.1 0.2"

a_path_script='s3'

file_studies_starts=studies


#------------------------------------------------------------------------------------------
create_list_filenames_in_casedir()
{
  a_list_filenames=`(cd ${case_dir} && ls -I *~ )`
  echo $a_list_filenames
}


#-------------------------------------------------------------------------------------------
create_list_case_files()
{
  a_list_filenames=$*
  a_list_files=''
  for a_filename in ${a_list_filenames}
  do
     a_list_files+=" ${case_dir}/${a_filename}"
  done
  echo ${a_list_files}
}


#-----------------------------------------------------------------------------------------
remove_log_prepare_test_case()
{
  rm -f log.prepare_test_case
}


#-----------------------------------------------------------------------------------------
get_study()
{
  an_old_api_number=${1}
  echo `sed '$!d' ${file_studies_starts}_${an_old_api_number}`
}


#-----------------------------------------------------------------------------------------
rm_from_studies()
{
  a_file_studies=${1}
  a_study_name1=${2}
  
  cat ${a_file_studies} | grep -v -e ${a_study_name1} > ${a_file_studies}
}


#-----------------------------------------------------------------------------------------
study_name_starts_with()
{
  echo testing
}


#-----------------------------------------------------------------------------------------
create_study_name()
{
  a_begin_study_name=`study_name_starts_with`
  a_study_name=`python -c "import uuid; print '${a_begin_study_name}-%s' % uuid.uuid4()"`
  echo ${a_study_name}
}


#-----------------------------------------------------------------------------------------
calc_path_to_case_dir()
{
  a_curdir=`python -c "import os; print os.path.basename( os.path.abspath(os.path.curdir) )"`
  if [ "$a_curdir" == "old_api" ]; then
     echo "../${a_case_dir_name}" 
  fi
  if [ "$a_curdir" == "s3" ]; then
     echo "${a_case_dir_name}" 
  fi
}


#-----------------------------------------------------------------------------------------
calc_path_to_api()
{
  an_api_number=$1
  if [ x${an_api_number} != x ]; then
     echo "../../balloon/r${an_api_number}/"
  else
     echo ''
  fi
}


#-----------------------------------------------------------------------------------------
create_study()
{
  an_old_api_number=${1}
  a_path_to_api=`calc_path_to_api $an_old_api_number`
  a_list_filenames=`create_list_filenames_in_casedir`
  a_list_files=`create_list_case_files ${a_list_filenames}`
  a_study_name=`create_study_name`

  a_testing_script="${a_path_to_api}amazon_upload_start.py --debug --study-name=${a_study_name} ${a_list_files}"
  if [ "${a_path_to_api}x" == "x" ] ; then
      a_testing_script="balloon-study-book --debug --study-name=${a_study_name} | amazon_upload_start.py --debug ${a_list_files}"
  fi

  process_script "${a_testing_script} | ${a_path_to_api}amazon_upload_resume.py" 

  echo ${a_study_name} >> ${file_studies_starts}_${an_old_api_number}

  export a_result=${a_study_name}
}


#-----------------------------------------------------------------------------------------
prepare_testing_data()
{ 
  an_old_api_number=${1}

  if [ ! -f ${file_studies_starts}_${an_old_api_number} ]; then
     create_study ${an_old_api_number} && a_study_name=`get_result`
  else
     a_study_name=`get_study ${an_old_api_number}`
     if [ "x${a_study_name}" == "x" ]; then
        create_study ${an_old_api_number}
     fi
  fi

  export __PROCESS_SCRIPT_RESULT__=`get_study ${an_old_api_number}`
}
     

#-----------------------------------------------------------------------------------------
case_dir=`calc_path_to_case_dir`


#-----------------------------------------------------------------------------------------
