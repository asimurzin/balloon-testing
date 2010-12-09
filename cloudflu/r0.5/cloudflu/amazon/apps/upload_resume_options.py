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
This script is responsible for efficient uploading of multi file data
"""


#--------------------------------------------------------------------------------------
def usage_description() :
    from cloudflu import common
    
    an_usage_description = ""
    an_usage_description += " --study-name=<my uploaded study>"
    an_usage_description += "[ --located-files='<file path 1>%s<file path 2>..']" % common.arg_list_separator()
    
    return an_usage_description


#--------------------------------------------------------------------------------------
from cloudflu.preferences import OptionGroup, PersistentOption, TransientOption
a_container = OptionGroup( 'amazon.data_transfer.upload_resume' )

a_container.add_option( TransientOption( "--located-files",
                                         metavar = "< the list of file paths inside the study >",
                                         action = "store",
                                         dest = "located_files",
                                         default = None ) )


#--------------------------------------------------------------------------------------
def extract( the_option_parser ) :
    from cloudflu.common import print_d
    an_options, an_args = the_option_parser.parse_args()

    a_located_files = an_options.located_files
    if a_located_files != None :
        from cloudflu import common
        a_located_files = a_located_files.split( common.arg_list_separator() )
        pass

    print_d( "a_located_files = %s\n" % a_located_files )

    return a_located_files


#--------------------------------------------------------------------------------------
def compose( the_located_files ) :
    if the_located_files != None :
        from cloudflu import common
        return " --located-files='%s'" % common.print_args( the_located_files, common.arg_list_separator() )

    return ''


#--------------------------------------------------------------------------------------
from cloudflu.preferences import template_add
add = lambda the_option_parser : template_add( the_option_parser, a_container )


#------------------------------------------------------------------------------------------
from cloudflu.preferences import template_dump
dump = lambda the_identation_level, the_output : template_dump( the_identation_level, a_container, the_output )


#--------------------------------------------------------------------------------------
