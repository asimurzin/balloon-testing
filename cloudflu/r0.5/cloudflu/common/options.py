

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
    return " --debug"


#--------------------------------------------------------------------------------------
from cloudflu.preferences import OptionGroup, PersistentOption, TransientOption
a_container = OptionGroup( 'common' )

a_container.add_option( PersistentOption( "--debug",
                                          metavar = "< print debug information >",
                                          action = "store_true",
                                          dest = "enable_debug",
                                          help = "(%default, by default)",
                                          default = False ) )

a_container.add_option( PersistentOption( "--log-file",
                                          metavar = "< file to write debug inforamtion >",
                                          action = "store",
                                          dest = "log_file",
                                          help = "('%default', by default)",
                                          default = "~/cloudflu.log" ) )


#--------------------------------------------------------------------------------------
ENABLE_DEBUG = True

def extract( the_option_parser ) :
    from cloudflu.common import print_d
    an_options, an_args = the_option_parser.parse_args()

    global ENABLE_DEBUG

    an_enable_debug = an_options.enable_debug
    
    import os
    if os.getenv( "__CLOUDFLU_DEBUG_ENABLE__" ) != None :
        an_enable_debug = True
        pass

    ENABLE_DEBUG = an_enable_debug

    a_log_file = an_options.log_file

    import os.path
    a_log_file = os.path.expanduser( a_log_file )
    a_log_file = os.path.abspath( a_log_file )
    if os.path.exists( a_log_file ) :
        import shutil
        shutil.rmtree( a_log_file, True )
        pass

    import logging
    logging.basicConfig( filename = a_log_file, level = logging.DEBUG )

    return an_enable_debug, a_log_file


#--------------------------------------------------------------------------------------
def is_debug() :
    return ENABLE_DEBUG != None and ENABLE_DEBUG == True


#--------------------------------------------------------------------------------------
from cloudflu.preferences import template_add
add = lambda the_option_parser : template_add( the_option_parser, a_container )


#------------------------------------------------------------------------------------------
def dump( the_identation_level, the_output ) :
    from cloudflu.preferences import dump_begin
    dump_begin( the_identation_level, a_container, the_output )

    # import proxy_options; proxy_options.dump( the_identation_level + 1, the_output )
    
    import algorithm_options; algorithm_options.dump( the_identation_level + 1, the_output )
    
    import deploy_options; deploy_options.dump( the_identation_level + 1, the_output )
    
    import ssh.options; ssh.options.dump( the_identation_level + 1, the_output )
    
    from cloudflu.preferences import dump_end
    dump_end( the_identation_level, a_container, the_output )
    pass


#------------------------------------------------------------------------------------------
