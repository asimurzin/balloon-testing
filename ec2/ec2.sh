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

file_reservations_starts='reservations'

instance_type="m1.large"


#----------------------------------------------------------------------------------------
process_script()
{
    a_testing_script=${1} 

    a_script_name=`basename $0`
    if [ $# -gt 1 ] ; then
	a_script_name=${2}
    fi

    echo "================================================================================"
    echo "${a_testing_script}" 
    export a_result=`bash -c "${a_testing_script} 2>>log.${a_script_name}"`
    if [ $? -ne 0 ]; then
	echo "---------------------------------- ERROR----------------------------------------"
	cat log.${a_script_name}
	rm log.${a_script_name}
	echo '----------------------------------- KO -----------------------------------------'
	exit -1
    fi
}


#----------------------------------------------------------------------------------------
get_result()
{
    echo ${a_result}
}


#----------------------------------------------------------------------------------------
rm_from_file_reservations()
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
     echo 'Prepare reservation...' >&2
          
     a_testing_script="amazon_reservation_run.py --instance-type=${an_instance_type} --debug"
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
        echo ${a_reservation} >> ${file_reservations_starts}_${an_instance_type}
     fi
}
        

#----------------------------------------------------------------------------------------
get_reservation()
{  
   a_file_reservations=${1}
   echo `sed '$!d' ${a_file_reservations}`
}


#----------------------------------------------------------------------------------------
prepare_testing_reservation()
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
  echo `get_reservation ${file_reservations_starts}_${an_instance_type}`
}

