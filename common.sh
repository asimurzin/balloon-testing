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
case_dir='case'


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
  rm log.prepare_test_case
}


#-----------------------------------------------------------------------------------------
get_studies()
{
  cat studies
}


#-----------------------------------------------------------------------------------------
rm_studies()
{
  rm studies
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
prepare_testing_data()
{ 
  a_list_filenames=`create_list_filenames_in_casedir`

  a_list_files=`create_list_case_files ${a_list_filenames}`
  
  if [ ! -f 'log.prepare_test_case'  ]; then
     a_study_name=`create_study_name`
     `amazon_upload_start.py --study-name=${a_study_name} ${a_list_files} > log.prepare_test_case 2>&1`
     if [ -f studies ]; then
        echo ${a_study_name} >> studies
     else
        echo ${a_study_name} > studies
     fi 
     if [ $? -ne 0 ]; then
        echo ' An error have appeared during execution of amazon_upload_start.py'
        cat log.prepare_test_case
        rm log.prepare_test_case
        exit -1
     else
        `amazon_upload_resume.py --study-name=${a_study_name} >>log.prepare_test_case 2>&1`
        if [ $? -ne 0 ]; then
           echo ' An error have appeared during execution of amazon_upload_resume.py'
           cat log.prepare_test_case
           rm log.prepare_test_case
           exit -1
        fi
      fi
   else
      a_study_name=`sed '$!d' studies`
fi
echo ${a_study_name}
}


#-----------------------------------------------------------------------------------------
