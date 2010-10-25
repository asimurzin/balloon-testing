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


#--------------------------------------------------------------------------------------
"""
This script is responsible for cluster environment setup for the given Amazon EC2 reservation
"""


#--------------------------------------------------------------------------------------
import balloon.common as common
from balloon.common import print_d, print_e, sh_command, Timer

from balloon import amazon
from balloon.amazon import ec2


#--------------------------------------------------------------------------------------
# Defining utility command-line interface

an_usage_description = "%prog"
an_usage_description += ec2.use.add_usage_description()
an_usage_description += amazon.add_usage_description()
an_usage_description += common.add_usage_description()

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
an_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

ec2.use.add_parser_options( an_option_parser )
amazon.add_parser_options( an_option_parser )
common.add_parser_options( an_option_parser )
  
 
#--------------------------------------------------------------------------------------
# Extracting and verifying command-line arguments

an_options, an_args = an_option_parser.parse_args()

an_enable_debug = common.extract_options( an_options )
AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.extract_options( an_options )
an_image_location, a_reservation_id, an_identity_file, a_host_port, a_login_name = ec2.use.extract_options( an_options )


print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
import sys
an_engine = sys.argv[ 0 ]

a_call = "%s %s %s" % ( an_engine, ec2.use.compose_call( an_options ), amazon.compose_call( an_options ) )
print_d( a_call + '\n' )


print_d( "\n----------------------- Running actual functionality ----------------------\n" )
a_spent_time = Timer()

an_ec2_conn = ec2.region_connect( an_image_location, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
a_reservation = ec2.use.get_reservation( an_ec2_conn, a_reservation_id )
a_security_group = ec2.use.get_security_group( an_ec2_conn, a_reservation )

a_password = "" # No password
an_identity_file = an_identity_file
a_host_port = a_host_port
a_login_name = a_login_name


print_d( "\n-------------------- Providing seamless ssh connection --------------------\n" )
from balloon.common import ssh
an_instance_2_ssh_client = {}
for an_instance in a_reservation.instances :
    a_host_name = an_instance.public_dns_name
    print_d( 'ssh -o "StrictHostKeyChecking no" -i %s -p %d %s@%s\n' % ( an_identity_file, a_host_port, a_login_name, a_host_name ) )
        
    a_ssh_client = ssh.connect( a_password, an_identity_file, a_host_port, a_login_name, a_host_name )
    a_sftp_client = a_ssh_client.open_sftp()

    import os
    an_upload_name = os.path.basename( an_identity_file )
    a_sftp_client.put( an_identity_file, an_upload_name )

    a_target_name = '${HOME}/.ssh/id_rsa'
    ssh.command( a_ssh_client, 'mv -f %s %s' % ( an_upload_name, a_target_name ) )
    ssh.command( a_ssh_client, 'chmod 600 %s' % ( a_target_name ) )
    ssh.command( a_ssh_client, """sudo sh -c 'echo "    StrictHostKeyChecking no" >> /etc/ssh/ssh_config'""" )

    try :
        a_security_group.authorize( 'tcp', 1, 65535, '%s/0' % an_instance.private_ip_address ) # mpi cluster ports
    except :
        pass

    an_instance_2_ssh_client[ an_instance ] = a_ssh_client, a_sftp_client
    pass

print_d( "\n--- Listing all the cluster nodes into special '.openmpi_hostfile' file ---\n" )
# The suggested cluster conffiguration is symmetric,
# which means that it does not matter who will be the master node.
# (if user need to do something special, he can do it from his own machine)
for a_master_node in a_reservation.instances :
    a_host_name = a_master_node.public_dns_name

    a_ssh_client, a_sftp_client = an_instance_2_ssh_client[ a_master_node ]
    ssh.command( a_ssh_client, 'echo %s > .openmpi_hostfile' % ( a_master_node.private_ip_address ) )

    for an_instance in a_reservation.instances :
        if an_instance == a_master_node :
            continue
        ssh.command( a_ssh_client, 'echo %s >> .openmpi_hostfile' % ( an_instance.private_ip_address ) )
        pass

    pass

[ a_ssh_client.close() for a_ssh_client, a_sftp_client in an_instance_2_ssh_client.values() ]

print_d( "a_spent_time = %s, sec\n" % a_spent_time )


print_d( "\n------------------ Printing succussive pipeline arguments -----------------\n" )
ec2.use.print_options( *ec2.use.unpack( an_options ) )


print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
print_d( a_call + '\n' )


print_d( "\n-------------------------------------- OK ---------------------------------\n" )
