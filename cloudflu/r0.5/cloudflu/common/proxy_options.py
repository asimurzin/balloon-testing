

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
from cloudflu.preferences import OptionGroup, PersistentOption, TransientOption
a_container = OptionGroup( 'common.proxy' )

a_container.add_option( PersistentOption( "--proxy-address",
                                          metavar = "< The proxy server address >",
                                          type = "str",
                                          action = "store",
                                          dest = "proxy_address",
                                          help = "(%default, by default)",
                                          default = None ) )

a_container.add_option( PersistentOption( "--proxy-port",
                                          metavar = "< The proxy server port >",
                                          type = "int",
                                          action = "store",
                                          dest = "proxy_port",
                                          help = "(%default, by default)",
                                          default = None ) )


a_container.add_option( PersistentOption( "--proxy-user",
                                          metavar = "< The proxy server user >",
                                          type = "str",
                                          action = "store",
                                          dest = "proxy_user",
                                          help = "(%default, by default)",
                                          default = None ) )


a_container.add_option( PersistentOption( "--proxy-pass",
                                          metavar = "< The proxy server password >",
                                          type = "str",
                                          action = "store",
                                          dest = "proxy_pass",
                                          help = "(%default, by default)",
                                          default = None ) )


#--------------------------------------------------------------------------------------
def extract( the_option_parser ) :
    an_options, an_args = the_option_parser.parse_args()

    a_proxy_address = an_options.proxy_address
    a_proxy_port = an_options.proxy_port
    a_proxy_user = an_options.proxy_user
    a_proxy_pass = an_options.proxy_pass
    
    return a_proxy_address, a_proxy_port, a_proxy_user, a_proxy_pass


#--------------------------------------------------------------------------------------
from cloudflu.preferences import template_add
add = lambda the_option_parser : template_add( the_option_parser, a_container )


#------------------------------------------------------------------------------------------
from cloudflu.preferences import template_dump
dump = lambda the_identation_level, the_output : template_dump( the_identation_level, a_container, the_output )


#------------------------------------------------------------------------------------------
