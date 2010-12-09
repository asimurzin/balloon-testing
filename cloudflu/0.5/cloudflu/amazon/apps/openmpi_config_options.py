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
## See http://sourceforge.net/apps/mediawiki/cloudflu
##
## Author : Alexey Petrov
##


#------------------------------------------------------------------------------------------
"""
Removes whole appointed cloud study or just given files from this study
"""

#--------------------------------------------------------------------------------------
def usage_description() :
    return " --hostfile='/tmp/.openmpi_hostfile'"


#------------------------------------------------------------------------------------------
from cloudflu.preferences import OptionGroup, PersistentOption, TransientOption
a_container = OptionGroup( 'amazon.openmpi_config' )

a_container.add_option( PersistentOption( "--hostfile",
                                          metavar = "< location of the MPI 'hostfile' >",
                                          action = "store",
                                          dest = "hostfile",
                                          help = "(\"%default\", by default)",
                                          default = '/tmp/.openmpi_hostfile' ) )


#------------------------------------------------------------------------------------------
def extract( the_option_parser ) :
    an_options, an_args = the_option_parser.parse_args()

    a_hostfile = an_options.hostfile
    from cloudflu.common import print_d
    print_d( "a_hostfile = '%s'\n" % a_hostfile )

    return a_hostfile


#--------------------------------------------------------------------------------------
def compose( the_hostfile ) :
    return "--hostfile='%s'" % the_hostfile


#--------------------------------------------------------------------------------------
from cloudflu.preferences import template_add
add = lambda the_option_parser : template_add( the_option_parser, a_container )


#------------------------------------------------------------------------------------------
from cloudflu.preferences import template_dump
dump = lambda the_identation_level, the_output : template_dump( the_identation_level, a_container, the_output )


#--------------------------------------------------------------------------------------
