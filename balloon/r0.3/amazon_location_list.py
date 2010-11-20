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
Lists the all avaialble Amazon AWS locations
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
an_usage_description += amazon.add_usage_description()
an_usage_description += common.add_usage_description()

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
an_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

amazon.add_parser_options( an_option_parser )
common.add_parser_options( an_option_parser )
  
 
#--------------------------------------------------------------------------------------
# Extracting and verifying command-line arguments

an_options, an_args = an_option_parser.parse_args()

an_enable_debug = common.extract_options( an_options )
AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.extract_options( an_options )


print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
import sys; an_engine = sys.argv[ 0 ]

a_call = "%s" % ( an_engine )
print_d( a_call + '\n' )


print_d( "\n----------------------- Running actual functionality ----------------------\n" )
a_spent_time = Timer()

import boto.ec2
for a_region in boto.ec2.regions( aws_access_key_id = AWS_ACCESS_KEY_ID, aws_secret_access_key = AWS_SECRET_ACCESS_KEY ) :
    print a_region.name
    
    pass
  
print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
print_d( a_call + '\n' )


print_d( "\n-------------------------------------- OK ---------------------------------\n" )
