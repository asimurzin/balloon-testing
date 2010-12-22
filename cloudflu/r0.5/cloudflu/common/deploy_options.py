

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
    return " [--production]"


#--------------------------------------------------------------------------------------
from cloudflu.preferences import OptionGroup, PersistentOption, TransientOption
a_container = OptionGroup( 'common.install' )

a_container.add_option( PersistentOption( "--production",
                                          metavar = "< deploy official production version >",
                                          action = "store_true",
                                          dest = "production",
                                          help = "(%default, by default)",
                                          default = True ) )

a_container.add_option( PersistentOption( "--url",
                                          metavar = "< package name or precise location to download from >",
                                          action = "store",
                                          dest = "url",
                                          help = "('%default', by default)",
                                          default = 'cloudflu' ) )


#--------------------------------------------------------------------------------------
def extract( the_option_parser ) :
    an_options, an_args = the_option_parser.parse_args()

    a_production = an_options.production

    an_url = an_options.url

    return a_production, an_url


#--------------------------------------------------------------------------------------
def compose( the_production, the_url ) :
    if the_production == True :
        return "--production --url='%s'" % the_url

    return ""


#--------------------------------------------------------------------------------------
from cloudflu.preferences import template_add
add = lambda the_option_parser : template_add( the_option_parser, a_container )


#------------------------------------------------------------------------------------------
from cloudflu.preferences import template_dump
dump = lambda the_identation_level, the_output : template_dump( the_identation_level, a_container, the_output )


#------------------------------------------------------------------------------------------
