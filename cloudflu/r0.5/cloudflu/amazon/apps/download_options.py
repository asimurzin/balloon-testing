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
    from cloudflu import common
    
    an_usage_description = ""
    an_usage_description += " --study-name=<my uploaded study>"
    an_usage_description += "[ --located-files='<file path 1>%s<file path 2>..']" % common.arg_list_separator()
    an_usage_description += " --output-dir='./tmp'"
    
    return an_usage_description


#--------------------------------------------------------------------------------------
from cloudflu.preferences import OptionGroup, PersistentOption, TransientOption
a_container = OptionGroup( 'amazon.data_transfer.download' )

a_container.add_option( TransientOption( "--located-files",
                                         metavar = "< the list of file paths inside the study >",
                                         action = "store",
                                         dest = "located_files",
                                         default = None ) )

a_container.add_option( TransientOption( "--output-dir",
                                         metavar = "< location of the task defintion >",
                                         action = "store",
                                         dest = "output_dir",
                                         help = "(the same a 'study' name, by default)",
                                         default = None ) )

a_container.add_option( PersistentOption( "--fresh",
                                          metavar = "< replace items even if they already exists >",
                                          action = "store_true",
                                          dest = "fresh",
                                          help = "(%default, by default)",
                                          default = False ) )

a_container.add_option( TransientOption( "--wait",
                                         metavar = "< waits for the study uploading completition>",
                                         action = "store_true",
                                         dest = "wait",
                                         help = "(%default, by default)",
                                         default = False ) )

a_container.add_option( PersistentOption( "--remove",
                                          metavar = "< automatically removes from study locally downloaded items >",
                                          action = "store_true",
                                          dest = "remove",
                                          help = "(%default, by default)",
                                          default = False ) )


#--------------------------------------------------------------------------------------
def extract( the_option_parser ) :
    from cloudflu.common import print_d, print_i, print_e
    import os, os.path
    
    an_options, an_args = the_option_parser.parse_args()

    a_located_files = an_options.located_files
    if a_located_files != None :
        from cloudflu import common
        a_located_files = a_located_files.split( common.arg_list_separator() )
        pass

    print_d( "a_located_files = %s\n" % a_located_files )

    an_output_dir = an_options.output_dir
    print_d( "an_output_dir = '%s'\n" % an_output_dir )
    
    a_fresh = an_options.fresh
    print_d( "a_fresh = %s\n" % a_fresh )

    a_wait = an_options.wait
    print_d( "a_wait = %s\n" % a_wait )

    a_remove = an_options.remove
    print_d( "a_remove = %s\n" % a_remove )

    return a_located_files, an_output_dir, a_fresh, a_wait, a_remove


#--------------------------------------------------------------------------------------
def compose( the_located_files, the_output_dir, the_fresh, the_wait, the_remove ) :
    a_compose = ''

    if the_output_dir != None :
        a_compose += " --output-dir='%s'" % the_output_dir
        pass

    if the_located_files != None :
        from cloudflu import common
        a_compose += " --located-files='%s'" % common.print_args( the_located_files, common.arg_list_separator() )
        pass

    if the_fresh == True :
        a_compose += " --fresh"
        pass
        
    if the_wait == True :
        a_compose += " --wait"
        pass
        
    if the_remove == True :
        a_compose += " --remove"
        pass
        
    return a_compose


#--------------------------------------------------------------------------------------
from cloudflu.preferences import template_add
add = lambda the_option_parser : template_add( the_option_parser, a_container )


#------------------------------------------------------------------------------------------
from cloudflu.preferences import template_dump
dump = lambda the_identation_level, the_output : template_dump( the_identation_level, a_container, the_output )


#--------------------------------------------------------------------------------------
