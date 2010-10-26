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


#----------------------------------------------------------------------------------------
run_old_api_script()
{
  a_script_name=`basename $0`
  a_fun_name=$1
  
  for an_api in ${a_list_old_api}
  do
    if [ ! -f log.${a_script_name}_${an_api} ]; then
       ${a_fun_name} ${an_api}
    else
       echo "${a_script_name} api_version=\"${an_api}\" already run : remove log.${a_script_name}_${an_api} to run"
       continue
    fi
  done
}
