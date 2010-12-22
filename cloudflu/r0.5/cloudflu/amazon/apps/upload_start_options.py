

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
Contains the package dedicated preferences
"""


#--------------------------------------------------------------------------------------
def usage_description() :
    from cloudflu import common

    an_usage_description = " --file-locations='< file1 location >%s< file2 location >..'" % common.arg_list_separator()
    an_usage_description += " < file 1 > < folder 2 > .."
    
    return an_usage_description


#--------------------------------------------------------------------------------------
from cloudflu.preferences import OptionGroup, PersistentOption, TransientOption
a_container = OptionGroup( 'amazon.data_transfer.upload' )

a_container.add_option( TransientOption( "--file-locations",
                                         metavar = "< location of files inside of the study >",
                                         action = "store",
                                         dest = "file_locations",
                                         help = "('%default', by default)",
                                         default = '' ) )


#--------------------------------------------------------------------------------------
def extract( the_option_parser ) :
    from cloudflu.common import print_d, print_i, print_e
    
    an_options, an_args = the_option_parser.parse_args()

    from cloudflu.preferences import get_inputs
    a_source_files = get_inputs( an_args )
    print_d( "a_source_files = %s\n" % a_source_files )

    a_files = list()
    for a_file in a_source_files :
        import os.path
        if not os.path.exists( a_file ) :
            the_option_parser.error( "The given file ('%s') should exists\n" % a_file )
            pass
        a_files.append( os.path.abspath( a_file ) )
        pass
    
    if len( a_files ) == 0 :
        the_option_parser.error( "You should define one valid 'file' at least\n" )
        pass

    print_d( "a_files = %r\n" % a_files )
    
    from cloudflu import common
    a_file_locations = an_options.file_locations
    a_file_locations = a_file_locations.split( common.arg_list_separator() )

    a_file2locations = {}
    if len( a_file_locations ) > 1 :
        if len( a_files ) != len( a_file_locations ) :
            the_option_parser.error( "The amount of file locations shoudl be equal to the number of given files\n" )
            pass
        else :
            for an_id in range( len( a_files ) ) :
                a_file = a_files[ an_id ]
                a_location = a_file_locations[ an_id ]
                a_file2locations[ a_file ] = a_location
                pass
            pass
        pass
    else :
        a_location = a_file_locations[ 0 ]
        for a_file in a_files:
            a_file2locations[ a_file ] = a_location
            pass
        pass   
    
    print_d( "a_file2locations = %r\n" % a_file2locations )

    return a_file2locations


#--------------------------------------------------------------------------------------
from cloudflu.preferences import template_add
add = lambda the_option_parser : template_add( the_option_parser, a_container )


#------------------------------------------------------------------------------------------
