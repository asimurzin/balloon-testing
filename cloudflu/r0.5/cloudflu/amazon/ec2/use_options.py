

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
from cloudflu.common import print_e, print_d, Timer

import os, os.path


#--------------------------------------------------------------------------------------
def usage_description() :
    return " --cluster-id='r-8cc1dfe7'"


#--------------------------------------------------------------------------------------
from cloudflu.preferences import OptionGroup, PersistentOption, TransientOption
a_container = OptionGroup( 'amazon.ec2.use' )

a_container.add_option( TransientOption( "--cluster-id",
                                          metavar = "< cluster identifier >",
                                          action = "store",
                                          dest = "cluster_id",
                                          help = "(read from standard input, if not given)",
                                          default = None ) )


#--------------------------------------------------------------------------------------
def extract( the_option_parser ) :
    an_options, an_args = the_option_parser.parse_args()

    a_cluster_id = an_options.cluster_id
    if a_cluster_id == None :
        from cloudflu.preferences import get_input
        a_cluster_id, an_args = get_input( an_args )
        pass
    
    if a_cluster_id == None :
        the_option_parser.error( "--cluster-id is not defined\n" )
        pass

    print_d( "a_cluster_id = '%s'\n" % a_cluster_id )

    return a_cluster_id


#--------------------------------------------------------------------------------------
def compose( the_cluster_id ) :
    return "--cluster-id='%s'" % ( the_cluster_id )


#--------------------------------------------------------------------------------------
def track( the_cluster_id ) :
    print the_cluster_id    
    pass


#--------------------------------------------------------------------------------------
from cloudflu.preferences import template_add
add = lambda the_option_parser : template_add( the_option_parser, a_container )


#------------------------------------------------------------------------------------------
from cloudflu.preferences import template_dump
dump = lambda the_identation_level, the_output : template_dump( the_identation_level, a_container, the_output )


#--------------------------------------------------------------------------------------
