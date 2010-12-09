#!/usr/bin/env python

#--------------------------------------------------------------------------------------
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
## See http://sourceforge.net/apps/mediawiki/cloudflu
##
## Author : Alexey Petrov
##


#------------------------------------------------------------------------------------------
"""
This script is responsible for efficient uploading of multi file data
"""


#------------------------------------------------------------------------------------------
import cloudflu.common as common
from cloudflu.common import print_d, print_i, print_e, sh_command
from cloudflu.common import Timer, WorkerPool, compute_md5

import cloudflu.amazon as amazon
from cloudflu.amazon.s3 import generate_uploading_dir
from cloudflu.amazon.s3 import TRootObject, TStudyObject, TFileObject, TSeedObject

import sys, os, os.path, uuid, hashlib


#--------------------------------------------------------------------------------------
def main() :
    #----------------------- Defining utility command-line interface -------------------------    
    an_usage_description = "%prog"

    from study_seal_options import usage_description as usage_description_options
    an_usage_description += usage_description_options()
    
    from cloudflu import VERSION
    a_version = "%s" % VERSION
    
    from optparse import IndentedHelpFormatter
    a_help_formatter = IndentedHelpFormatter( width = 127 )
    
    from optparse import OptionParser
    an_option_parser = OptionParser( usage = an_usage_description, version = a_version, formatter = a_help_formatter )
    
    #----------------------- Definition of the command line arguments ------------------------
    from study_seal_options import add as add_options
    add_options( an_option_parser )

    amazon.security_options.add( an_option_parser )
    
    common.concurrency_options.add( an_option_parser )

    common.communication_options.add( an_option_parser )

    common.options.add( an_option_parser )

    
    #------------------ Extracting and verifying command-line arguments ----------------------
    an_options, an_args = an_option_parser.parse_args()

    common.options.extract( an_option_parser )
    
    common.communication_options.extract( an_option_parser )

    a_number_threads = common.concurrency_options.extract( an_option_parser )
    
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.security_options.extract( an_option_parser )
    
    from study_seal_options import extract as extract_options
    a_study_name = extract_options( an_option_parser )
    
    
    print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
    import sys; an_engine = sys.argv[ 0 ]

    from study_seal_options import compose as compose_options
    a_call = "%s %s" % ( an_engine, compose_options( a_study_name ) )
    print_d( a_call + '\n' )


    print_i( "--------------------------- Defining the study object ---------------------------\n" )
    a_spent_time = Timer()

    a_root_object = TRootObject.get( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
    print_d( "a_root_object = %s\n" % a_root_object )
    
    a_study_object = TStudyObject.get( a_root_object, a_study_name )
    print_d( "a_study_object = %s\n" % a_study_object )
    
    a_study_object.seal()
    print_d( "is sealed : %r\n" % a_study_object.sealed() )

    print_d( "a_spent_time = %s, sec\n" % a_spent_time )
    
    
    print_i( "-------------------- Printing succussive pipeline arguments ---------------------\n" )
    print a_study_name

    
    print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
    print_d( a_call + '\n' )
    

    print_i( "-------------------------------------- OK ---------------------------------------\n" )
    pass


#------------------------------------------------------------------------------------------
if __name__ == '__main__' :
    main()
    pass


#------------------------------------------------------------------------------------------
