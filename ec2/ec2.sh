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

file_reservations_starts='reservations'

count_instances=1

instance_type="m1.small"

image_id="ami-0440b46d"


#----------------------------------------------------------------------------------------
rm_from_file_reservations()
{
  a_count_instances=$1
  an_instance_type=$2
  an_image_id=$3
  a_reservation=$4
  a_file_reservations=${file_reservations_starts}_${a_count_instances}_${an_instance_type}_${an_image_id}
  cat ${a_file_reservations} | grep -v -e ${a_reservation} > ${a_file_reservations}
}


#----------------------------------------------------------------------------------------
create_reservation()
{
     a_count_instances=$1
     an_instance_type=$2
     an_image_id=$3
     echo 'Prepare reservation...' >&2
          
     a_testing_script="amazon_reservation_run.py --instance-type=${an_instance_type} --image-id=${an_image_id} --min-count=${a_count_instances} --debug"
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
        echo ${a_reservation} >> ${file_reservations_starts}_${a_count_instances}_${an_instance_type}_${an_image_id}
     fi
}
        

#----------------------------------------------------------------------------------------
get_reservation()
{  
   a_file_reservations=$1
   echo `sed '$!d' ${a_file_reservations}`
}


#----------------------------------------------------------------------------------------
prepare_testing_reservation()
{
  a_count_instances=$1
  an_instance_type=$2
  an_image_id=$3
  echo ${a_count_instances} ${an_instance_type} ${an_image_id} >> log.tmp
  if [ ! -f reservations_${a_count_instances}_${an_instance_type}_${an_image_id} ]; then
     echo ${a_count_instances} > log.tmp
     dummy=`create_reservation ${a_count_instances} ${an_instance_type} ${an_image_id}`
  else
     a_reservation=`get_reservation ${file_reservations_starts}_${a_count_instances}_${an_instance_type}_${an_image_id}`
     if [ "x${a_reservation}" == "x" ]; then
        dummy=`create_reservation ${a_count_instances} ${an_instance_type} ${an_image_id}`
     fi
  fi
  echo `get_reservation ${file_reservations_starts}_${a_count_instances}_${an_instance_type}_${an_image_id}`
}

