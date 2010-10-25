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
This script is responsible for efficient downloading of multi file data
"""


#------------------------------------------------------------------------------------------
import balloon.common as common
from balloon.common import print_d, print_i, print_e, sh_command
from balloon.common import Timer, WorkerPool, compute_md5

import balloon.amazon as amazon
from balloon.amazon.s3 import TRootObject, TStudyObject, TFileObject, TSeedObject

import boto
from boto.s3.key import Key

import sys, os, os.path, uuid, hashlib


#------------------------------------------------------------------------------------------
def download_seed( the_seed_object, the_file_path, the_printing_depth ) :
    try :
        the_seed_object.download( the_file_path )
        print_d( "the_seed_object = %s\n" % the_seed_object, the_printing_depth )
        
        return True
    except :
        import sys, traceback
        traceback.print_exc( file = sys.stderr )

        pass

    return False


#------------------------------------------------------------------------------------------
def download_seeds( the_file_object, the_file_basename, the_output_dir, the_number_threads, the_printing_depth ) :
    an_is_download_ok = False
    an_is_everything_uploaded = False
    while not an_is_everything_uploaded or not an_is_download_ok :
        a_worker_pool = WorkerPool( the_number_threads )

        for a_seed_object in the_file_object :
            if a_seed_object.is_seal() :
                an_is_everything_uploaded = True
                print_d( "an_is_everything_uploaded = %s\n" % an_is_everything_uploaded, the_printing_depth )
                continue

            a_hex_md5 = a_seed_object.hex_md5()
            a_seed_path = os.path.join( the_output_dir, a_seed_object.name() )

            if os.path.exists( a_seed_path ) :
                a_file_pointer = open( a_seed_path, 'rb' )
                a_md5 = compute_md5( a_file_pointer )[ 0 ]

                if a_hex_md5 == a_md5 :
                    continue

                os.remove( a_seed_path )

                pass

            print_d( "a_seed_path = '%s'\n" % a_seed_path, the_printing_depth )

            a_worker_pool.charge( download_seed, ( a_seed_object, a_seed_path, the_printing_depth + 1 ) )
            
            pass

        a_worker_pool.shutdown()
        an_is_download_ok = a_worker_pool.is_all_right()

        pass
    
    return True


#------------------------------------------------------------------------------------------
def download_file( the_file_object, the_output_dir, the_number_threads, the_enable_fresh, the_printing_depth ) :
    print_d( "the_file_object = %s\n" % the_file_object, the_printing_depth )

    a_hex_md5 = the_file_object.hex_md5()
    a_source_file_path = the_file_object.file_path()

    a_file_dirname = os.path.dirname( a_source_file_path )
    a_file_basename = os.path.basename( a_source_file_path )

    an_output_dir = os.path.join( the_output_dir, a_file_dirname[ 1 : ] )
    print_d( "an_output_dir = '%s'\n" % an_output_dir, the_printing_depth + 1 )
    
    if the_enable_fresh :
        import shutil
        shutil.rmtree( an_output_dir, True )

        pass

    if not os.path.exists( an_output_dir ) :
        os.makedirs( an_output_dir )

        pass

    a_file_path = os.path.join( an_output_dir, a_file_basename )
    print_d( "a_file_path = '%s'\n" % a_file_path, the_printing_depth + 2 )
    if os.path.exists( a_file_path ) :
        print_d( "nothing to be done, already downloaded\n", the_printing_depth + 3 )

        return True

    while True :
        download_seeds( the_file_object, a_file_basename, an_output_dir, the_number_threads, the_printing_depth + 3 )
        
        an_archive_name = "%s.tgz" % a_file_basename

        sh_command( "cd '%s' && cat %s-* > %s" % ( an_output_dir, an_archive_name, an_archive_name ), the_printing_depth )

        an_archive_path = os.path.join( an_output_dir, an_archive_name )
        an_archive_pointer = open( an_archive_path, 'rb' )
        a_md5 = compute_md5( an_archive_pointer )[ 0 ]

        print_d( "'%s' - %s\n" % ( a_hex_md5, ( a_hex_md5 == a_md5 ) ), the_printing_depth )

        if a_hex_md5 == a_md5 :
            break

        pass

    sh_command( "tar -xzf '%s' -C '%s'" % ( an_archive_path, an_output_dir ), the_printing_depth + 2 )

    sh_command( "cd '%s' && rm %s-*" % ( an_output_dir, an_archive_name ), the_printing_depth + 2 )

    os.remove( an_archive_path )

    return True


#------------------------------------------------------------------------------------------
def download_files( the_study_object, the_output_dir, the_number_threads, the_enable_fresh, the_printing_depth ) :
    a_worker_pool = WorkerPool( the_number_threads )

    for a_file_object in the_study_object :
        a_worker_pool.charge( download_file, ( a_file_object, the_output_dir, the_number_threads, the_enable_fresh, the_printing_depth ) )
        
        pass

    a_worker_pool.shutdown()
    a_worker_pool.join()

    pass


#------------------------------------------------------------------------------------------
# Defining utility command-line interface

an_usage_description = "%prog --study-name='my uploaded study' --file-name='/home/alexey' --output-dir='./tmp'"
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
                            metavar = "< a name of an uploaded study >",
                            action = "store",
                            dest = "study_name",
                            help = "(intialized from input, otherwise)" )
a_option_parser.add_option( "--file-name",
                            metavar = "< a of a file into uploaded study >",
                            action = "store",
                            dest = "file_name",
                            help = "(if missed, all the study files will be downloaded)" )
a_option_parser.add_option( "--output-dir",
                            metavar = "< location of the task defintion >",
                            action = "store",
                            dest = "output_dir",
                            help = "(the same a 'study' name, by default)" )
a_option_parser.add_option( "--enable-fresh",
                            action = "store_true",
                            dest = "enable_fresh",
                            help = "do not take into account previous downloads",
                            default = False )
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
    
an_output_dir = an_options.output_dir
if an_output_dir == None :
    an_output_dir = os.path.join( an_engine_dir, a_study_name )
    pass

print_d( "an_output_dir = '%s'\n" % an_output_dir )

an_enable_fresh = an_options.enable_fresh
print_d( "an_enable_fresh = %s\n" % an_enable_fresh )

AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.extract_options( an_options )

a_number_threads = amazon.extract_threading_options( an_options, a_option_parser )

print_d( "a_number_threads = %d\n" % a_number_threads )

amazon.extract_timeout_options( an_options, a_option_parser )


print_i( "--------------------------- Looking for study object ----------------------------\n" )
a_root_object = TRootObject.get( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
print_d( "a_root_object = %s\n" % a_root_object )

a_study_object = TStudyObject.get( a_root_object, a_study_name )
print_d( "a_study_object = %s\n" % a_study_object )


print_i( "--------------------------- Reading the study files -----------------------------\n" )
a_data_loading_time = Timer()

a_file_name = an_options.file_name
if a_file_name == None :
    download_files( a_study_object, an_output_dir, a_number_threads, an_enable_fresh, 0 )

else :
    a_file_object = TFileObject.get( a_study_object, a_file_name )

    download_file( a_file_object, an_output_dir, a_number_threads, an_enable_fresh, 0 )

    pass

print_d( "a_data_loading_time = %s, sec\n" % a_data_loading_time )


print_i( "-------------------------------------- OK ---------------------------------------\n" )

