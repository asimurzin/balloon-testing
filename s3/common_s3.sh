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

TEST_CLOUDFLU_CASE_DIR_NAME='case'

TEST_CLOUDFLU_LIST_OLD_API="0.5"

TEST_CLOUDFLU_PATH_SCRIPT='s3'

TEST_CLOUDFLU_FILE_STUDIES_STARTS=studies

TEST_CLOUDFLU_S3LOCATIONS="ap-southeast-1 EU us-west-1"


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
  for a_filename in ${a_list_filenames} ; do
     a_list_files+=" ${case_dir}/${a_filename}"
  done

  echo ${a_list_files}
}


#-----------------------------------------------------------------------------------------
get_study()
{
  echo `sed '$!d' ${TEST_CLOUDFLU_FILE_STUDIES_STARTS}`
}


#-----------------------------------------------------------------------------------------
unregister_study()
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

  if [ "$a_curdir" == "s3" ]; then
     echo "${TEST_CLOUDFLU_CASE_DIR_NAME}" 
  else
       echo "../${TEST_CLOUDFLU_CASE_DIR_NAME}" 
  fi
}


#-----------------------------------------------------------------------------------------
create_study()
{
  a_list_filenames=`create_list_filenames_in_casedir`
  a_list_files=`create_list_case_files ${a_list_filenames}`
  a_study_name=`create_study_name`

  a_testing_script="cloudflu-study-book --study-name=${a_study_name} | cloudflu-upload-start ${a_list_files}"

  process_script "${a_testing_script} | ${a_path_to_api}cloudflu-upload-resume"

  echo ${a_study_name} >> ${TEST_CLOUDFLU_FILE_STUDIES_STARTS}

  export a_result=${a_study_name}
}


#-----------------------------------------------------------------------------------------
prepare_new_testing_data()
{ 
  an_old_api_number=${1}
  
  if [ "x${an_old_api_number}" == "x" ]; then
     create_study
  else
     create_old_api_study ${an_old_api_number} 
  fi
}
     

#-----------------------------------------------------------------------------------------
prepare_testing_data()
{ 
  an_old_api_number=${1}

  if [ ! -f ${TEST_CLOUDFLU_FILE_STUDIES_STARTS} ]; then
     prepare_new_testing_data ${an_old_api_number}
  else
     a_study_name=`get_study ${an_old_api_number}`
     if [ "x${a_study_name}" == "x" ]; then
        prepare_new_testing_data ${an_old_api_number}
     fi
  fi

  export __PROCESS_SCRIPT_RESULT__=`get_study`
}
     

#-----------------------------------------------------------------------------------------
case_dir=`calc_path_to_case_dir`


#-----------------------------------------------------------------------------------------
