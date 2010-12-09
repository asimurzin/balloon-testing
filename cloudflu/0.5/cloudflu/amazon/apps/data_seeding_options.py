

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
    return " --upload-seed-size=5160"


#--------------------------------------------------------------------------------------
from cloudflu.preferences import OptionGroup, PersistentOption, TransientOption
a_container = OptionGroup( 'amazon.data_transfer.upload' )

a_container.add_option( PersistentOption( "--upload-seed-size",
                                          metavar = "< size of file pieces to be uploaded, in bytes >",
                                          type = "int",
                                          action = "store",
                                          dest = "upload_seed_size",
                                          help = "(%default, by default)",
                                          default = 65536 ) )


#--------------------------------------------------------------------------------------
def extract( the_option_parser ) :
    from cloudflu.common import print_d, print_i, print_e
    
    an_options, an_args = the_option_parser.parse_args()

    an_upload_seed_size = an_options.upload_seed_size
    print_d( "an_upload_seed_size = %d, bytes\n" % an_upload_seed_size )

    return an_upload_seed_size


#--------------------------------------------------------------------------------------
def compose( the_upload_seed_size ) :
    return "--upload-seed-size=%d" % the_upload_seed_size


#--------------------------------------------------------------------------------------
from cloudflu.preferences import template_add
add = lambda the_option_parser : template_add( the_option_parser, a_container )


#------------------------------------------------------------------------------------------
