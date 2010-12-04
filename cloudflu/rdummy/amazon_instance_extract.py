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
from balloon.common import ssh

from balloon import amazon
from balloon.amazon import ec2


#--------------------------------------------------------------------------------------
# Defining utility command-line interface

an_usage_description = "%prog --instance-id=0"
an_usage_description += ec2.use.add_usage_description()
an_usage_description += amazon.add_usage_description()
an_usage_description += common.add_usage_description()

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
an_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

an_option_parser.add_option( "--instance-id",
                             metavar = "< order number of the instance in the given reservation >",
                             type = "int",
                             action = "store",
                             dest = "instance_id",
                             help = "(%default, by default)",
                             default = 0 )
ec2.use.add_parser_options( an_option_parser )
amazon.add_parser_options( an_option_parser )
common.add_parser_options( an_option_parser )
  
 
#--------------------------------------------------------------------------------------
# Extracting and verifying command-line arguments

an_options, an_args = an_option_parser.parse_args()

an_enable_debug = common.extract_options( an_options )
AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.extract_options( an_options )
an_image_location, a_reservation_id, an_identity_file, a_host_port, a_login_name = ec2.use.extract_options( an_options )
an_instance_id = an_options.instance_id


print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
import sys
an_engine = sys.argv[ 0 ]

a_call = "%s --instance-id=%d %s %s" % ( an_engine, an_instance_id, ec2.use.compose_call( an_options ), amazon.compose_call( an_options ) )
print_d( a_call + '\n' )


print_d( "\n----------------------- Running actual functionality ----------------------\n" )
a_spent_time = Timer()

an_ec2_conn = ec2.region_connect( an_image_location, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
a_reservation = ec2.use.get_reservation( an_ec2_conn, a_reservation_id )
an_instance = a_reservation.instances[ an_instance_id ]
print_d( 'an_instance = %s\n' % an_instance )


print_d( "\n------------------ Printing succussive pipeline arguments -----------------\n" )
a_password = "" # No password
an_identity_file = an_identity_file
a_host_port = a_host_port
a_login_name = a_login_name
a_host_name = an_instance.public_dns_name

ssh.print_options( a_password, an_identity_file, a_host_port, a_login_name, a_host_name )


print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
ssh.print_call( a_password, an_identity_file, a_host_port, a_login_name, a_host_name )
print_d( a_call + '\n' )


print_d( "\n-------------------------------------- OK ---------------------------------\n" )
