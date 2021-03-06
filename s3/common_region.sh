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
source ./s3.sh


#-----------------------------------------------------------------------------------------
create_study_in_location()
{
  a_s3location=${1}
  if [ "${a_s3location}x" == "x" ] ; then
      a_s3location=''
  fi
  a_list_filenames=`create_list_filenames_in_casedir`
  a_list_files=`create_list_case_files ${a_list_filenames}`
  
  a_study_name=`create_study_name`
  
  export __CLOUDFLU_S3_LOCATION__=${a_s3location}

  a_testing_script="cloudflu-study-book --study-name=${a_study_name} | cloudflu-upload-start ${a_list_files} | cloudflu-upload-resume"
  process_script "${a_testing_script}" ${a_s3location}
}


#-----------------------------------------------------------------------------------------
single_test()
{
  echo "********************************************************************************"
  echo $0
  
  a_script_name=`basename $0`
  an_output_dir=${case_dir}.out
  
  a_s3location=${1}
  echo "Testing ${a_s3location} "
  create_study_in_location ${a_s3location} && a_study_name=`get_result`
 
  a_list_filenames=`create_list_filenames_in_casedir`
  a_downloading_file=`python -c "temp='${a_list_filenames}';_list=temp.split(' '); print _list[ 2 ]" `

  process_script "cloudflu-download --study-name=${a_study_name} --located-files=${a_downloading_file} --output-dir=${an_output_dir} --fresh"
  if [ ! -e ${an_output_dir}/${a_downloading_file} ]; then
     process_error "There is no downloading file '${a_downloading_file}', in '${an_output_dir}' folder"
  fi
  
  process_script "cloudflu-study-rm ${a_study_name}"
  
  echo '----------------------------------- OK -----------------------------------------'
}


#-----------------------------------------------------------------------------------------

