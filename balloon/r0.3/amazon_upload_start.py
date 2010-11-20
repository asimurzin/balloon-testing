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
## See http://sourceforge.net/apps/mediawiki/balloon-foam
##
## Author : Alexey Petrov
##


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
def upload_files( the_file2locations, the_study_object, the_upload_seed_size, the_printing_depth ) :
    a_worker_pool = WorkerPool( len( the_file2locations ) )

    for a_file, a_location_file in the_file2locations.iteritems() :
        a_worker_pool.charge( upload_file, ( a_worker_pool, a_file, a_location_file, the_study_object, 
                                             the_upload_seed_size, the_printing_depth ) )

        pass

    a_worker_pool.shutdown()
    a_worker_pool.join()
    
    pass


#------------------------------------------------------------------------------------------
def extract_locations( the_file_locations ):

    return the_file_locations.split( common.arg_list_separator() )


#--------------------------------------------------------------------------------------
# Defining utility command-line interface

an_usage_description = "%prog"
an_usage_description += " --study-name='my favorite study' --upload-item-size=5160 --socket-timeout=3"
an_usage_description += " --file-locations= '<file1 location>,<file2 location>,...'"
an_usage_description += common.add_usage_description()
an_usage_description += amazon.add_usage_description()
an_usage_description += amazon.add_timeout_usage_description()
an_usage_description += " <file 1> <file 2> ..."

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
an_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

# Definition of the command line arguments
an_option_parser.add_option( "--study-name",
                             metavar = "< an unique name of the user study >",
                             action = "store",
                             dest = "study_name",
                             help = "(generated, by default)",
                             default = 'tmp-' + str( uuid.uuid4() ) )
an_option_parser.add_option( "--file-locations",
                             metavar = "< location of files inside of the study >",
                             action = "store",
                             dest = "file_locations",
                             help = "(\"%default\", by default)",
                             default = '' )
an_option_parser.add_option( "--upload-item-size",
                             metavar = "< size of file pieces to be uploaded, in bytes >",
                             type = "int",
                             action = "store",
                             dest = "upload_seed_size",
                             help = "(\"%default\", by default)",
                             default = 65536 )
common.add_parser_options( an_option_parser )
amazon.add_parser_options( an_option_parser )
amazon.add_timeout_options( an_option_parser )
    
an_engine_dir = os.path.abspath( os.path.dirname( sys.argv[ 0 ] ) )


#------------------------------------------------------------------------------------------
# Extracting and verifying command-line arguments

an_options, an_args = an_option_parser.parse_args()

common.extract_options( an_options )

a_source_files = None
if len( an_args ) == 0 :
    a_source_files = [ raw_input() ]
else :
    a_source_files = an_args
    pass

a_files = list()
for a_file in a_source_files :
    if not os.path.exists( a_file ) :
        an_option_parser.error( "The given file should exists\n" )
        pass
    a_files.append( os.path.abspath( a_file ) )
    pass

if len( a_files ) == 0 :
    an_option_parser.error( "You should define one valid 'file' at least\n" )
    pass

print_d( "a_files = %r\n" % a_files )

a_file_locations = extract_locations( an_options.file_locations )

a_file2locations = {}
if len( a_file_locations ) > 1 :
    if len( a_files ) != len( a_file_locations ) :
        an_option_parser.error( "The amount of file locations shoudl be equal to the number of given files\n" )
    else :
        for an_id in range( len( a_files ) ) :
            a_file = a_files[ an_id ]
            a_location = a_file_locations[ an_id ]
            a_file2locations[ a_file ] = a_location
            pass
        pass
else :
    a_location = a_file_locations[ 0 ]
    for a_file in a_files:
        a_file2locations[ a_file ] = a_location
        pass
    pass   

print_d( "a_file2locations = %r\n" % a_file2locations )

a_study_name = an_options.study_name
print_d( "a_study_name = '%s'\n" % a_study_name )
    
AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.extract_options( an_options )

amazon.extract_timeout_options( an_options, an_option_parser )


print_i( "--------------------------- Defining the study object ---------------------------\n" )
a_root_object = TRootObject.get( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
print_d( "a_root_object = %s\n" % a_root_object )

a_study_object = TStudyObject.create( a_root_object, a_study_name )
print_d( "a_study_object = %s\n" % a_study_object )


print_i( "---------------------------- Uploading study files ------------------------------\n" )
a_data_loading_time = Timer()

upload_files( a_file2locations, a_study_object, an_options.upload_seed_size, 0 )

print_d( "a_data_loading_time = %s, sec\n" % a_data_loading_time )


print_i( "-------------------------------------- OK ---------------------------------------\n" )
print a_study_name


#------------------------------------------------------------------------------------------
