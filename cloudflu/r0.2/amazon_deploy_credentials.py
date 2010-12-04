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
This script upload a file from web and publish it as 'study file' in S3
"""


#--------------------------------------------------------------------------------------
import balloon.common as common
from balloon.common import print_d, print_e, sh_command, Timer
from balloon.common import ssh

from balloon import amazon

import os, os.path


#--------------------------------------------------------------------------------------
# Defining utility command-line interface

an_usage_description = "%prog --remote-location='/mnt'"
an_usage_description += amazon.add_usage_description()
an_usage_description += ssh.add_usage_description()
an_usage_description += common.add_usage_description()

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
a_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

a_option_parser.add_option( "--remote-location",
                            metavar = "< destination of the credendtials environemnt files >",
                            action = "store",
                            dest = "remote_location",
                            help = "(\"%default\", by default)",
                            default = "/mnt" )
a_option_parser.add_option( "--aws-user-id",
                            metavar = "< AWS User ID >",
                            action = "store",
                            dest = "aws_user_id",
                            help = "(\"%default\", by default)",
                            default = os.getenv( "AWS_USER_ID" ) )
a_option_parser.add_option( "--ec2-private-key",
                            metavar = "< EC2 Private Key >",
                            action = "store",
                            dest = "ec2_private_key",
                            help = "(\"%default\", by default)",
                            default = os.getenv( "EC2_PRIVATE_KEY" ) )
a_option_parser.add_option( "--ec2-cert",
                            metavar = "<EC2 Certificate >",
                            action = "store",
                            dest = "ec2_cert",
                            help = "(\"%default\", by default)",
                            default = os.getenv( "EC2_CERT" ) )
amazon.add_parser_options( a_option_parser )
ssh.add_parser_options( a_option_parser )
common.add_parser_options( a_option_parser )
  
 
#--------------------------------------------------------------------------------------
# Extracting and verifying command-line arguments

an_options, an_args = a_option_parser.parse_args()

an_enable_debug = common.extract_options( an_options )
AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.extract_options( an_options )
a_password, an_identity_file, a_host_port, a_login_name, a_host_name, a_command = ssh.extract_options( an_options )

a_remote_location = os.path.abspath( an_options.remote_location )

AWS_USER_ID = an_options.aws_user_id
if AWS_USER_ID == None or AWS_USER_ID == "" :
    a_option_parser.error( "use '--aws-user-id' option to define proper AWS User ID" )
    pass

EC2_PRIVATE_KEY = os.path.abspath( an_options.ec2_private_key )
if not os.path.isfile( EC2_PRIVATE_KEY ) :
    a_option_parser.error( "--ec2-private-key='%s' must be a file" % EC2_PRIVATE_KEY )
    pass

EC2_CERT = os.path.abspath( an_options.ec2_cert )
if not os.path.isfile( EC2_CERT ) :
    a_option_parser.error( "--ec2-cert='%s' must be a file" % EC2_CERT )
    pass

print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
import sys
an_engine = sys.argv[ 0 ]

a_call = "%s --remote-location='%s' %s" % ( an_engine, a_remote_location, ssh.compose_call( an_options ) )

print_d( a_call + '\n' )
ssh.print_call( *ssh.unpack( an_options ) )


print_d( "\n----------------------- Running actual functionality ----------------------\n" )
a_ssh_client = ssh.connect( a_password, an_identity_file, a_host_port, a_login_name, a_host_name )

a_sftp_client = a_ssh_client.open_sftp()
ssh.command( a_ssh_client, 'sudo mkdir --parents %s' % a_remote_location )
ssh.command( a_ssh_client, 'sudo chmod 777 %s' % a_remote_location )
ssh.command( a_ssh_client, 'ls --color=no -alF %s' % a_remote_location )

a_remote_ec2_private_key = os.path.join( a_remote_location, os.path.basename( EC2_PRIVATE_KEY ) )
a_sftp_client.put( EC2_PRIVATE_KEY, a_remote_ec2_private_key )

a_remote_ec2_cert = os.path.join( a_remote_location, os.path.basename( EC2_CERT ) )
a_sftp_client.put( EC2_CERT, a_remote_ec2_cert )

a_remote_rcfile = os.path.join( a_remote_location, ".aws_credentialsrc")
ssh.command( a_ssh_client, 'echo "# AWS Credentials" > %s' % ( a_remote_rcfile ) )
ssh.command( a_ssh_client, 'echo "# ---------------" >> %s' % ( a_remote_rcfile ) )
ssh.command( a_ssh_client, 'echo "export AWS_ACCESS_KEY_ID=%s" >> %s' % ( AWS_ACCESS_KEY_ID, a_remote_rcfile ) )
ssh.command( a_ssh_client, 'echo "export AWS_SECRET_ACCESS_KEY=%s" >> %s' % ( AWS_SECRET_ACCESS_KEY, a_remote_rcfile ) )
ssh.command( a_ssh_client, 'echo "export AWS_USER_ID=%s" >> %s' % ( AWS_USER_ID, a_remote_rcfile ) )
ssh.command( a_ssh_client, 'echo "export EC2_PRIVATE_KEY=%s" >> %s' % ( a_remote_ec2_private_key, a_remote_rcfile ) )
ssh.command( a_ssh_client, 'echo "export EC2_CERT=%s" >> %s' % ( a_remote_ec2_cert, a_remote_rcfile ) )

ssh.command( a_ssh_client, 'source %s && env | grep -E "AWS|EC2"' % ( a_remote_rcfile ) )
ssh.command( a_ssh_client, 'cat %s' % ( a_remote_rcfile ) )

a_ssh_client.close()


print_d( "\n------------------ Printing succussive pipeline arguments -----------------\n" )
ssh.print_options( *ssh.unpack( an_options ) )


print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
ssh.print_call( *ssh.unpack( an_options ) )
print_d( a_call + '\n' )


print_d( "\n-------------------------------------- OK ---------------------------------\n" )

