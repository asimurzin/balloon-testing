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


#--------------------------------------------------------------------------------------
"""
This script is responsible for fetching of the task resulting data from the cloud
"""


#--------------------------------------------------------------------------------------
import balloon.common as common
from balloon.common import print_d, print_e

import balloon.rackspace as rackspace
import balloon.amazon as amazon

import os


#--------------------------------------------------------------------------------------
# Defining utility command-line interface

an_usage_description = "%prog --container-name=33f89d9d-5417-49c1-80c9-787e74cc7154 --output-dir=."
an_usage_description += common.add_usage_description()
an_usage_description += rackspace.add_usage_description()
an_usage_description += amazon.add_usage_description()

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
a_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

# Definition of the command line arguments
a_option_parser.add_option( "--container-name",
                            metavar = "< name of task container >",
                            action = "store",
                            dest = "container_name" )

a_option_parser.add_option( "--output-dir",
                            metavar = "< location of the task defintion >",
                            action = "store",
                            dest = "output_dir",
                            help = "(\"%default\", by default)",
                            default = "." )

common.add_parser_options( a_option_parser )

rackspace.add_parser_options( a_option_parser )

amazon.add_parser_options( a_option_parser )
    

#--------------------------------------------------------------------------------------
# Extracting and verifying command-line arguments

an_options, an_args = a_option_parser.parse_args()

common.extract_options( an_options )

a_container_name = an_options.container_name
if a_container_name == None :
    a_container_name = raw_input()
    pass

RACKSPACE_USER, RACKSPACE_KEY = rackspace.extract_options( an_options )

AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.extract_options( an_options )


#---------------------------------------------------------------------------
# Trying to access to the container with the appointed name

import cloudfiles
a_cloudfiles_conn = cloudfiles.get_connection( RACKSPACE_USER, RACKSPACE_KEY, timeout = 500 )
a_cloudfiles_container = a_cloudfiles_conn[ a_container_name ]


#---------------------------------------------------------------------------
# Creating an output directory

import os.path, shutil
an_options.output_dir = os.path.abspath( an_options.output_dir )
an_output_dir = os.path.join( an_options.output_dir, a_container_name )
shutil.rmtree( an_output_dir, True )
os.makedirs( an_output_dir )
if not os.path.isdir( an_output_dir ) :
    print_e( "Couild not create output directory - '%s'\n" % an_output_dir )
    pass


#---------------------------------------------------------------------------
# Downloding the data from cloud according to the queue

import boto
a_sqs_conn = boto.connect_sqs( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
a_queue_name = common.generate_initial_queue_name( a_container_name )
while True :
    print_d( '%s\n' % a_queue_name ) 
    an_is_final, a_data_name, a_queue_suffix = common.get_message( a_sqs_conn, a_queue_name )
    print_d( '%s %s\n' % ( a_data_name, a_queue_suffix ) )
    
    a_queue_name = common.generate_queue_name( a_container_name, a_queue_suffix )
    
    # To secure the following 'save' operation
    a_file_path = os.path.join( an_output_dir, a_data_name )
    shutil.rmtree( a_file_path, True ) 
    print_d( '%s ' % ( not os.path.isfile( a_file_path ) ) )
    
    a_file_object = a_cloudfiles_container.get_object( a_data_name )
    a_file_object.save_to_filename( a_file_path )
    print_d( '%s %s\n' % ( a_file_path, os.path.isfile( a_file_path ) ) )
    
    if an_is_final:
        break
    
    pass


#---------------------------------------------------------------------------
print_d( 'OK\n' )


#--------------------------------------------------------------------------------------
