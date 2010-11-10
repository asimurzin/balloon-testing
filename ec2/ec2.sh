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


#----------------------------------------------------------------------------------------
unregister_reservation()
{
  an_instance_type=${1}
  a_reservation=${2}
  a_file_reservations=${file_reservations_starts}_${an_instance_type}
  cat ${a_file_reservations} | grep -v -e ${a_reservation} > ${a_file_reservations}
}


#----------------------------------------------------------------------------------------
create_reservation()
{
     an_instance_type=${1}
     process_script "amazon_reservation_run.py --instance-type=${an_instance_type} --debug" && a_reservation=`get_result`

     echo ${a_reservation} >> ${file_reservations_starts}_${an_instance_type}
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
  echo ${an_instance_type} >> log.tmp
  if [ ! -f reservations_${an_instance_type} ]; then
     create_reservation ${an_instance_type}
  else
     a_reservation=`get_reservation ${file_reservations_starts}_${an_instance_type}`
     if [ "x${a_reservation}" == "x" ]; then
       create_reservation ${an_instance_type}
     fi
  fi
  export a_result=`get_reservation ${file_reservations_starts}_${an_instance_type}`
}

