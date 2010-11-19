#!/usr/bin/env python

#------------------------------------------------------------------------------------------
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
Deletes all SQS resources
"""

#------------------------------------------------------------------------------------------
import boto
import boto.ec2

import balloon.common as common
from balloon.common import print_d, print_i, print_e, sh_command, Timer, WorkerPool

import balloon.amazon as amazon


#------------------------------------------------------------------------------------------
# Defining utility command-line interface
an_usage_description = "%prog"
an_usage_description += common.add_usage_description()
an_usage_description += amazon.add_usage_description()

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
a_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

# Definition of the command line arguments
common.add_parser_options( a_option_parser )
amazon.add_parser_options( a_option_parser )


#------------------------------------------------------------------------------------------
# Extracting and verifying command-line arguments

an_options, an_args = a_option_parser.parse_args()

common.extract_options( an_options )

AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.extract_options( an_options )


print_d( "\n----------------------------- Delete SQS queues ---------------------------\n" )
a_sqs_conn = boto.connect_sqs( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
for a_queue in a_sqs_conn.get_all_queues() :
    print "'%s' : %d" % ( a_queue.name, a_queue.count() )
    a_queue.clear()
    a_queue.delete()
    pass

print


print_d( "\n-------------------------------------- OK ---------------------------------\n" )

