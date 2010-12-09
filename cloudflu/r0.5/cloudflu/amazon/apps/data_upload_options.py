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
## See http://sourceforge.net/apps/mediawiki/cloudflu
##
## Author : Alexey Petrov
##


#------------------------------------------------------------------------------------------
"""
This script is responsible for efficient downloading of multi file data
"""


#--------------------------------------------------------------------------------------
def usage_description() :
    return " [--booked]"


#--------------------------------------------------------------------------------------
from cloudflu.preferences import OptionGroup, PersistentOption, TransientOption
a_container = OptionGroup( 'amazon.data_transfer.upload' )

a_container.add_option( TransientOption( "--booked",
                                         metavar = "< use already existing study >",
                                         action = "store_true",
                                         dest = "booked",
                                         help = "(%default, by default)",
                                         default = False ) )

#--------------------------------------------------------------------------------------
def extract( the_option_parser ) :
    from cloudflu.common import print_d
    an_options, an_args = the_option_parser.parse_args()

    a_booked = an_options.booked
    print_d( "a_booked = %s\n" % a_booked )

    return a_booked


#--------------------------------------------------------------------------------------
def compose( the_booked ) :
    a_compose = ''

    if the_booked == True :
        a_compose += " --booked"
        pass
        
    return a_compose


#--------------------------------------------------------------------------------------
from cloudflu.preferences import template_add
add = lambda the_option_parser : template_add( the_option_parser, a_container )


#--------------------------------------------------------------------------------------
