

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
a_container = OptionGroup( 'amazon.cluster' )

a_container.add_option( PersistentOption( "--cluster-location",
                                          metavar = "< location of the cluster nodes : 'eu-west-1', 'us-east-1', 'us-west-1' or 'ap-southeast-1' >",
                                          choices = [ 'eu-west-1', 'us-east-1', 'us-west-1', 'ap-southeast-1' ],
                                          action = "store",
                                          dest = "location",
                                          help = "('%default', by default)",
                                          default = 'us-east-1' ) )


#------------------------------------------------------------------------------------------
def dump( the_identation_level, the_output ) :
    from cloudflu.preferences import dump_begin, dump_resume, dump_end
    dump_begin( the_identation_level, a_container, the_output )

    from ami import run_options
    dump_resume( the_identation_level, run_options.a_container, the_output )
    
    from ami import use_options
    dump_resume( the_identation_level, use_options.a_container, the_output )
    
    dump_end( the_identation_level, a_container, the_output )
    pass


#------------------------------------------------------------------------------------------
