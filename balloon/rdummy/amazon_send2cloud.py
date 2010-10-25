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
This script is responsible for the task packaging and sending it for execution in a cloud
"""


#--------------------------------------------------------------------------------------
import balloon.common as common
from balloon.common import print_d, print_e, sh_command, ssh_command, Timer

import balloon.amazon as amazon
from balloon.amazon import wait_activation, wait_ssh

import sys, os, os.path, uuid


#--------------------------------------------------------------------------------------
# Defining utility command-line interface

an_usage_description = "%prog --task-control-dir=~/rackspace/control --task-control-dir=~/rackspace/data"
an_usage_description += common.add_usage_description()
an_usage_description += amazon.add_usage_description()

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
a_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

# Definition of the command line arguments
a_option_parser.add_option( "--task-control-dir",
                            metavar = "< location of the task 'control' scripts >",
                            action = "store",
                            dest = "task_control_dir",
                            help = "(\"%default\", by default)",
                            default = "./amazon_control" )

a_option_parser.add_option( "--task-data-dir",
                            metavar = "< location of the task 'data' >",
                            action = "store",
                            dest = "task_data_dir",
                            help = "(\"%default\", by default)",
                            default = "./data" )

common.add_parser_options( a_option_parser )

amazon.add_parser_options( a_option_parser )
    
an_engine_dir = os.path.abspath( os.path.dirname( sys.argv[ 0 ] ) )


print_d( "\n---------------------------------------------------------------------------\n" )
# Extracting and verifying command-line arguments

an_options, an_args = a_option_parser.parse_args()

common.extract_options( an_options )

import os.path
a_task_control_dir = os.path.abspath( an_options.task_control_dir )
if not os.path.isdir( a_task_control_dir ) :
    print_e( "The task 'control' should a be directory\n" )
    pass

a_launch_script = os.path.join( a_task_control_dir, "launch" )
if not os.path.isfile( a_launch_script ) :
    print_e( "The task 'control' should contain 'launch' start-up script\n" )
    pass

a_task_data_dir = os.path.abspath( an_options.task_data_dir )
if not os.path.isdir( a_task_data_dir ) :
    print_e( "The task 'data' should a be directory\n" )
    pass

AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.extract_options( an_options )


print_d( "\n---------------------------------------------------------------------------\n" )
# Packaging of the local data

import os, tempfile
a_working_dir = tempfile.mkdtemp()
print_d( "a_working_dir = %s\n" % a_working_dir )

# Packaging the 'control' scripts
a_control_name = "task_control.tgz"
a_control_archive = os.path.join( a_working_dir, a_control_name )
sh_command( "cd %s && tar --exclude-vcs -czf %s *" % ( a_task_control_dir, a_control_archive ) )

# Packaging the task data
a_data_name = "task_data.tgz"
a_data_archive = os.path.join( a_working_dir, a_data_name )
sh_command( "cd %s && tar --exclude-vcs -czf %s *" % ( a_task_data_dir, a_data_archive ) )

# Packaging Python engine (itself)
sh_command( "cd %s && ./setup.py sdist" % an_engine_dir )
a_balloon_name = "balloon-0.5-alfa"
a_balloon_archive_name = a_balloon_name + os.extsep + "tar.gz"
a_balloon_source_archive = os.path.join( an_engine_dir, 'dist', a_balloon_archive_name )
a_balloon_target_archive = os.path.join( a_working_dir, a_balloon_archive_name )


print_d( "\n---------------------------------------------------------------------------\n" )
# Uploading task data into cloud
a_data_loading_time = Timer()

import boto
a_s3_conn = boto.connect_s3( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
print_d( "a_s3_conn = %r\n" % a_s3_conn )
print_d( "a_s3_conn.get_canonical_user_id() = %s\n" % a_s3_conn.get_canonical_user_id() )

a_bucket_name = str( uuid.uuid4() )
a_s3_bucket = a_s3_conn.create_bucket( a_bucket_name )
print_d( "a_s3_bucket = %s\n" % a_s3_bucket.name )

from boto.s3.key import Key
a_s3_bucket_key = Key( a_s3_bucket )
a_s3_bucket_key.key = a_data_name
a_s3_bucket_key.set_contents_from_filename( a_data_archive )
print_d( "a_s3_bucket_key = %s\n" % a_s3_bucket_key.name )

print_d( "a_data_loading_time = %s, sec\n" % a_data_loading_time )


print_d( "\n---------------------------------------------------------------------------\n" )
# Instanciating node in cloud
an_instance_reservation_time = Timer()

import boto
# Establish an connection with EC2
an_ec2_conn = boto.connect_ec2()
print_d( '%r\n' % an_ec2_conn )

# Choose an image to be run
an_image_ids = "ami-2d4aa444"
# an_image_ids = "ami-fd4aa494" # 64-bit version
an_images = an_ec2_conn.get_all_images( image_ids = an_image_ids )
an_image = an_images[ 0 ]
print_d( '%s\n' % an_image.location )

# Generating an unique name to be used for corresponding
# ssh "key pair" & EC2 "security group"
import tempfile
an_unique_file = tempfile.mkstemp()[ 1 ]
an_unique_name = os.path.basename( an_unique_file )
os.remove( an_unique_file )
print_d( 'an_unique_name = %s\n' % an_unique_name )

# Asking EC2 to generate a new ssh "key pair"
a_key_pair_name = an_unique_name
a_key_pair = an_ec2_conn.create_key_pair( a_key_pair_name )

# Saving the generated ssh "key pair" locally
a_key_pair_dir = os.path.expanduser( "~/.ssh")
a_key_pair.save( a_key_pair_dir )
a_key_pair_file = os.path.join( a_key_pair_dir, a_key_pair.name ) + os.path.extsep + "pem"
print_d( 'a_key_pair_file = %s\n' % a_key_pair_file )

import stat
os.chmod( a_key_pair_file, stat.S_IRUSR )

# Asking EC2 to generate a new "sequirity group" & apply corresponding firewall permissions
a_security_group = an_ec2_conn.create_security_group( an_unique_name, 'temporaly generated' )
a_security_group.authorize( 'tcp', 80, 80, '0.0.0.0/0' )
a_security_group.authorize( 'tcp', 22, 22, '0.0.0.0/0' )

# Creating a EC2 "reservation" with all the parameters mentioned above
an_instance_type = 'm1.small'
# an_instance_type = 'm1.large' # 64-bit version
a_reservation = an_image.run( instance_type = an_instance_type, min_count = 1, max_count = 1, key_name = a_key_pair_name, security_groups = [ a_security_group.name ] )
an_instance = a_reservation.instances[ 0 ]
wait_activation( an_instance )

# Instantiating ssh connection with root access
import paramiko
a_ssh_client = paramiko.SSHClient()
a_ssh_client.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
a_rsa_key = paramiko.RSAKey( filename = a_key_pair_file )

a_username = 'ubuntu'
a_ssh_connect = lambda : a_ssh_client.connect( hostname = an_instance.dns_name, port = 22, username = a_username, pkey = a_rsa_key )

# Making sure that corresponding instances are ready to use
wait_ssh( a_ssh_connect, a_ssh_client, 'echo  > /dev/null' )
print_d( 'ssh -i %s %s@%s\n' % ( a_key_pair_file, a_username, an_instance.dns_name ) )

print_d( "an_instance_reservation_time = %s, sec\n" % an_instance_reservation_time )


print_d( "\n---------------------------------------------------------------------------\n" )
# Uploading and running 'control' scripts into cloud
a_task_execution_time = Timer()

# Preparing corresponding cloud 'working dir'
ssh_command( a_ssh_client, 'mkdir %s' % a_working_dir )

# Instantiating a sftp client
a_sftp_client = a_ssh_client.open_sftp()

# Uploading and installing into the cloud corresponding Python engine (itself)
a_sftp_client.put( a_balloon_source_archive, a_balloon_target_archive )
ssh_command( a_ssh_client, 'cd %s && tar -xzf %s' % ( a_working_dir, a_balloon_archive_name ) )
a_balloon_setup_dir = os.path.join( a_working_dir, a_balloon_name )
ssh_command( a_ssh_client, 'cd %s && sudo python ./setup.py install' % ( a_balloon_setup_dir ) )

# Uploading and unpacking into the cloud 'control' scripts
a_sftp_client.put( a_control_archive, a_control_archive )
ssh_command( a_ssh_client, 'cd %s && tar -xzf %s' % ( a_working_dir, a_control_name ) )

# Executing into the cloud 'control' scripts
a_command = '%s/launch' % ( a_working_dir ) 
a_command += " --bucket-name='%s'" % a_bucket_name
a_command += " --data-name='%s'" % a_data_name
a_command += " --working-dir='%s'" % a_working_dir
a_command += " --aws-access-key-id='%s'" % AWS_ACCESS_KEY_ID
a_command += " --aws-secret-access-key='%s'" % AWS_SECRET_ACCESS_KEY
# ssh_command( a_ssh_client, a_command )

# ssh_command( a_ssh_client, 'sudo add-apt-repository ppa:cae-team/ppa' )
# ssh_command( a_ssh_client, 'sudo apt-get update' )
# ssh_command( a_ssh_client, 'sudo apt-get upgrade' )
# ssh_command( a_ssh_client, 'sudo apt-get install openfoam-dev-1.5' )

print_d( "a_task_execution_time = %s, sec\n" % a_task_execution_time )


print_d( "\n---------------------------------------------------------------------------\n" )
# Closing SSH connection
a_ssh_client.close()

# Cleaning tempral working folder
import shutil
shutil.rmtree( a_working_dir )


#---------------------------------------------------------------------------
# This refenrece value could be used further in cloud management pipeline
print a_bucket_name


print_d( "\n---------------------------------------------------------------------------\n" )
print_d( 'OK\n' )


#--------------------------------------------------------------------------------------
