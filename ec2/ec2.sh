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
#----------------------------------------------------------------------------------------
#source common function
. ../common.sh
a_path_script='ec2'

a_file_reservations='reservations'

an_instance_type="m1.small"

an_image_id="ami-9c5aaff5"


#----------------------------------------------------------------------------------------
create_reservation()
{
     a_count_instances=$1
     echo "1111" $a_count_instances >> log.tmp
     echo 'Prepare reservation...'
     a_testing_script="amazon_reservation_run.py --instance-type=${an_instance_type} --image-id=${an_image_id} --min-count=${a_count_instances} "
     a_reservation=`${a_testing_script} 2>log.create_reservation`
     if [ $? -ne 0 ]; then
        echo ''
        echo ''
        echo "--------------------------------------------------------------------------------"
        echo "An error have appeared during execution of"
        echo "${a_testing_script}" 
        echo "--------------------------------------------------------------------------------"
        echo ''
        echo ''
        cat log.create_reservation
        rm log.create_reservation
        exit -1
     else
        echo ${a_reservation} >> ${a_file_reservations}_${a_count_instances}
     fi
}
        

#----------------------------------------------------------------------------------------
get_reservation()
{  
   a_count_instances=$1
   echo `sed '$!d' reservations_${a_count_instances}`
}


#----------------------------------------------------------------------------------------
prepare_testing_reservation()
{
  a_count_instances=$1 
  if [ "x${a_count_instances}" == "x" ]; then
     a_count_instances='1'
  fi 
  if [ ! -f reservations_${a_count_instances} ]; then
     echo ${a_count_instances} > log.tmp
     `create_reservation ${a_count_instances}`
  else
     a_reservation=`get_reservation ${a_count_instances}`
     if [ "x${a_reservation}" == "x" ]; then
        `create_reservation ${a_count_instances}`
     fi
  fi
  echo `get_reservation ${a_count_instances}`
}

