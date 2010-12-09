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
Cleans all nodes from cloudservers and cloudfiles that correspond to defined rackspace account
"""

#--------------------------------------------------------------------------------------
import cloudflu.common as common
from cloudflu.common import print_d, print_i, print_e
from cloudflu.common import Timer, WorkerPool

import cloudflu.amazon as amazon


#--------------------------------------------------------------------------------------
def terminate_instance( the_instance ) :
    a_status = the_instance.update()
    if a_status != 'terminated' :
        print_d( "%s : %s : '%s'\n" % ( the_instance, a_status, the_instance.dns_name ) )
        the_instance.terminate()

        pass

    pass


#--------------------------------------------------------------------------------------
def delete_key_pair( the_key_pair ) :
    print_d( the_key_pair.name )

    # an_ec2_conn.delete_key_pair( the_key_pair ) # Does not work (bug)
    the_key_pair.delete()

    import os, os.path
    a_key_pair_dir = os.path.expanduser( "~/.ssh")
    a_key_pair_file = os.path.join( a_key_pair_dir, the_key_pair.name ) + os.path.extsep + "pem"

    if os.path.isfile( a_key_pair_file ) :
        os.remove( a_key_pair_file )
        pass
    
    pass


#--------------------------------------------------------------------------------------
def delete_security_group( the_ec2_conn, the_security_group ) :
    if the_security_group.name != 'default' :
        print_d( the_security_group.name )

        the_ec2_conn.delete_security_group( the_security_group.name )
        pass
    pass


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


    print_i( "-------------------------- Running actual functionality -------------------------\n" )
    import boto.ec2
    for a_region in boto.ec2.regions( aws_access_key_id = AWS_ACCESS_KEY_ID, aws_secret_access_key = AWS_SECRET_ACCESS_KEY ) :
        an_ec2_conn = a_region.connect()
        print_d( "region - '%s'" % a_region.name )


        print_i( "------------------------------- Delete EC2 instances ----------------------------\n" )
        for a_reservation in an_ec2_conn.get_all_instances() :
            for an_instance in a_reservation.instances :
                terminate_instance( an_instance )
                pass
            pass

        print_i( "------------------------------- Delete EC2 key pairs ----------------------------\n" )
        for a_key_pair in an_ec2_conn.get_all_key_pairs() :
            delete_key_pair( a_key_pair )
            pass


        print_i( "---------------------------- Delete EC2 security groups -------------------------\n" )
        for a_security_group in an_ec2_conn.get_all_security_groups() :
            delete_security_group( an_ec2_conn, a_security_group )
            pass

        pass


    print_i( "-------------------------------------- OK ---------------------------------------\n" )
    pass


#------------------------------------------------------------------------------------------
if __name__ == '__main__' :
    main()
    pass


#------------------------------------------------------------------------------------------
