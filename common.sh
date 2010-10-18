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
prepare_testing_data()
{
if [ ! -f 'log.prepare_test_case'  ]; then
   echo '---------------------------- Preparing test data -------------------------------'
   `amazon_upload_start.py --study-name=TEST_STUDY ./case/blockMeshDict ./case/boundary ./case/faces ./case/neighbour $* > log.prepare_test_case 2>&1`
   if [ $? -ne 0 ]; then
      echo ' An error have appeared during execution of amazon_upload_start.py'
      cat log.prepare_test_case
      rm log.prepare_test_case
   else
      amazon_upload_resume.py --study-name=TEST_STUDY $* > log.prepare_test_case 2>&1
      if [ $? -ne 0 ]; then
         echo ' An error have appeared during execution of amazon_upload_resume.py'
         cat log.prepare_test_case
         rm log.prepare_test_case
      else
         echo '----------------------------------- OK -----------------------------------------'
         echo ''
      fi
   fi   
fi
}


#-----------------------------------------------------------------------------------------
