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
This script helps to perform a command into remote cloud instance through ssh protocol,
  where the main problem is to establish proper connection 
  (server inocation & ssh timeout problems)
"""


#--------------------------------------------------------------------------------------
def usage_description() :
    import cloudflu.common as common

    an_usage_description = ""
    an_usage_description += " [ --script-file='./remote_adjust_profile.sh%s./remote_update_sources-list.sh' ]" % common.arg_list_separator()
    an_usage_description += " [ --sequence-file='./remote_sshd-config.sh' ]"

    return an_usage_description


#--------------------------------------------------------------------------------------
from cloudflu.preferences import OptionGroup, PersistentOption, TransientOption
a_container = OptionGroup( 'common.ssh.run' )

import cloudflu.common as common
a_container.add_option( TransientOption( "--script-file",
                                         metavar = "< script (or list of scripts separated by '%s')"
                                         "or be executed on the remote host >" % common.arg_list_separator(),
                                         action = "store",
                                         dest = "script_file",
                                         default = None ) )

a_container.add_option( TransientOption( "--script-args",
                                         metavar = "< arguments (or list of arguments separated by '%s)"
                                         "or the remote script execution >" % common.arg_list_separator(),
                                         action = "store",
                                         dest = "script_args",
                                         default = None ) )

a_container.add_option( TransientOption( "--sequence-file",
                                         metavar = "< file with sequence of commands to be executed >",
                                         action = "store",
                                         dest = "sequence_file",
                                         default = None ) )


#--------------------------------------------------------------------------------------
def extract( the_option_parser ) :
    import cloudflu.common as common
    an_options, an_args = the_option_parser.parse_args()

    import os.path
    a_scripts = None
    a_script_args = None
    a_script_file = an_options.script_file
    if a_script_file != None :
        # First, check that all appointed scripts exists and regular files
        a_scripts = a_script_file.split( common.arg_list_separator() )
        for a_script in a_scripts :
            if not os.path.isfile( a_script ) :
                an_option_parser.error( "--script-file='%s' must be a file" % a_script )
                pass
            pass

        # Next, check wether number of 'scripts' match number of script's args
        if an_options.script_args != None :
            a_script_args = an_options.script_args.split( common.arg_list_separator() )
            if len( a_script_args ) != len( a_scripts ) :
                an_option_parser.error( "number of items in --script-file='%s'"
                                        " must the same or zero as for --script-args='%s' " 
                                        % ( a_script_files, an_options.script_args ) )
                pass
            pass
        else :
            a_script_args = [ "" for a_script in a_scripts ]
            pass
        pass

    a_sequence_file = an_options.sequence_file
    if a_sequence_file != None :
        a_sequence_file = os.path.abspath( a_sequence_file )
        if not os.path.isfile( a_sequence_file ) :
            an_option_parser.error( "--sequence-file='%s' must be a file" % a_sequence_file )
            pass
        pass

    return a_scripts, a_script_args, a_sequence_file


#--------------------------------------------------------------------------------------
def compose( the_scripts, the_script_args, the_sequence_file ) :
    import cloudflu.common as common
    
    a_compose = ""
    if the_scripts != None :
        a_compose += " --script-file='%s'" % common.print_args( the_scripts, common.arg_list_separator() )
        a_compose += " --script-args='%s'" % common.print_args( the_script_args, common.arg_list_separator() )
        pass
    
    if the_sequence_file != None :
        a_compose = " --sequence-file='%s'" % the_sequence_file
        pass

    return a_compose


#--------------------------------------------------------------------------------------
from cloudflu.preferences import template_add
add = lambda the_option_parser : template_add( the_option_parser, a_container )


#------------------------------------------------------------------------------------------
from cloudflu.preferences import template_dump
dump = lambda the_identation_level, the_output : template_dump( the_identation_level, a_container, the_output )


#------------------------------------------------------------------------------------------
