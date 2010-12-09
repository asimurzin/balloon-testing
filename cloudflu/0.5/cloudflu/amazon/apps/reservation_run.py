#!/usr/bin/env python

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
This script is responsible for the task packaging and sending it for execution in a cloud
"""


#--------------------------------------------------------------------------------------
import cloudflu.common as common
from cloudflu.common import print_d, print_e, sh_command, Timer

from cloudflu import amazon
from cloudflu.amazon import ec2


#--------------------------------------------------------------------------------------
def main() :
    #----------------------- Defining utility command-line interface -------------------------    
    an_usage_description = "%prog"
    an_usage_description += ec2.ami.run_options.usage_description()

    from cloudflu import VERSION
    a_version = "%s" % VERSION

    from optparse import IndentedHelpFormatter
    a_help_formatter = IndentedHelpFormatter( width = 127 )

    from optparse import OptionParser
    an_option_parser = OptionParser( usage = an_usage_description, version = a_version, formatter = a_help_formatter )


    #----------------------- Definition of the command line arguments ------------------------
    ec2.ami.run_options.add( an_option_parser )
    
    amazon.security_options.add( an_option_parser )

    common.options.add( an_option_parser )
  
 
    #------------------ Extracting and verifying command-line arguments ----------------------
    an_options, an_args = an_option_parser.parse_args()

    common.options.extract( an_option_parser )

    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.security_options.extract( an_option_parser )

    an_instance_type, an_image_id, a_number_nodes = ec2.ami.run_options.extract( an_option_parser )

    from cloudflu.preferences import get
    a_cluster_location = get( 'amazon.cluster.location' )
    a_host_port = get( 'amazon.cluster.host_port' )
    

    print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
    import sys; an_engine = sys.argv[ 0 ]

    a_call = "%s %s" % ( an_engine, 
                         ec2.ami.run_options.compose( an_instance_type, an_image_id, a_number_nodes ) )
    print_d( a_call + '\n' )


    print_d( "\n----------------------- Running actual functionality ----------------------\n" )
    a_spent_time = Timer()

    a_reservation, an_identity_file = ec2.run.run_reservation( an_image_id, a_cluster_location, an_instance_type, 
                                                               a_number_nodes, a_number_nodes, a_host_port,
                                                               AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )

    print_d( "a_spent_time = %s, sec\n" % a_spent_time )
    

    print_d( "\n------------------ Printing succussive pipeline arguments -----------------\n" )
    a_cluster_location = a_reservation.region.name
    a_cluster_id = a_reservation.id
    
    ec2.use.options.track( a_cluster_id )


    print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
    print_d( a_call + '\n' )


    print_d( "\n-------------------------------------- OK ---------------------------------\n" )
    pass


#------------------------------------------------------------------------------------------
if __name__ == '__main__' :
    main()
    pass


#------------------------------------------------------------------------------------------
