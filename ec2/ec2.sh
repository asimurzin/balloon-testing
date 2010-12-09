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

TEST_CLOUDFLU_FILE_RESERVATIONS_STARTS='reservations'

TEST_CLOUDFLU_INSTANCE_TYPE="m1.large"

__CLOUDFLU_DEPLOY_URL__="http://pypi.python.org/packages/source/c/cloudflu/cloudflu-0.21-alfa.tar.gz"

TEST_CLOUDFLU_EC2_REGIONS='ap-southeast-1 eu-west-1'



#----------------------------------------------------------------------------------------
params_in_region()
{
   a_region=$1
   a_foam_version=$2
   case ${a_region} in
   eu-west-1)
      a_result='EU':'ami-12ffca66'
   ;;
   us-east-1)
      a_result=':'
      case ${a_foam_version} in
        openfoam171_0-1ubuntu2)
           a_result+='ami-ecf50385'
        ;;
        openfoam171_0-1)
           a_result+='ami-62fa0c0b'
        ;;
        openfoam-dev-1.5)
           a_result+='ami-98f701f1'
        ;;
        *)
        ;;
      esac
   ;;
   us-west-1)
      a_result='us-west-1':'ami-24500061'
   ;;
   ap-southeast-1)
      a_result='ap-southeast-1':'ami-0c6d135e'
   ;;
   *) 
      a_result='':''
   ;;
   esac
   echo ${a_result}
}


#----------------------------------------------------------------------------------------

unregister_reservation()
{
  a_reservation=${1}
  an_instance_type=${2}
  a_region=${3}
  an_image_id=${4}
  
  a_file_reservations=${TEST_CLOUDFLU_FILE_RESERVATIONS_STARTS}_${an_instance_type}_${a_region}_${an_image_id}
  cat ${a_file_reservations} | grep -v -e ${a_reservation} > ${a_file_reservations}
}


#----------------------------------------------------------------------------------------
create_reservation()
{
     an_instance_type=${1}
     a_region=${2}
     an_image_id=${3}
     
     an_option=''
     
     if [ "x${an_image_id}" != "x" ]; then
        an_option="${an_option} --image-id=${an_image_id}"
     fi
     process_script "cloudflu-reservation-run --instance-type=${an_instance_type} ${an_option}" && a_reservation=`get_result`
     a_file_reservation=${TEST_CLOUDFLU_FILE_RESERVATIONS_STARTS}_${an_instance_type}_${a_region}_${an_image_id}
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
     a_reservation=`get_reservation ${TEST_CLOUDFLU_FILE_RESERVATIONS_STARTS}_${an_instance_type}_${a_region}_${an_image_id}`
     if [ "x${a_reservation}" == "x" ]; then
       create_reservation ${an_instance_type} ${a_region} ${an_image_id}
     fi
  fi
  export __PROCESS_SCRIPT_RESULT__=`get_reservation ${TEST_CLOUDFLU_FILE_RESERVATIONS_STARTS}_${an_instance_type}_${a_region}_${an_image_id}`
}


#----------------------------------------------------------------------------------------


