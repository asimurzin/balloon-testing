

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
    return " --socket-timeout=2"


#--------------------------------------------------------------------------------------
from cloudflu.preferences import OptionGroup, PersistentOption, TransientOption
a_container = OptionGroup( 'common.algorithm' )

a_container.add_option( PersistentOption( "--socket-timeout",
                                          metavar = "< socket timeout >",
                                          type = "int",
                                          action = "store",
                                          dest = "socket_timeout",
                                          help = "(%default, by default)",
                                          default = 7 ) )


#--------------------------------------------------------------------------------------
def extract( the_option_parser ) :
    an_options, an_args = the_option_parser.parse_args()

    a_socket_timeout = an_options.socket_timeout
    import socket; socket.setdefaulttimeout( a_socket_timeout )

    return a_socket_timeout


#--------------------------------------------------------------------------------------
from cloudflu.preferences import template_add
add = lambda the_option_parser : template_add( the_option_parser, a_container )


#------------------------------------------------------------------------------------------
from cloudflu.preferences import template_dump
dump = lambda the_identation_level, the_output : template_dump( the_identation_level, a_container, the_output )


#------------------------------------------------------------------------------------------
