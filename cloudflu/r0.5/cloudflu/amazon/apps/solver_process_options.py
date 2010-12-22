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
    return " --output-dir='~/damBreak 2010-11-23 16:23' --before-hook='cloudflu-foam2vtk-before' --time-hook='cloudflu-foam2vtk' --after-hook='cloudflu-foam2vtk-after'"


#--------------------------------------------------------------------------------------
from cloudflu.preferences import OptionGroup, PersistentOption, TransientOption
a_container = OptionGroup( 'amazon.solver' )

a_container.add_option( TransientOption( "--output-dir",
                                         metavar = "< folder suffix for the output results >",
                                         action = "store",
                                         dest = "output_dir",
                                         help = "(%default, by default)",
                                         default = None ) )

a_container.add_option( PersistentOption( "--before-hook",
                                          metavar = "< executable to be run 'before' any results will be downloaded >",
                                          action = "store",
                                          dest = "before_hook",
                                          help = "('do nothing', by default)",
                                          default = None ) )

a_container.add_option( PersistentOption( "--time-hook",
                                          metavar = "< executable to be run on each timestamp download >",
                                          action = "store",
                                          dest = "time_hook",
                                          help = "('do nothing', by default)",
                                          default = None ) )

a_container.add_option( PersistentOption( "--after-hook",
                                          metavar = "< executable to be run 'after' all results will be downloaded >",
                                          action = "store",
                                          dest = "after_hook",
                                          help = "('do nothing', by default)",
                                          default = None ) )


#--------------------------------------------------------------------------------------
def extract( the_option_parser, the_case_dir = None ) :
    from cloudflu.common import print_d
    an_options, an_args = the_option_parser.parse_args()

    an_output_dir = an_options.output_dir
    if an_output_dir == None :
        if the_case_dir != None :
            import time; an_output_dir = '%s %s' % ( the_case_dir, time.strftime('%Y-%m-%d %H:%M') )
        else:
            the_option_parser.error( "--output-dir='%s' is not defined\n" % an_output_dir )
            pass
        pass
    
    import os.path; an_output_dir = os.path.abspath( os.path.expanduser( an_output_dir ) )
    print_d( "an_output_dir = '%s'\n" % an_output_dir )

    a_before_hook = an_options.before_hook
    a_time_hook = an_options.time_hook
    an_after_hook = an_options.after_hook

    return an_output_dir, a_before_hook, a_time_hook, an_after_hook


#--------------------------------------------------------------------------------------
def compose( the_output_dir, the_before_hook, the_time_hook, the_after_hook ) :
    a_compose = "--output-dir='%s'" % ( the_output_dir )

    if the_before_hook != None :
        a_compose += " --before-hook='%s'" % the_before_hook
        pass

    if the_time_hook != None :
        a_compose += " --time-hook='%s'" % the_time_hook
        pass

    if the_after_hook != None :
        a_compose += " --after-hook='%s'" % the_after_hook
        pass

    return a_compose


#--------------------------------------------------------------------------------------
from cloudflu.preferences import template_add
add = lambda the_option_parser : template_add( the_option_parser, a_container )


#------------------------------------------------------------------------------------------
from cloudflu.preferences import template_dump
dump = lambda the_identation_level, the_output : template_dump( the_identation_level, a_container, the_output )


#------------------------------------------------------------------------------------------
