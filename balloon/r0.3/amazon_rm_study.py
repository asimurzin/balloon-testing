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
Removes whole appointed cloud study or just given files from this study
"""

#------------------------------------------------------------------------------------------
import balloon.common as common
from balloon.common import print_d, print_i, print_e, sh_command
from balloon.common import Timer, WorkerPool, compute_md5

import balloon.amazon as amazon
from balloon.amazon.s3 import TRootObject, TStudyObject, TFileObject, TSeedObject

import sys, os, os.path, uuid, hashlib


#------------------------------------------------------------------------------------------
# Defining utility command-line interface
an_usage_description = "%prog <study1> <study2>"
an_usage_description += common.add_usage_description()
an_usage_description += amazon.add_usage_description()
an_usage_description += amazon.add_timeout_usage_description()
an_usage_description += amazon.add_threading_usage_description()

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
a_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

# Definition of the command line arguments
common.add_parser_options( a_option_parser, True )
amazon.add_parser_options( a_option_parser )
amazon.add_timeout_options( a_option_parser )
amazon.add_threading_parser_options( a_option_parser )


#------------------------------------------------------------------------------------------
# Extracting and verifying command-line arguments

an_options, an_args = a_option_parser.parse_args()

a_study_names = None
if len( an_args ) == 0 :
    a_study_names = [ raw_input() ]
else :
    a_study_names = an_args
    pass

common.extract_options( an_options )

AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.extract_options( an_options )

a_number_threads = amazon.extract_threading_options( an_options, a_option_parser )

amazon.extract_timeout_options( an_options, a_option_parser )


print_i( "--------------------------- Looking for study object ----------------------------\n" )
a_root_object = TRootObject.get( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
print_d( "a_root_object = %s\n" % a_root_object )

for a_study_name in a_study_names :
    a_study_object = TStudyObject.get( a_root_object, a_study_name )
    print_d( "a_study_object = %s\n" % a_study_object )

    print_i( "------------------------------- Removing study ----------------------------------\n" )
    a_study_object.delete()

    pass

print_i( "-------------------------------------- OK ---------------------------------------\n" )
