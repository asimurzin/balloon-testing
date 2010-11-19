#!/usr/bin/env python

#------------------------------------------------------------------------------------------
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
## See http://sourceforge.net/apps/mediawiki/balloon-foam
##
## Author : Alexey Petrov
##


#------------------------------------------------------------------------------------------
"""
Deletes all running Amazon EC2 reservations and release all resources incorporated by them
"""

#------------------------------------------------------------------------------------------
import boto
import boto.ec2

import balloon.common as common
from balloon.common import print_d, print_i, print_e, sh_command, Timer, WorkerPool

import balloon.amazon as amazon


#------------------------------------------------------------------------------------------
# Defining utility command-line interface
an_usage_description = "%prog"
an_usage_description += common.add_usage_description()
an_usage_description += amazon.add_usage_description()

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
a_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

# Definition of the command line arguments
common.add_parser_options( a_option_parser )
amazon.add_parser_options( a_option_parser )


#------------------------------------------------------------------------------------------
# Extracting and verifying command-line arguments

an_options, an_args = a_option_parser.parse_args()

common.extract_options( an_options )

AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.extract_options( an_options )


#------------------------------------------------------------------------------------------
def stop_instance( the_instance ) :
    a_status = the_instance.update()
    if a_status != 'terminated' :
        print "%s : %s : '%s'" % ( the_instance, a_status, the_instance.dns_name )
        the_instance.stop()

        pass

    pass


#------------------------------------------------------------------------------------------
def delete_key_pair( the_key_pair ) :
    print the_key_pair.name

    # an_ec2_conn.delete_key_pair( the_key_pair ) # Does not work (bug)
    the_key_pair.delete()

    import os.path
    a_key_pair_dir = os.path.expanduser( "~/.ssh")
    a_key_pair_file = os.path.join( a_key_pair_dir, the_key_pair.name ) + os.path.extsep + "pem"

    if os.path.isfile( a_key_pair_file ) :
        os.remove( a_key_pair_file )
        pass
    
    pass


#------------------------------------------------------------------------------------------
def delete_security_group( the_ec2_conn, the_security_group ) :
    if the_security_group.name != 'default' :
        print the_security_group.name
        the_ec2_conn.delete_security_group( the_security_group.name )
        
        pass
    pass


#------------------------------------------------------------------------------------------
a_worker_pool = WorkerPool( 8 )

for a_region in boto.ec2.regions( aws_access_key_id = AWS_ACCESS_KEY_ID, aws_secret_access_key = AWS_SECRET_ACCESS_KEY ) :
    an_ec2_conn = a_region.connect()
    print a_region

    print_d( "\n--------------------------- Delete EC2 instances --------------------------\n" )
    for a_reservation in an_ec2_conn.get_all_instances() :
        for an_instance in a_reservation.instances :
            # a_worker_pool.charge( stop_instance, ( an_instance ) )
            stop_instance( an_instance )
            pass
        pass
    print
    a_worker_pool.join()

    print_d( "\n--------------------------- Delete EC2 key pairs --------------------------\n" )
    for a_key_pair in an_ec2_conn.get_all_key_pairs() :
        # a_worker_pool.charge( delete_key_pair, ( a_key_pair ) )
        delete_key_pair( a_key_pair )
        pass
    print


    print_d( "\n------------------------ Delete EC2 security groups -----------------------\n" )
    for a_security_group in an_ec2_conn.get_all_security_groups() :
        # a_worker_pool.charge( delete_security_group, ( an_ec2_conn, a_security_group ) )
        delete_security_group( an_ec2_conn, a_security_group )
        pass
    print

    a_worker_pool.join()
    pass


a_worker_pool.shutdown()
a_worker_pool.join()


print_d( "\n-------------------------------------- OK ---------------------------------\n" )


