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


#------------------------------------------------------------------------------------------
"""
This script is responsible for efficient uploading of multi file data
"""


#------------------------------------------------------------------------------------------
import balloon.common as common
from balloon.common import print_d, print_i, print_e, sh_command
from balloon.common import Timer, WorkerPool, compute_md5

import balloon.amazon as amazon
from balloon.amazon.s3 import generate_uploading_dir
from balloon.amazon.s3 import TRootObject, TStudyObject, TFileObject, TSeedObject

import sys, os, os.path, uuid, hashlib


#------------------------------------------------------------------------------------------
def mark_finished( the_file_object, the_working_dir, the_printing_depth ) :
    try :
        the_file_object.seal( the_working_dir )

        return True
    except :
        import sys, traceback
        traceback.print_exc( file = sys.stderr )

        pass

    return False


#------------------------------------------------------------------------------------------
def upload_seed( the_file_object, the_seed_name, the_seed_path, the_printing_depth ) :
    "Uploading file item"
    try :
        a_seed_object = TSeedObject.create( the_file_object, the_seed_name, the_seed_path )
        print_d( "%s\n" % a_seed_object, the_printing_depth )
        
        return True
    except :
        import sys, traceback
        traceback.print_exc( file = sys.stderr )

        pass

    return False


#------------------------------------------------------------------------------------------
def upload_seeds( the_file_object, the_working_dir, the_number_threads, the_printing_depth ) :
    "Uploading file items"
    while True :
        a_dir_contents = os.listdir( the_working_dir )

        a_number_threads = max( min( the_number_threads, len( a_dir_contents ) ), 1 )
        print_d( "a_number_threads = %d\n" % a_number_threads, the_printing_depth )

        a_worker_pool = WorkerPool( a_number_threads )
        
        a_dir_contents.sort()
        a_dir_contents.reverse()
        
        a_seed_names = [ a_seed_object.name() for a_seed_object in the_file_object ]
        
        for a_seed_name in a_dir_contents :
            a_seed_path = os.path.join( the_working_dir, a_seed_name )
            print_d( "'%s'\n" % a_seed_path, the_printing_depth + 1 )
        
            if a_seed_name in a_seed_names :
                os.remove( a_seed_path )

                continue

            a_worker_pool.charge( upload_seed, ( the_file_object, a_seed_name, a_seed_path, the_printing_depth + 2 ) )

            pass

        a_worker_pool.shutdown()
        an_is_all_right = a_worker_pool.is_all_right()

        if an_is_all_right :
            mark_finished( the_file_object, the_working_dir, the_printing_depth )

            break

        pass

    return True


#------------------------------------------------------------------------------------------
def upload_file( the_file_object, the_number_threads, the_printing_depth ) :
    a_working_dir = generate_uploading_dir( the_file_object.file_path() )
    if not os.path.exists( a_working_dir ) :
        return True

    print_d( "a_working_dir = '%s'\n" % a_working_dir, the_printing_depth )

    return upload_seeds( the_file_object, a_working_dir, the_number_threads, the_printing_depth + 1 )


#------------------------------------------------------------------------------------------
def upload_files( the_study_object, the_number_threads, the_printing_depth ) :
    for a_file_object in the_study_object :
        print_d( "a_file_object = %s\n" % a_file_object, the_printing_depth )

        upload_file( a_file_object, the_number_threads, the_printing_depth + 1 )
        
        pass

    pass


#------------------------------------------------------------------------------------------
# Defining utility command-line interface

an_usage_description = "%prog --study-name='my interrupted study'"
an_usage_description += common.add_usage_description()
an_usage_description += amazon.add_usage_description()
an_usage_description += amazon.add_timeout_usage_description()
an_usage_description += amazon.add_threading_usage_description()

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
a_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

# Definition of the command line arguments
a_option_parser.add_option( "--study-name",
                            metavar = "< an unique name of the user study >",
                            action = "store",
                            dest = "study_name" )
common.add_parser_options( a_option_parser )
amazon.add_parser_options( a_option_parser )
amazon.add_timeout_options( a_option_parser )
amazon.add_threading_parser_options( a_option_parser )
    
an_engine_dir = os.path.abspath( os.path.dirname( sys.argv[ 0 ] ) )


#------------------------------------------------------------------------------------------
# Extracting and verifying command-line arguments

an_options, an_args = a_option_parser.parse_args()

common.extract_options( an_options )

a_study_name = an_options.study_name
if a_study_name == None :
    a_study_name = raw_input()
    pass

print_d( "a_study_name = '%s'\n" % a_study_name )
    
AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.extract_options( an_options )

a_number_threads = amazon.extract_threading_options( an_options, a_option_parser )

amazon.extract_timeout_options( an_options, a_option_parser )


print_i( "--------------------------- Looking for study object ----------------------------\n" )
a_root_object = TRootObject.get( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
print_d( "a_root_object = %s\n" % a_root_object )

a_study_object = TStudyObject.get( a_root_object, a_study_name )
print_d( "a_study_object = %s\n" % a_study_object )


print_i( "---------------------------- Uploading study files ------------------------------\n" )
a_data_loading_time = Timer()

upload_files( a_study_object, a_number_threads, 0 )

print_d( "a_data_loading_time = %s, sec\n" % a_data_loading_time )


print_i( "-------------------------------------- OK ---------------------------------------\n" )
print a_study_name


#------------------------------------------------------------------------------------------
