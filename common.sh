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


#------------------------------------------------------------------------------------------
run_script()
{
  a_script_name=`basename $0`
  a_fun_name=$1
  if [ -f log.${a_script_name} ]; then
     echo "${a_script_name} already run: remove \"log.${a_script_name}\" to run"
     exit 0
  else
     ${a_fun_name}
  fi
}


#-----------------------------------------------------------------------------------------
runRecursive()
{
  engine=$1
  for case in *; do
     if [ -d ${case} ]; then
        cd ${case}
        if [ -f ${engine} ]; then
           echo ------------------------------------------------------------------------------
           echo "${engine} in the \"${case}\""
           echo ------------------------------------------------------------------------------
           echo
           ./${engine}
           echo
           echo
        fi
        runRecursive ${engine}
        cd ..
     fi
  done
}

