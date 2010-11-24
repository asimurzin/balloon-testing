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
source ../common.sh

file_reservations_starts='reservations'

instance_type="m1.large"

__BALLOON_DEPLOY_URL__="http://pypi.python.org/packages/source/b/balloon/balloon-0.05-alfa.tar.gz"


#----------------------------------------------------------------------------------------
unregister_reservation()
{
  a_reservation=${1}
  an_instance_type=${2}
  a_region=${3}
  an_image_id=${4}
  
  a_file_reservations=${file_reservations_starts}_${an_instance_type}_${a_region}_${an_image_id}
  cat ${a_file_reservations} | grep -v -e ${a_reservation} > ${a_file_reservations}
}


#----------------------------------------------------------------------------------------
create_reservation()
{
     an_instance_type=${1}
     a_region=${2}
     an_image_id=${3}
     process_script "amazon_reservation_run.py --instance-type=${an_instance_type}" && a_reservation=`get_result`
     a_file_reservation=${file_reservations_starts}_${an_instance_type}_${a_region}_${an_image_id}
     echo ${a_reservation} >> ${a_file_reservation}
}
        

#----------------------------------------------------------------------------------------
get_reservation()
{  
   a_file_reservations=${1}
   echo `sed '$!d' ${a_file_reservations} 2>/dev/null`
}


#----------------------------------------------------------------------------------------
prepare_reservation()
{
  an_instance_type=${1}
  a_region=${2}
  an_image_id=${3}
  echo ${an_instance_type} >> log.tmp
  if [ ! -f reservations_${an_instance_type}_${a_region}_${an_image_id} ]; then
     create_reservation ${an_instance_type} ${a_region} ${an_image_id}
  else
     a_reservation=`get_reservation ${file_reservations_starts}_${an_instance_type}_${a_region}_${an_image_id}`
     if [ "x${a_reservation}" == "x" ]; then
       create_reservation ${an_instance_type} ${a_region} ${an_image_id}
     fi
  fi
  export __PROCESS_SCRIPT_RESULT__=`get_reservation ${file_reservations_starts}_${an_instance_type}_${a_region}_${an_image_id}`
}

