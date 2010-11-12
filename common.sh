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
export __BALLOON_DEBUG_ENABLE__="X" # To enable debug mode (undocumented feature, just for testing)


#----------------------------------------------------------------------------------------
process_script()
{
    a_script_name=`basename ${0}`

    a_testing_script=${1}

    a_log_file_name="./log.${a_script_name}"
    if [ $# -ge 2 ] ; then 
	a_log_file_name="${a_log_file_name}_${2}"
    fi

    echo "================================================================================"
    echo "${a_testing_script}" 
    a_testing_script=`echo ${a_testing_script} | sed -e "s%|%2>>${a_log_file_name} |%g"`
    export __PROCESS_SCRIPT_RESULT__=`bash -c "${a_testing_script} 2>>${a_log_file_name} || echo X"`
    if [ "${__PROCESS_SCRIPT_RESULT__}x" == 'Xx' ]; then
	echo "---------------------------------- ERROR----------------------------------------"
	cat ${a_log_file_name}
	rm ${a_log_file_name}
	echo "${a_testing_script}" 
	echo '----------------------------------- KO -----------------------------------------'
	exit -1
    fi
}


#----------------------------------------------------------------------------------------
get_result()
{
    echo ${__PROCESS_SCRIPT_RESULT__}
}


#----------------------------------------------------------------------------------------
process_error()
{
    a_script_name=`basename ${0}`

    an_error_message=${1}

    a_log_file_name="./log.${a_script_name}"
    if [ $# -ge 2 ] ; then 
	a_log_file_name="${a_log_file_name}_${2}"
    fi

    echo "---------------------------------- ERROR----------------------------------------"
    cat ${a_log_file_name}
    rm ${a_log_file_name}
    echo "--------------------------------------------------------------------------------"
    printf "${an_error_message}\n"
    echo '----------------------------------- KO -----------------------------------------'
    exit -1
}


#------------------------------------------------------------------------------------------
run_script()
{
    a_test_log_name=./log.`basename ${0}`
    if [ -f ${a_test_log_name} ]; then
	a_script_name=${0}; 
	a_user_log_name=`dirname ${0}`/log.`basename ${0}`
	echo "rm ${a_user_log_name} # before run '${a_script_name}'"
	exit 0
    else
	a_function=${1}; ${a_function}
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


#-----------------------------------------------------------------------------------------
