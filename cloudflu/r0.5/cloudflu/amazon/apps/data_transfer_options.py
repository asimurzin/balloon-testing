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
    return " --study-name=< user study name >"


#--------------------------------------------------------------------------------------
from cloudflu.preferences import OptionGroup, PersistentOption, TransientOption
a_container = OptionGroup( 'amazon.data_transfer' )

a_container.add_option( TransientOption( "--study-name",
                                         metavar = "< existing study name >",
                                         action = "store",
                                         dest = "study_name",
                                         help = "(read from standard input, if not given)",
                                         default = None ) )

#--------------------------------------------------------------------------------------
def extract( the_option_parser ) :
    from cloudflu.common import print_d
    an_options, an_args = the_option_parser.parse_args()

    a_study_name = an_options.study_name
    if a_study_name == None :
        from cloudflu.preferences import get_raw_input
        a_study_name, an_args = get_raw_input()
        pass

    if a_study_name == None :
        the_option_parser.error( "--study-name is not defined\n" )
        pass

    print_d( "a_study_name = '%s'\n" % a_study_name )

    return a_study_name


#--------------------------------------------------------------------------------------
def compose( the_study_name ) :
    return "--study-name='%s'" % the_study_name


#--------------------------------------------------------------------------------------
from cloudflu.preferences import template_add
add = lambda the_option_parser : template_add( the_option_parser, a_container )


#------------------------------------------------------------------------------------------
def dump( the_identation_level, the_output ) :
    a_container.add_option( PersistentOption( "--data-location",
                                              metavar = "< location of the data : 'EU', ''( us-east ), 'us-west-1' or 'ap-southeast-1' >",
                                              choices = [ 'EU', '', 'us-west-1', 'ap-southeast-1' ],
                                              action = "store",
                                              dest = "location",
                                              help = "'%default', by default ",
                                              default = '' ) )

    from cloudflu.preferences import dump_begin
    dump_begin( the_identation_level, a_container, the_output )

    import upload_options; upload_options.dump( the_identation_level + 1, the_output )
    import download_options; download_options.dump( the_identation_level + 1, the_output )

    from cloudflu.preferences import dump_end
    dump_end( the_identation_level, a_container, the_output )
    pass


#--------------------------------------------------------------------------------------
