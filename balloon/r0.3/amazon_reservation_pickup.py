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

an_usage_description = "%prog"
an_usage_description += ec2.use.add_usage_description()
an_usage_description += amazon.add_usage_description()
an_usage_description += common.add_usage_description()

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
an_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

ec2.use.add_parser_options( an_option_parser )
amazon.add_parser_options( an_option_parser )
common.add_parser_options( an_option_parser )
  
 
#--------------------------------------------------------------------------------------
# Extracting and verifying command-line arguments

an_options, an_args = an_option_parser.parse_args()

an_enable_debug = common.extract_options( an_options )
AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.extract_options( an_options )

an_image_location = an_options.image_location
a_reservation_id = an_options.reservation_id
an_identity_file = an_options.identity_file
a_host_port = an_options.host_port
a_login_name = an_options.login_name


print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
import sys
an_engine = sys.argv[ 0 ]

a_call = "%s %s" % ( an_engine, ec2.use.compose_call( an_options ) )
print_d( a_call + '\n' )


print_d( "\n----------------------- Running actual functionality ----------------------\n" )
a_spent_time = Timer()

import boto.ec2
a_target_reservation = None
for a_region in boto.ec2.regions( aws_access_key_id = AWS_ACCESS_KEY_ID, aws_secret_access_key = AWS_SECRET_ACCESS_KEY ) :
    if an_image_location != None and a_region.name != an_image_location :
        continue
    
    print_d( 'a_region = "%s"\n' % a_region.name )

    an_ec2_conn = a_region.connect()
    for a_reservation in an_ec2_conn.get_all_instances() :
        if a_reservation.id == a_reservation_id or a_reservation_id == None :
            an_instance = a_reservation.instances[ 0 ]
            a_status = an_instance.update()
            if a_status == 'terminated' :
                continue

            a_target_reservation = a_reservation
            a_reservation_id = a_reservation.id

            an_image_location = a_region.name

            if an_identity_file == None :
                import os.path; a_key_pair_dir = os.path.expanduser( "~/.ssh")
                an_identity_file = os.path.join( a_key_pair_dir, an_instance.key_name ) + os.path.extsep + "pem"
                pass
            
            break
        pass

    if a_target_reservation != None :
        break

    pass


if a_target_reservation == None :
    print_d( "\n-------------------- There are no running reservations --------------------\n" )
    import sys, os; sys.exit( os.EX_UNAVAILABLE )
    pass

  
print_d( "\n------------------ Printing succussive pipeline arguments -----------------\n" )
ec2.use.print_options( an_image_location, a_reservation_id, an_identity_file, a_host_port, a_login_name )


print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
print_d( a_call + '\n' )


print_d( "\n-------------------------------------- OK ---------------------------------\n" )
