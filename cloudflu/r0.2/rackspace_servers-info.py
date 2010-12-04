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
from balloon.common import print_d, print_list, print_e, sh_command, wait_ssh, Timer

import balloon.rackspace as rackspace

import sys, os, os.path, uuid


#--------------------------------------------------------------------------------------
# Defining utility command-line interface

an_usage_description = "%prog"
an_usage_description += common.add_usage_description()
an_usage_description += rackspace.add_usage_description()

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
an_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

rackspace.add_parser_options( an_option_parser )
common.add_parser_options( an_option_parser )
    

#--------------------------------------------------------------------------------------
# Extracting and verifying command-line arguments

an_options, an_args = an_option_parser.parse_args()

an_enable_debug = common.extract_options( an_options )
RACKSPACE_USER, RACKSPACE_KEY = rackspace.extract_options( an_options )


print_d( "\n----------------------- Running actual functionality ----------------------\n" )
an_instance_reservation_time = Timer()

from libcloud.types import Provider 
from libcloud.providers import get_driver 

Driver = get_driver( Provider.RACKSPACE ) 
a_libcloud_conn = Driver( RACKSPACE_USER, RACKSPACE_KEY ) 
print_d( "a_libcloud_conn = %r\n" % a_libcloud_conn )

an_images = a_libcloud_conn.list_images() 
print_list( "an_images :\n" , an_images )

a_sizes = a_libcloud_conn.list_sizes() 
print_list( "a_sizes :\n" , a_sizes )


print_d( "\n-------------------------------------- OK ---------------------------------\n" )
