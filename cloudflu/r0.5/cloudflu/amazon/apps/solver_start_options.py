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
This script is responsible for cluster environment setup for the given Amazon EC2 reservation
"""


#--------------------------------------------------------------------------------------
def usage_description() :
    return " --case-dir='~/damBreak' --run-hook='Allrun'"


#--------------------------------------------------------------------------------------
from cloudflu.preferences import OptionGroup, PersistentOption, TransientOption
a_container = OptionGroup( 'amazon.solver' )

a_container.add_option( TransientOption( "--case-dir",
                                         metavar = "< location of the source OpenFOAM case dir >",
                                         action = "store",
                                         dest = "case_dir",
                                         default = None ) )

a_container.add_option( PersistentOption( "--run-hook",
                                          metavar = "< case dir executable in to be run in the cluster >",
                                          action = "store",
                                          dest = "run_hook",
                                          help = "('%default', by default)",
                                          default = 'Allrun' ) )


#--------------------------------------------------------------------------------------
def extract( the_option_parser ) :
    an_options, an_args = the_option_parser.parse_args()

    if an_options.case_dir == None :
        the_option_parser.error( "Use '--case-dir' option to define folder containing solver case\n" )
        pass

    import os.path; a_case_dir = os.path.abspath( os.path.expanduser( an_options.case_dir ) )
    if not os.path.isdir( a_case_dir ) :
        the_option_parser.error( "--case-dir='%s' should be a folder\n" % a_case_dir )
        pass

    a_run_hook = an_options.run_hook
    import os.path; a_run_path = os.path.join( a_case_dir, a_run_hook )
    import stat; an_is_exec = stat.S_IMODE( os.stat( a_run_path )[ 0 ] ) & stat.S_IXGRP
    if not os.path.isfile( a_run_path ) or not an_is_exec :
        the_option_parser.error( "--run-hook='%s' should be an executable\n" % a_run_hook )
        pass


    return a_case_dir, a_run_hook


#--------------------------------------------------------------------------------------
def compose( the_case_dir, the_run_hook ) :
    a_compose = "--case-dir='%s' --run-hook='%s'" % ( the_case_dir, the_run_hook )

    return a_compose


#--------------------------------------------------------------------------------------
from cloudflu.preferences import template_add
add = lambda the_option_parser : template_add( the_option_parser, a_container )


#------------------------------------------------------------------------------------------
from cloudflu.preferences import template_dump
dump = lambda the_identation_level, the_output : template_dump( the_identation_level, a_container, the_output )


#------------------------------------------------------------------------------------------
