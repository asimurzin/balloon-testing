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
This script upload a file from web and publish it as 'study file' in S3
"""


#--------------------------------------------------------------------------------------
import cloudflu.common as common
from cloudflu.common import print_d, print_e, sh_command, Timer
from cloudflu.common import ssh

import credentials_deploy_options

from cloudflu import amazon

import os, os.path


#--------------------------------------------------------------------------------------
def main() :
    #----------------------- Defining utility command-line interface -------------------------    
    an_usage_description = "%prog"

    an_usage_description += credentials_deploy_options.usage_description()

    an_usage_description += ssh.options.usage_description()
    
    from cloudflu import VERSION
    a_version = "%s" % VERSION

    from optparse import IndentedHelpFormatter
    a_help_formatter = IndentedHelpFormatter( width = 127 )

    from optparse import OptionParser
    an_option_parser = OptionParser( usage = an_usage_description, version = a_version, formatter = a_help_formatter )


    #----------------------- Definition of the command line arguments ------------------------
    credentials_deploy_options.add( an_option_parser )

    ssh.options.add( an_option_parser )
    
    amazon.security_options.add( an_option_parser )
    
    common.options.add( an_option_parser )
  

    #------------------ Extracting and verifying command-line arguments ----------------------
    an_options, an_args = an_option_parser.parse_args()

    common.options.extract( an_option_parser )

    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.security_options.extract( an_option_parser )

    a_password, an_identity_file, a_host_port, a_login_name, a_host_name, a_command = ssh.options.extract( an_option_parser )

    AWS_USER_ID, EC2_PRIVATE_KEY, EC2_CERT, a_remote_location = credentials_deploy_options.extract( an_option_parser )

    
    print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
    import sys; an_engine = sys.argv[ 0 ]

    a_call = "%s %s %s" % ( an_engine, 
                            credentials_deploy_options.compose( AWS_USER_ID, EC2_PRIVATE_KEY, EC2_CERT, a_remote_location ),
                            ssh.options.compose( a_password, an_identity_file, a_host_port, a_login_name, a_host_name ) )
    print_d( a_call + '\n' )
    ssh.options.echo( a_password, an_identity_file, a_host_port, a_login_name, a_host_name )


    print_d( "\n----------------------- Running actual functionality ----------------------\n" )
    a_ssh_client = ssh.connect( a_password, an_identity_file, a_host_port, a_login_name, a_host_name, a_command )
    import os.path; a_remote_dir = os.path.dirname( a_remote_location )
    ssh.command( a_ssh_client, 'sudo mkdir --parents %s' % a_remote_dir )
    ssh.command( a_ssh_client, 'sudo chmod 777 %s' % a_remote_dir )

    a_sftp_client = a_ssh_client.open_sftp()

    ssh.command( a_ssh_client, 'echo "export AWS_ACCESS_KEY_ID=%s" > %s' % ( AWS_ACCESS_KEY_ID, a_remote_location ) )
    ssh.command( a_ssh_client, 'echo "export AWS_SECRET_ACCESS_KEY=%s" >> %s' % ( AWS_SECRET_ACCESS_KEY, a_remote_location ) )

    if AWS_USER_ID != None :
        ssh.command( a_ssh_client, 'echo "export AWS_USER_ID=%s" >> %s' % ( AWS_USER_ID, a_remote_location ) )
        pass

    if EC2_PRIVATE_KEY != None :
        a_remote_ec2_private_key = os.path.join( a_remote_dir, os.path.basename( EC2_PRIVATE_KEY ) )
        a_sftp_client.put( EC2_PRIVATE_KEY, a_remote_ec2_private_key )
        ssh.command( a_ssh_client, 'echo "export EC2_PRIVATE_KEY=%s" >> %s' % ( a_remote_ec2_private_key, a_remote_location ) )
        pass

    if EC2_CERT != None :
        a_remote_ec2_cert = os.path.join( a_remote_dir, os.path.basename( EC2_CERT ) )
        a_sftp_client.put( EC2_CERT, a_remote_ec2_cert )
        ssh.command( a_ssh_client, 'echo "export EC2_CERT=%s" >> %s' % ( a_remote_ec2_cert, a_remote_location ) )
        pass

    ssh.command( a_ssh_client, 'sudo ln -s %s /etc/profile.d/aws_credentials.sh' % ( a_remote_location ) )
    ssh.command( a_ssh_client, 'env | grep -E "AWS|EC2"' )
    
    a_ssh_client.close()
    
    
    print_d( "\n------------------ Printing succussive pipeline arguments -----------------\n" )
    ssh.options.track( a_password, an_identity_file, a_host_port, a_login_name, a_host_name )
    
    
    print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
    ssh.options.echo( a_password, an_identity_file, a_host_port, a_login_name, a_host_name )
    print_d( a_call + '\n' )


    print_d( "\n-------------------------------------- OK ---------------------------------\n" )
    pass


#------------------------------------------------------------------------------------------
if __name__ == '__main__' :
    main()
    pass


#------------------------------------------------------------------------------------------
