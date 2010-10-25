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
This script is responsible for the task packaging and sending it for execution in a cloud
"""


#--------------------------------------------------------------------------------------
import balloon.common as common
from balloon.common import print_d, print_list, print_e, sh_command, Timer

import balloon.rackspace as rackspace

import sys, os, os.path, uuid


#--------------------------------------------------------------------------------------
# Defining utility command-line interface

an_usage_description = "%prog --image-id=49 --size-id=1"
an_usage_description += common.add_usage_description()
an_usage_description += rackspace.add_usage_description()

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
an_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

an_option_parser.add_option( "--image-id",
                             metavar = "< Rackspace Servers Image ID >",
                             type = "int",
                             action = "store",
                             dest = "image_id",
                             help = "(%default, by default)",
                             default = "49" ) # Ubuntu 10.04 LTS (lucid)
an_option_parser.add_option( "--size-id",
                             metavar = "< Rackspace Servers Size ID >",
                             type = "int",
                             action = "store",
                             dest = "size_id",
                             help = "(%default, by default)",
                             default = "1" ) # RAM 256Mb HDD 10Gb

rackspace.add_parser_options( an_option_parser )
common.add_parser_options( an_option_parser )
    

#--------------------------------------------------------------------------------------
# Extracting and verifying command-line arguments

an_options, an_args = an_option_parser.parse_args()

an_enable_debug = common.extract_options( an_options )
RACKSPACE_USER, RACKSPACE_KEY = rackspace.extract_options( an_options )
an_image_id = an_options.image_id
a_size_id = an_options.size_id


print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
import sys
an_engine = sys.argv[ 0 ]

a_call = "%s --image-id=%d --size-id=%d %s" % ( an_engine, an_image_id, a_size_id, rackspace.compose_call( an_options ) )

print_d( a_call + '\n' )


print_d( "\n----------------------- Running actual functionality ----------------------\n" )
an_instance_reservation_time = Timer()

from libcloud.types import Provider 
from libcloud.providers import get_driver 

Driver = get_driver( Provider.RACKSPACE ) 
a_libcloud_conn = Driver( RACKSPACE_USER, RACKSPACE_KEY ) 
print_d( "a_libcloud_conn = %r\n" % a_libcloud_conn )


#--------------------------------------------------------------------------------------
an_images = a_libcloud_conn.list_images() 
print_list( "an_images :\n" , an_images )

an_image = None
for an_item in an_images :
    if int( an_item.id ) == an_image_id :
       an_image = an_item
       break
    pass

if an_image == None :
    an_option_parser.error( "--image-id='%d' does not exists" % an_image_id )
    pass

print_d( "an_image = %r\n" % an_image )


#--------------------------------------------------------------------------------------
a_sizes = a_libcloud_conn.list_sizes() 
print_list( "a_sizes :\n" , a_sizes )

a_size = None
for an_item in a_sizes :
    if int( an_item.id ) == a_size_id :
       a_size = an_item
       break
    pass

if a_size == None :
    an_option_parser.error( "--size-id='%d' does not exists" % a_size_id )
    pass

print_d( "a_size = %r\n" % a_size )


#--------------------------------------------------------------------------------------
a_node_name = str( uuid.uuid4() )
print_d( "a_node_name = '%s'\n" % a_node_name )

a_node = a_libcloud_conn.create_node( name = a_node_name, image = an_image , size = a_size ) 
print_d( "a_node = %r\n" % a_node )

print_d( "an_instance_reservation_time = %s, sec\n" % an_instance_reservation_time )


print_d( "\n------------------ Printing succussive pipeline arguments -----------------\n" )
a_password = a_node.extra.get( 'password' )
an_identity_file = "" # No identity file
a_host_port = 22
a_login_name = 'root'
a_host_name = a_node.public_ip[ 0 ]

print a_password
print an_identity_file
print a_host_port
print a_login_name
print a_host_name


print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
print_d( a_call + '\n' )
print_d( 'sshpass -p %s ssh -o "StrictHostKeyChecking no" -p %d %s@%s\n' % ( a_password, a_host_port, a_login_name, a_host_name ) )


print_d( "\n-------------------------------------- OK ---------------------------------\n" )
