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


#--------------------------------------------------------------------------------------
"""
This script is responsible for the task packaging and sending it for execution in a cloud
"""


#--------------------------------------------------------------------------------------
def usage_description() :
    return " --instance-ord=0"


#--------------------------------------------------------------------------------------
from cloudflu.preferences import OptionGroup, PersistentOption, TransientOption
a_container = OptionGroup( 'amazon.instance_extract' )

a_container.add_option( TransientOption( "--instance-ord",
                                         metavar = "< order number of the instance in the given reservation >",
                                         type = "int",
                                         action = "store",
                                         dest = "instance_ord",
                                         help = "(%default, by default)",
                                         default = 0 ) )


#--------------------------------------------------------------------------------------
def extract( the_option_parser ) :
    an_options, an_args = the_option_parser.parse_args()

    an_instance_ord = int( an_options.instance_ord )

    return an_instance_ord


#--------------------------------------------------------------------------------------
def compose( the_instance_ord ) :
    return "--instance-ord=%d" % ( the_instance_ord )


#--------------------------------------------------------------------------------------
from cloudflu.preferences import template_add
add = lambda the_option_parser : template_add( the_option_parser, a_container )


#------------------------------------------------------------------------------------------
from cloudflu.preferences import template_dump
dump = lambda the_identation_level, the_output : template_dump( the_identation_level, a_container, the_output )


#------------------------------------------------------------------------------------------
