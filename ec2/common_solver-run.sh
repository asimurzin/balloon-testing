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
single_test()
{
  echo "********************************************************************************"
  echo $0

  a_region=${1}
  
  a_foam_version=${2}
  
  echo " \"${a_region}\"  \"${a_foam_version}\""
  
  a_params=`params_in_region ${a_region} ${a_foam_version}`
  a_s3location=`echo $a_params | awk "-F:" '{print $1}'`
  an_image_id=`echo $a_params | awk "-F:" '{print $2}'`
     
  export __CLOUDFLU_IMAGE_LOCATION__=${a_region}
      
  export __CLOUDFLU_S3_LOCATION__=${a_s3location}
     
  prepare_reservation ${instance_type} ${a_region} ${an_image_id} && a_reservation=`get_result`
     
  process_script "echo '${a_reservation}' | cloudflu-openmpi-config | cloudflu-nfs-config"
     
  process_script "echo '${a_reservation}' | cloudflu-instance-extract" && an_instance=`get_result`
     
  process_script "echo ${an_instance} | cloudflu-credentials-deploy | cloudflu-deploy --production --url='${__CLOUDFLU_DEPLOY_URL__}'"
     
  process_script "mkfifo $$ && cloudflu-study-book | tee >(cloudflu-solver-process --output-dir='damBreak.out' >$$) | cloudflu-solver-start <(echo '${a_reservation}') --case-dir='damBreak' | cat $$ && rm $$"
     
  process_script "cloudflu-cluster-rm ${a_reservation}"
    
  unregister_reservation ${a_reservation} ${instance_type} ${a_region} ${an_image_id}

  echo '----------------------------------- OK -----------------------------------------'
}
