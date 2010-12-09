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
Lists all reservation avaialble for the current location
"""


#--------------------------------------------------------------------------------------
import cloudflu.common as common
from cloudflu.common import print_d, print_e, sh_command, Timer
from cloudflu.common import ssh

from cloudflu import amazon
from cloudflu.amazon import ec2


#--------------------------------------------------------------------------------------
def main() :
    #----------------------- Defining utility command-line interface -------------------------    
    an_usage_description = "%prog"

    from cloudflu import VERSION
    a_version = "%s" % VERSION
    
    from optparse import IndentedHelpFormatter
    a_help_formatter = IndentedHelpFormatter( width = 127 )
    
    from optparse import OptionParser
    an_option_parser = OptionParser( usage = an_usage_description, version = a_version, formatter = a_help_formatter )
    

    #----------------------- Definition of the command line arguments ------------------------
    amazon.security_options.add( an_option_parser )
    
    common.options.add( an_option_parser )
  

    #------------------ Extracting and verifying command-line arguments ----------------------
    an_options, an_args = an_option_parser.parse_args()
    
    common.options.extract( an_option_parser )
    
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.security_options.extract( an_option_parser )

    from cloudflu.preferences import get
    a_cluster_location = get( 'amazon.cluster.location' )


    print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
    import sys; an_engine = sys.argv[ 0 ]

    a_call = "%s" % ( an_engine )
    print_d( a_call + '\n' )


    print_d( "\n----------------------- Running actual functionality ----------------------\n" )
    a_spent_time = Timer()

    import boto.ec2
    an_ec2_conn = boto.ec2.connect_to_region( a_cluster_location,
                                              aws_access_key_id = AWS_ACCESS_KEY_ID,
                                              aws_secret_access_key = AWS_SECRET_ACCESS_KEY )

    for a_reservation in an_ec2_conn.get_all_instances() :
        an_instance = a_reservation.instances[ 0 ]
        a_status = an_instance.update()
        if a_status == 'terminated' or a_status == 'shutting-down' :
            continue
        
        print a_reservation.id
        
        pass


    print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
    print_d( a_call + '\n' )
    

    print_d( "\n-------------------------------------- OK ---------------------------------\n" )
    pass


#------------------------------------------------------------------------------------------
if __name__ == '__main__' :
    main()
    pass


#------------------------------------------------------------------------------------------
