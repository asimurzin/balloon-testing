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
This script is responsible for the deployng of the 'balloon' package into appointed cloud instance
"""


#--------------------------------------------------------------------------------------
import balloon.common as common
from balloon.common import print_d, print_e, sh_command, Timer
from balloon.common import ssh


#--------------------------------------------------------------------------------------
# Defining utility command-line interface

an_usage_description = "%prog"
an_usage_description += ssh.add_usage_description()
an_usage_description += common.add_usage_description()

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
a_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

ssh.add_parser_options( a_option_parser )
common.add_parser_options( a_option_parser )
  
 
#--------------------------------------------------------------------------------------
# Extracting and verifying command-line arguments

an_options, an_args = a_option_parser.parse_args()

an_enable_debug = common.extract_options( an_options )
a_password, an_identity_file, a_host_port, a_login_name, a_host_name, a_command = ssh.extract_options( an_options )

print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
import sys
an_engine = sys.argv[ 0 ]

a_call = "%s %s" % ( an_engine, ssh.compose_call( an_options ) )

print_d( a_call + '\n' )
ssh.print_call( a_password, an_identity_file, a_host_port, a_login_name, a_host_name )


print_d( "\n----------------------- Running actual functionality ----------------------\n" )
a_ssh_client = ssh.connect( a_password, an_identity_file, a_host_port, a_login_name, a_host_name )

import os, tempfile
a_working_dir = tempfile.mkdtemp()
print_d( "a_working_dir = %s\n" % a_working_dir )

import os.path
an_engine_dir = os.path.abspath( os.path.dirname( an_engine ) )
sh_command( "cd %s && ./setup.py sdist" % an_engine_dir )

import balloon
a_balloon_name = "%s-%s" % ( balloon.NAME, balloon.VERSION )
a_balloon_archive_name = a_balloon_name + os.extsep + "tar.gz"
a_balloon_source_archive = os.path.join( an_engine_dir, 'dist', a_balloon_archive_name )
a_balloon_target_archive = os.path.join( a_working_dir, a_balloon_archive_name )

# Instantiating a sftp client
a_sftp_client = a_ssh_client.open_sftp()

ssh.command( a_ssh_client, 'mkdir %s' % a_working_dir )

# Uploading and installing into the cloud corresponding Python engine (itself)
a_sftp_client.put( a_balloon_source_archive, a_balloon_target_archive )
ssh.command( a_ssh_client, 'cd %s && tar -xzf %s' % ( a_working_dir, a_balloon_archive_name ) )
a_balloon_setup_dir = os.path.join( a_working_dir, a_balloon_name )
ssh.command( a_ssh_client, 'cd %s && sudo python ./setup.py install' % ( a_balloon_setup_dir ) )

import shutil
shutil.rmtree( a_working_dir ) # Cleaning temporal working folder

a_ssh_client.close()


print_d( "\n------------------ Printing succussive pipeline arguments -----------------\n" )
ssh.print_options( a_password, an_identity_file, a_host_port, a_login_name, a_host_name )


print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
ssh.print_call( a_password, an_identity_file, a_host_port, a_login_name, a_host_name )
print_d( a_call + '\n' )


print_d( "\n-------------------------------------- OK ---------------------------------\n" )

