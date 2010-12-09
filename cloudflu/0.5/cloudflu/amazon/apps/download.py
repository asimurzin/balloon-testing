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
This script is responsible for efficient downloading of multi file data
"""


#------------------------------------------------------------------------------------------
import cloudflu.common as common
from cloudflu.common import print_d, print_i, print_e, sh_command
from cloudflu.common import Timer, WorkerPool, TaggedWorkerPool, compute_md5

import cloudflu.amazon as amazon
from cloudflu.amazon.s3 import TRootObject, TStudyObject, TFileObject, TSeedObject

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
        from cloudflu.common import print_traceback
        print_traceback( the_printing_depth + 1 )
        pass

    return False


#------------------------------------------------------------------------------------------
def download_seeds( the_file_object, the_file_basename, the_output_dir, the_number_threads, the_printing_depth ) :
    an_is_download_ok = False
    while not the_file_object.sealed() or not an_is_download_ok :
        a_worker_pool = WorkerPool( the_number_threads )
        try:
            for a_seed_object in the_file_object :
                a_hex_md5 = a_seed_object.hex_md5()
                a_seed_path = os.path.join( the_output_dir, a_seed_object.basename() )

                if os.path.exists( a_seed_path ) :
                    a_file_pointer = open( a_seed_path, 'rb' )
                    a_md5 = compute_md5( a_file_pointer )[ 0 ]
                    
                    if a_hex_md5 == a_md5 :
                        continue
                    
                    os.remove( a_seed_path )

                    pass

                print_d( "a_seed_path = '%s'\n" % a_seed_path, the_printing_depth )

                a_worker_pool.charge( download_seed, ( a_seed_object, a_seed_path, the_printing_depth + 1 ) )
        except:
            from cloudflu.common import print_traceback
            print_traceback( the_printing_depth )
            pass

        a_worker_pool.shutdown()
        an_is_download_ok = a_worker_pool.is_all_right()

        print_d( "'%s'.uploaded() == %s\n" % ( the_file_object.located_file(), the_file_object.sealed() ), the_printing_depth )
        pass
    
    return True


#------------------------------------------------------------------------------------------
def download_file( the_file_object, the_output_dir, the_number_threads, the_remove, the_fresh, the_callback ) :
    a_printing_depth = 0
    print_d( "the_file_object = %s\n" % the_file_object, a_printing_depth )

    a_hex_md5 = the_file_object.hex_md5()
    a_located_file = the_file_object.located_file()

    import os.path
    a_file_dirname = os.path.dirname( a_located_file )
    a_file_basename = os.path.basename( a_located_file )

    import os.path; an_output_dir = os.path.join( the_output_dir, a_file_dirname )
    print_d( "an_output_dir = '%s'\n" % an_output_dir, a_printing_depth + 1 )
    
    import os.path; a_file_path = os.path.join( an_output_dir, a_file_basename )
    if the_fresh :
        sh_command( "rm -fr '%s.tgz*'" % ( a_file_path ), a_printing_depth + 1 )
        sh_command( "rm -fr '%s'" % ( a_file_path ), a_printing_depth + 1 )
        pass

    if not os.path.exists( an_output_dir ) :
        os.makedirs( an_output_dir )
        pass

    print_d( "a_file_path = '%s'\n" % a_file_path, a_printing_depth + 2 )
    if not os.path.exists( a_file_path ) :
        while True :
            download_seeds( the_file_object, a_file_basename, an_output_dir, the_number_threads, a_printing_depth + 3 )
            
            an_archive_name = "%s.tgz" % a_file_basename
            
            import os.path
            an_archive_path = os.path.join( an_output_dir, an_archive_name )
            if not os.path.exists( an_archive_path ) :
                sh_command( "cd '%s' && cat %s-* > %s" % ( an_output_dir, an_archive_name, an_archive_name ), a_printing_depth + 1 )
                pass

            an_archive_pointer = open( an_archive_path, 'rb' )
            a_md5 = compute_md5( an_archive_pointer )[ 0 ]

            print_d( "'%s' - %s\n" % ( a_hex_md5, ( a_hex_md5 == a_md5 ) ), a_printing_depth + 1 )
            
            if a_hex_md5 == a_md5 :
                break

            import os; os.remove( an_archive_path )
            pass
        
        sh_command( "tar -xzf '%s' -C '%s'" % ( an_archive_path, an_output_dir ), a_printing_depth + 1 )
        
        sh_command( "cd '%s' && rm %s-*" % ( an_output_dir, an_archive_name ), a_printing_depth + 1 )
        
        os.remove( an_archive_path )
    else:
        print_d( "- nothing to be done, already downloaded\n", a_printing_depth + 1 )
        pass

    if the_remove == True and os.path.exists( a_file_path ) :
        the_file_object.delete( the_number_threads, a_printing_depth + 1 )
        pass

    if the_callback != None :
        the_callback( an_output_dir, a_located_file )
        pass
        
    return True


#------------------------------------------------------------------------------------------
def download_files( the_study_object, the_output_dir, the_number_threads, the_wait, the_remove, the_fresh, the_callback ) :
    a_worker_pool = TaggedWorkerPool( the_number_threads )

    if the_wait == False or the_study_object.sealed() :
        for a_file_object in the_study_object :
            a_worker_pool.charge( a_file_object.located_file(), download_file, 
                                  ( a_file_object, the_output_dir, the_number_threads, the_remove, the_fresh, the_callback ) )
            pass

        a_worker_pool.shutdown()
        a_worker_pool.join()
    else:
        print_d( "waiting ", 0 )

        while True :
            an_sealed = the_study_object.sealed()

            for a_file_object in the_study_object :
                a_worker_pool.charge( a_file_object.located_file(), download_file, 
                                      ( a_file_object, the_output_dir, the_number_threads, the_remove, the_fresh, the_callback ) )
                pass

            if an_sealed :
                break

            print_d( "." )
            pass

        a_worker_pool.shutdown()
        a_worker_pool.join()
        
        print_d( " compleated\n", 0 )
        return
    
    if the_remove == True :
        the_study_object.delete( the_number_threads, 0 )
        pass

    pass


#--------------------------------------------------------------------------------------
def file_entry_point( the_study_object, the_output_dir, the_located_file, 
                      the_number_threads, the_wait, the_remove, the_fresh, the_callback ) :
    if the_wait == False or the_study_object.sealed() :
        try:
            a_file_object = TFileObject.get( the_study_object, the_located_file )
            download_file( a_file_object, the_output_dir, the_number_threads, the_remove, the_fresh, the_callback )
        except:
            from cloudflu.common import print_traceback
            print_traceback( 0 )
            pass
        pass
    else:
        print_d( "waiting " )
        
        while True :
            an_sealed = the_study_object.sealed()
            
            try:
                a_file_object = TFileObject.get( the_study_object, the_located_file )
                print_d( "\n" )
                download_file( a_file_object, the_output_dir, the_number_threads, the_remove, the_fresh, the_callback )
                break
            except:
                if an_sealed :
                    break
                print_d( "." )
                pass
            
            
            pass

        print_d( " compleated\n" )
        pass
    
    pass


#--------------------------------------------------------------------------------------
def entry_point( the_study_object, the_output_dir, the_located_files = None, 
                 the_number_threads = 3, the_wait = True, the_remove = False, the_fresh = False, the_callback = None ) :
    a_spent_time = Timer()
    
    if the_output_dir == None :
        the_output_dir = os.path.join( os.curdir, the_study_object.name() )
        pass

    if the_located_files == None :
        download_files( the_study_object, the_output_dir,
                        the_number_threads, the_wait, the_remove, the_fresh, the_callback )
    else :
        a_worker_pool = TaggedWorkerPool( the_number_threads )
        
        for a_located_file in the_located_files :
            a_worker_pool.charge( a_located_file, file_entry_point, 
                                  ( the_study_object, the_output_dir, a_located_file, 
                                    the_number_threads, the_wait, the_remove, the_fresh, the_callback ) )
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
    import download_options

    an_usage_description = "%prog"
    an_usage_description += data_transfer_options.usage_description()
    an_usage_description += download_options.usage_description()
    
    from cloudflu import VERSION
    a_version = "%s" % VERSION
    
    from optparse import IndentedHelpFormatter
    a_help_formatter = IndentedHelpFormatter( width = 127 )
    
    from optparse import OptionParser
    an_option_parser = OptionParser( usage = an_usage_description, version = a_version, formatter = a_help_formatter )


    #----------------------- Definition of the command line arguments ------------------------
    data_transfer_options.add( an_option_parser )

    download_options.add( an_option_parser )

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

    a_located_files, an_output_dir, a_fresh, a_wait, a_remove = download_options.extract( an_option_parser )

    a_study_name = data_transfer_options.extract( an_option_parser )


    print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
    import sys; an_engine = sys.argv[ 0 ]

    from download_options import compose as compose_options
    a_call = "%s %s %s" % ( an_engine, 
                            data_transfer_options.compose( a_study_name ),
                            download_options.compose( a_located_files, an_output_dir, a_fresh, a_wait, a_remove ) )
    print_d( a_call + '\n' )


    print_i( "--------------------------- Looking for study object ----------------------------\n" )
    a_root_object = TRootObject.get( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
    print_d( "a_root_object = %s\n" % a_root_object )

    a_study_object = None
    try:
        a_study_object = TStudyObject.get( a_root_object, a_study_name )
    except Exception, exc:
        print_e( '%s\n' % exc )
        pass
    print_d( "a_study_object = %s\n" % a_study_object )
    

    print_i( "-------------------------- Running actual functionality -------------------------\n" )
    a_study_object = entry_point( a_study_object, an_output_dir, a_located_files, 
                                  a_number_threads, a_wait, a_remove, a_fresh )
    
    print_i( "------------------- Printing succussive pipeline arguments ----------------------\n" )
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
