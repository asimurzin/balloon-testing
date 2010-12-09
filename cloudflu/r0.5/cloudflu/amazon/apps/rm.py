#!/usr/bin/env python

#------------------------------------------------------------------------------------------
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
Removes whole appointed cloud study or just given files from this study
"""

#------------------------------------------------------------------------------------------
import cloudflu.common as common
from cloudflu.common import print_d, print_i, print_e, sh_command
from cloudflu.common import Timer, WorkerPool, compute_md5

import cloudflu.amazon as amazon
from cloudflu.amazon.s3 import TRootObject, TStudyObject, TFileObject, TSeedObject

import sys, os, os.path, uuid, hashlib


#--------------------------------------------------------------------------------------
def main() :
    #----------------------- Defining utility command-line interface -------------------------    
    an_usage_description = "%prog"

    from rm_options import usage_description as usage_description_options
    an_usage_description += usage_description_options()
    
    from cloudflu import VERSION
    a_version = "%s" % VERSION

    from optparse import IndentedHelpFormatter
    a_help_formatter = IndentedHelpFormatter( width = 127 )

    from optparse import OptionParser
    an_option_parser = OptionParser( usage = an_usage_description, version = a_version, formatter = a_help_formatter )


    #----------------------- Definition of the command line arguments ------------------------
    from rm_options import add as add_options
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

    from rm_options import extract as extract_options
    a_study_name, a_located_files = extract_options( an_option_parser )


    print_i( "--------------------------- Looking for study object ----------------------------\n" )
    a_root_object = TRootObject.get( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
    print_d( "a_root_object = %s\n" % a_root_object )

    a_study_object = TStudyObject.get( a_root_object, a_study_name )
    print_d( "a_study_object = %s\n" % a_study_object )


    print_i( "-------------------------- Removing study files -----------------------------\n" )
    a_worker_pool = WorkerPool( len( a_located_files ) )

    a_deleter = lambda the_object, the_number_threads, the_printing_depth : \
        the_object.delete( the_number_threads, the_printing_depth )

    for a_located_file in a_located_files :
        print_d( "a_located_file = %s\n" % a_located_file )
    
        a_file_object = TFileObject.get( a_study_object, a_located_file )
        print_d( "a_file_object = %s\n" % a_file_object, 1 )
        
        a_worker_pool.charge( a_deleter, ( a_file_object, a_number_threads, 2 ) )
        pass

    a_worker_pool.shutdown()
    a_worker_pool.join()


    print_i( "------------------- Printing succussive pipeline arguments ----------------------\n" )
    print a_study_name


    print_i( "-------------------------------------- OK ---------------------------------------\n" )
    pass


#------------------------------------------------------------------------------------------
if __name__ == '__main__' :
    main()
    pass


#------------------------------------------------------------------------------------------
