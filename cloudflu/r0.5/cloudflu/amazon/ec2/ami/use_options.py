
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
from cloudflu.preferences import OptionGroup, PersistentOption, TransientOption
a_container = OptionGroup( 'amazon.cluster' )

a_container.add_option( PersistentOption( "--login-name",
                                          metavar = "< specifies the user to log in as on the remote machine >",
                                          action = "store",
                                          dest = "login_name",
                                          help = "(\"%default\", by default)",
                                          default = 'ubuntu' ) )

a_container.add_option( PersistentOption( "--host-port",
                                          metavar = "< port to ssh >",
                                          type = "int",
                                          action = "store",
                                          dest = "host_port",
                                          help = "(%default, by default)",
                                          default = 22 ) )


#--------------------------------------------------------------------------------------
def extract( the_option_parser ) :
    from cloudflu.preferences import get_input
    an_options, an_args = the_option_parser.parse_args()

    a_login_name = an_options.login_name
    if a_login_name == None :
        a_login_name, an_args = get_input( an_args )
        pass

    return a_login_name


#--------------------------------------------------------------------------------------
from cloudflu.preferences import template_add
add = lambda the_option_parser : template_add( the_option_parser, a_container )


#------------------------------------------------------------------------------------------
from cloudflu.preferences import template_dump
dump = lambda the_identation_level, the_output : template_dump( the_identation_level, a_container, the_output )


#--------------------------------------------------------------------------------------
