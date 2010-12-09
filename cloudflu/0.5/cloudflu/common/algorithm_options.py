

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


#------------------------------------------------------------------------------------------
def dump( the_identation_level, the_output ) :
    from cloudflu.preferences import OptionGroup
    a_container = OptionGroup( 'common.algorithm' )

    from cloudflu.preferences import dump_begin, dump_resume, dump_end
    dump_begin( the_identation_level, a_container, the_output )

    import concurrency_options
    dump_resume( the_identation_level, concurrency_options.a_container, the_output )
    
    import communication_options
    dump_resume( the_identation_level, communication_options.a_container, the_output )

    dump_end( the_identation_level, a_container, the_output )
    pass


#------------------------------------------------------------------------------------------
