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
from balloon.common import print_d, print_e, sh_command, Timer

from balloon import amazon
from balloon.amazon import ec2


#--------------------------------------------------------------------------------------
# Defining utility command-line interface

an_usage_description = "%prog"
an_usage_description += ec2.run.add_usage_description()
an_usage_description += amazon.add_usage_description()
an_usage_description += common.add_usage_description()

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
an_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

ec2.run.add_parser_options( an_option_parser )
amazon.add_parser_options( an_option_parser )
common.add_parser_options( an_option_parser )
  
 
#--------------------------------------------------------------------------------------
# Extracting and verifying command-line arguments

an_options, an_args = an_option_parser.parse_args()

an_enable_debug = common.extract_options( an_options )
AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.extract_options( an_options )
an_image_id, an_image_location, an_instance_type, a_min_count, a_max_count, a_host_port = ec2.run.extract_options( an_options )


print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
import sys
an_engine = sys.argv[ 0 ]

a_call = "%s %s %s" % ( an_engine, ec2.run.compose_call( an_options ), amazon.compose_call( an_options ) )
print_d( a_call + '\n' )


print_d( "\n----------------------- Running actual functionality ----------------------\n" )
a_spent_time = Timer()

a_reservation, an_identity_file = ec2.run.run_reservation( an_image_id, an_image_location, an_instance_type, 
                                                           a_min_count, a_max_count, a_host_port,
                                                           AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )

print_d( "a_spent_time = %s, sec\n" % a_spent_time )


print_d( "\n------------------ Printing succussive pipeline arguments -----------------\n" )
ec2.use.print_options( a_reservation.region.name, a_reservation.id, an_identity_file, a_host_port )


print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
print_d( a_call + '\n' )


print_d( "\n-------------------------------------- OK ---------------------------------\n" )

