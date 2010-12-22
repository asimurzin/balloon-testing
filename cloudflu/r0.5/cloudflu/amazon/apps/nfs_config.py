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
This script is responsible for cluster environment setup for the given Amazon EC2 reservation
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
    an_usage_description += ec2.use.options.usage_description()

    from cloudflu import VERSION
    a_version = "%s" % VERSION
    
    from optparse import IndentedHelpFormatter
    a_help_formatter = IndentedHelpFormatter( width = 127 )

    from optparse import OptionParser
    an_option_parser = OptionParser( usage = an_usage_description, version = a_version, formatter = a_help_formatter )


    #----------------------- Definition of the command line arguments ------------------------
    ec2.use.options.add( an_option_parser )
    
    amazon.security_options.add( an_option_parser )
    
    common.options.add( an_option_parser )
  
 
    #------------------ Extracting and verifying command-line arguments ----------------------
    an_options, an_args = an_option_parser.parse_args()
    
    common.options.extract( an_option_parser )
   
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.security_options.extract( an_option_parser )
    
    a_cluster_id = ec2.use.options.extract( an_option_parser )
   
    from cloudflu.preferences import get
    a_cluster_location = get( 'amazon.cluster.location' )
    a_host_port = int( get( 'amazon.cluster.host_port' ) )
    a_login_name = get( 'amazon.cluster.login_name' )


    print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
    import sys; an_engine = sys.argv[ 0 ]
   
    a_call = "%s %s" % ( an_engine, ec2.use.options.compose( a_cluster_id ) )
    print_d( a_call + '\n' )
   

    print_d( "\n----------------------- Running actual functionality ----------------------\n" )
    a_spent_time = Timer()
   
    an_ec2_conn = ec2.common.region_connect( a_cluster_location, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )

    a_reservation = ec2.use.get_reservation( an_ec2_conn, a_cluster_id )
    print_d( '< %r > : %s\n' % ( a_reservation, a_reservation.instances ) )
   
    a_security_group = ec2.use.get_security_group( an_ec2_conn, a_reservation )
    print_d( "< %r > : %s\n" % ( a_security_group, a_security_group.rules ) )

    an_instance2ssh = {}
    for an_instance in a_reservation.instances :
        a_password = None
        an_identity_file = ec2.run.get_identity_filepath( an_instance.key_name )
        a_host_name = an_instance.public_dns_name
        ssh.options.echo( a_password, an_identity_file, a_host_port, a_login_name, a_host_name )
    
        a_ssh_client = ssh.connect( a_password, an_identity_file, a_host_port, a_login_name, a_host_name )
        an_instance2ssh[ an_instance ] = a_ssh_client
       
        ssh.command( a_ssh_client, 'sudo apt-get install -y nfs-common portmap nfs-kernel-server' ) # install server and client packages
       
        try:
            a_security_group.authorize( 'tcp', 111, 111, '%s/0' % an_instance.private_ip_address ) # for rpcbind
            a_security_group.authorize( 'tcp', 2049, 2049, '%s/0' % an_instance.private_ip_address ) # for nfs over tcp
            a_security_group.authorize( 'udp', 35563, 35563, '%s/0' % an_instance.private_ip_address ) # for nfs over udp
        except :
            pass
        pass

    [ a_ssh_client.close() for a_ssh_client in an_instance2ssh.values() ]
    
    print_d( "a_spent_time = %s, sec\n" % a_spent_time )
    
    
    print_d( "\n------------------ Printing succussive pipeline arguments -----------------\n" )
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
