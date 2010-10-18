#!/bin/bash



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

