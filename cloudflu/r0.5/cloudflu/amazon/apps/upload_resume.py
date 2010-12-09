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
def mark_finished( the_file_object, the_working_dir, the_printing_depth ) :
    try :
        the_file_object.seal( the_working_dir )

        return True
    except :
        from cloudflu.common import print_traceback
        print_traceback( the_printing_depth )
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
        from cloudflu.common import print_traceback
        print_traceback( the_printing_depth )
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
        
        a_seed_names = [ a_seed_object.basename() for a_seed_object in the_file_object ]
        
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
    a_worker_pool = WorkerPool( the_number_threads )

    for a_file_object in the_study_object :
        print_d( "a_file_object = %s\n" % a_file_object, the_printing_depth )

        a_worker_pool.charge( upload_file, ( a_file_object, the_number_threads, the_printing_depth + 1 ) )                    
        pass

    a_worker_pool.shutdown()
    a_worker_pool.join()
    pass


#--------------------------------------------------------------------------------------
def entry_point( the_study_object, the_located_files, the_number_threads ) :
    a_spent_time = Timer()
    
    if the_located_files == None :
        upload_files( the_study_object, the_number_threads, 0 )
        pass
    else :
        a_worker_pool = WorkerPool( the_number_threads )
        
        for a_located_file in the_located_files:
            a_file_object = TFileObject.get( the_study_object, a_located_file )
            a_worker_pool.charge( upload_file, ( a_file_object, the_number_threads, 0 ) )                    
            pass
        
        a_worker_pool.shutdown()
        a_worker_pool.join()
        pass
    
    print_d( "a_spent_time = %s, sec\n" % a_spent_time )

    return the_study_object


#--------------------------------------------------------------------------------------
def main() :
    #----------------------- Defining utility command-line interface ------------------------- 
    import data_transfer_options
    import upload_resume_options

    an_usage_description = "%prog"
    an_usage_description += data_transfer_options.usage_description()
    an_usage_description += upload_resume_options.usage_description()
    
    from cloudflu import VERSION
    a_version = "%s" % VERSION
    
    from optparse import IndentedHelpFormatter
    a_help_formatter = IndentedHelpFormatter( width = 127 )
    
    from optparse import OptionParser
    an_option_parser = OptionParser( usage = an_usage_description, version = a_version, formatter = a_help_formatter )

    
    #----------------------- Definition of the command line arguments ------------------------
    data_transfer_options.add( an_option_parser )

    upload_resume_options.add( an_option_parser )

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

    a_located_files = upload_resume_options.extract( an_option_parser )

    a_study_name = data_transfer_options.extract( an_option_parser )


    print_i( "------------------------------- Canonical substitution --------------------------\n" )
    import sys; an_engine = sys.argv[ 0 ]

    a_call = "%s %s %s" % ( an_engine, 
                            data_transfer_options.compose( a_study_name ),
                            upload_resume_options.compose( a_located_files ) )
    print_d( a_call + '\n' )


    print_i( "--------------------------- Looking for study object ----------------------------\n" )
    a_root_object = TRootObject.get( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
    print_d( "a_root_object = %s\n" % a_root_object )

    a_study_object = TStudyObject.get( a_root_object, a_study_name )
    print_d( "a_study_object = %s\n" % a_study_object )


    print_i( "-------------------------- Running actual functionality -------------------------\n" )
    entry_point( a_study_object, a_located_files, a_number_threads )


    print_i( "------------------- Printing succussive pipeline arguments ----------------------\n" )
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
