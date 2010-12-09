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


#------------------------------------------------------------------------------------------
def upload_file( the_worker_pool, the_file_path, the_file_location, the_study_object, the_upload_seed_size, the_printing_depth ) :
    a_working_dir = generate_uploading_dir( the_file_path )

    import shutil
    shutil.rmtree( a_working_dir, True )
    os.makedirs( a_working_dir )
    print_d( "a_working_dir = '%s'\n" % a_working_dir, the_printing_depth )

    a_file_dirname = os.path.dirname( the_file_path )
    a_file_basename = os.path.basename( the_file_path )

    import tempfile
    a_tmp_file = tempfile.mkstemp( dir = a_working_dir )[ 1 ]
    # a_tmp_file = tempfile.mkstemp()[ 1 ] # use this work arround for FAT file systems
    sh_command( "cd '%s' &&  tar -czf %s '%s'" % 
                ( a_file_dirname, a_tmp_file, a_file_basename ), the_printing_depth )

    a_statinfo = os.stat( a_tmp_file )
    print_d( "a_statinfo.st_size = %d, bytes\n" % a_statinfo.st_size, the_printing_depth )

    import math
    a_suffix_length = math.log10( float( a_statinfo.st_size ) / the_upload_seed_size )
    if a_suffix_length > 0 :
        a_suffix_length = int( a_suffix_length + 1.0 )
    else:
        a_suffix_length = 0
        pass
    print_d( "a_suffix_length = %d, digits\n" % a_suffix_length, the_printing_depth )

    a_file_seed_target = os.path.join( a_working_dir, a_file_basename )
    sh_command( "cat '%s' | split --bytes=%d --numeric-suffixes --suffix-length=%d - %s.tgz-" % 
                ( a_tmp_file, the_upload_seed_size, a_suffix_length, a_file_seed_target ), the_printing_depth )

    a_file_pointer = open( a_tmp_file, 'rb' )
    a_md5 = compute_md5( a_file_pointer )
    a_hex_md5, a_base64md5 = a_md5

    a_file_pointer.close()
    os.remove( a_tmp_file )

    a_file_object = TFileObject.create( the_study_object, the_file_path, the_file_location, a_hex_md5 )
    print_d( "a_file_object = %s\n" % a_file_object, the_printing_depth )

    pass


#------------------------------------------------------------------------------------------
def upload_files( the_study_object, the_file2locations, the_upload_seed_size, the_number_threads, the_printing_depth ) :
    a_worker_pool = WorkerPool( the_number_threads )

    for a_file, a_location_file in the_file2locations.iteritems() :
        a_worker_pool.charge( upload_file, ( a_worker_pool, a_file, a_location_file, the_study_object, 
                                             the_upload_seed_size, the_printing_depth ) )

        pass

    a_worker_pool.shutdown()
    a_worker_pool.join()
    
    pass


#------------------------------------------------------------------------------------------
def entry_point( the_study_object, the_file2locations, the_upload_seed_size, the_number_threads ) :
    a_spent_time = Timer()
    
    upload_files( the_study_object, the_file2locations, the_upload_seed_size, the_number_threads, 0 )
    
    print_d( "a_spent_time = %s, sec\n" % a_spent_time )

    return the_study_object
    

#--------------------------------------------------------------------------------------
def main() :
    #----------------------- Defining utility command-line interface -------------------------
    import data_transfer_options
    import upload_start_options
    import data_seeding_options

    an_usage_description = "%prog"
    an_usage_description += data_transfer_options.usage_description()
    an_usage_description += upload_start_options.usage_description()
    
    from cloudflu import VERSION
    a_version = "%s" % VERSION
    
    from optparse import IndentedHelpFormatter
    a_help_formatter = IndentedHelpFormatter( width = 127 )
    
    from optparse import OptionParser
    an_option_parser = OptionParser( usage = an_usage_description, version = a_version, formatter = a_help_formatter )
    

    #----------------------- Definition of the command line arguments ------------------------
    data_transfer_options.add( an_option_parser )

    upload_start_options.add( an_option_parser )

    data_seeding_options.add( an_option_parser )

    common.concurrency_options.add( an_option_parser )

    common.communication_options.add( an_option_parser )

    amazon.security_options.add( an_option_parser )
    
    common.options.add( an_option_parser )

    
    #------------------ Extracting and verifying command-line arguments ----------------------
    an_options, an_args = an_option_parser.parse_args()

    common.options.extract( an_option_parser )
    
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.security_options.extract( an_option_parser )
    
    common.communication_options.extract( an_option_parser )

    a_number_threads = common.concurrency_options.extract( an_option_parser )
    
    an_upload_seed_size = data_seeding_options.extract( an_option_parser )

    a_file2locations = upload_start_options.extract( an_option_parser )

    a_study_name = data_transfer_options.extract( an_option_parser )
    
    
    print_i( "------------------------------- Canonical substitution --------------------------\n" )
    import sys; an_engine = sys.argv[ 0 ]

    a_call = "%s %s" % ( an_engine, 
                         data_transfer_options.compose( a_study_name ) )
    print_d( a_call + '\n' )


    print_i( "--------------------------- Defining the study object ---------------------------\n" )
    a_root_object = TRootObject.get( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
    print_d( "a_root_object = %s\n" % a_root_object )
    
    a_study_object = TStudyObject.get( a_root_object, a_study_name )
    print_d( "a_study_object = %s\n" % a_study_object )
    

    print_i( "-------------------------- Running actual functionality -------------------------\n" )
    a_study_object = entry_point( a_study_object, a_file2locations, an_upload_seed_size, a_number_threads )
    
    
    print_i( "-------------------- Printing succussive pipeline arguments ---------------------\n" )
    print a_study_name

    
    print_i( "------------------------------- Canonical substitution --------------------------\n" )
    print_d( a_call + '\n' )
    

    print_i( "-------------------------------------- OK ---------------------------------------\n" )
    pass


#------------------------------------------------------------------------------------------
if __name__ == '__main__' :
    main()
    pass


#------------------------------------------------------------------------------------------
