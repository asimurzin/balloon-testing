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

import balloon.rackspace as rackspace
import balloon.amazon as amazon

import sys, os, os.path, uuid


#--------------------------------------------------------------------------------------
# Defining utility command-line interface

an_usage_description = "%prog --task-control-dir=~/rackspace/control --task-control-dir=~/rackspace/data"
an_usage_description += common.add_usage_description()
an_usage_description += rackspace.add_usage_description()
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
                            default = "./rackspace_control" )

a_option_parser.add_option( "--task-data-dir",
                            metavar = "< location of the task 'data' >",
                            action = "store",
                            dest = "task_data_dir",
                            help = "(\"%default\", by default)",
                            default = "./data" )

common.add_parser_options( a_option_parser )

rackspace.add_parser_options( a_option_parser )

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

RACKSPACE_USER, RACKSPACE_KEY = rackspace.extract_options( an_options )

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

import cloudfiles
a_cloudfiles_conn = cloudfiles.get_connection( RACKSPACE_USER, RACKSPACE_KEY, timeout = 500 )
print_d( "a_cloudfiles_conn = %r\n" % a_cloudfiles_conn )

a_container_name = str( uuid.uuid4() )
a_cloudfiles_container = a_cloudfiles_conn.create_container( a_container_name )
print_d( "a_cloudfiles_container = %s\n" % a_cloudfiles_container.name )

a_file_object = a_cloudfiles_container.create_object( a_data_name )
a_file_object.load_from_filename( a_data_archive )
print_d( "a_file_object = %s\n" % a_file_object.name )

print_d( "a_data_loading_time = %s, sec\n" % a_data_loading_time )


print_d( "\n---------------------------------------------------------------------------\n" )
# Instanciating node in cloud
an_instance_reservation_time = Timer()

from libcloud.types import Provider 
from libcloud.providers import get_driver 

Driver = get_driver( Provider.RACKSPACE ) 
a_libcloud_conn = Driver( RACKSPACE_USER, RACKSPACE_KEY ) 
print_d( "a_libcloud_conn = %r\n" % a_libcloud_conn )

an_images = a_libcloud_conn.list_images() 
print_d( "an_images = %r\n" % an_images )

a_sizes = a_libcloud_conn.list_sizes() 
print_d( "a_sizes = %r\n" % a_sizes )

a_deployment_steps = []
from libcloud.deployment import MultiStepDeployment, ScriptDeployment, SSHKeyDeployment
a_key_pair_file = os.path.expanduser( "~/.ssh/id_rsa.pub")
a_deployment_steps.append( SSHKeyDeployment( open( a_key_pair_file ).read() ) )
# a_deployment_steps.append( ScriptDeployment( "apt-get -y install python-boto" ) )
# a_deployment_steps.append( ScriptDeployment( "apt-get -y install python-paramiko" ) )
# a_deployment_steps.append( ScriptDeployment( "apt-get -y install python-libcloud" ) )
# a_deployment_steps.append( ScriptDeployment( "apt-get -y install python-software-properties" ) )
# a_deployment_steps.append( ScriptDeployment( "add-apt-repository ppa:chmouel/rackspace-cloud-files" ) )
# a_deployment_steps.append( ScriptDeployment( "apt-get -y install python-rackspace-cloudfiles" ) )
a_msd = MultiStepDeployment( a_deployment_steps ) 

a_node_name = a_container_name
a_node = a_libcloud_conn.deploy_node( name = a_node_name, image = an_images[ 9 ] , size = a_sizes[ 0 ], deploy = a_msd ) 
print_d( "a_node = %r\n" % a_node )

print_d( "an_instance_reservation_time = %s, sec\n" % an_instance_reservation_time )


print_d( "\n---------------------------------------------------------------------------\n" )
# Uploading and running 'control' scripts into cloud
a_task_execution_time = Timer()

# Instantiating ssh connection with root access
import paramiko
a_ssh_client = paramiko.SSHClient()
a_ssh_client.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
a_username = 'root'
a_ssh_client.connect( hostname = a_node.public_ip[ 0 ], port = 22, username = a_username )
print_d( 'ssh -i %s %s@%s\n' % ( a_key_pair_file, a_username, a_node.public_ip[ 0 ] ) )

# Preparing corresponding cloud 'working dir'
ssh_command( a_ssh_client, 'mkdir %s' % a_working_dir )

# Instantiating a sftp client
a_sftp_client = a_ssh_client.open_sftp()

# Uploading and installing into the cloud corresponding Python engine (itself)
a_sftp_client.put( a_balloon_source_archive, a_balloon_target_archive )
ssh_command( a_ssh_client, 'cd %s && tar -xzf %s' % ( a_working_dir, a_balloon_archive_name ) )
a_balloon_setup_dir = os.path.join( a_working_dir, a_balloon_name )
ssh_command( a_ssh_client, 'cd %s && python ./setup.py install' % ( a_balloon_setup_dir ) )

# Uploading and unpacking into the cloud 'control' scripts
a_sftp_client.put( a_control_archive, a_control_archive )
ssh_command( a_ssh_client, 'cd %s && tar -xzf %s' % ( a_working_dir, a_control_name ) )

# Executing into the cloud 'control' scripts
a_command = '%s/launch' % ( a_working_dir ) 
a_command += " --container-name='%s'" % a_container_name
a_command += " --data-name='%s'" % a_data_name
a_command += " --working-dir='%s'" % a_working_dir
a_command += " --rackspace-user='%s'" % RACKSPACE_USER
a_command += " --rackspace-key='%s'" % RACKSPACE_KEY
a_command += " --aws-access-key-id='%s'" % AWS_ACCESS_KEY_ID
a_command += " --aws-secret-access-key='%s'" % AWS_SECRET_ACCESS_KEY
ssh_command( a_ssh_client, a_command )

print_d( "a_task_execution_time = %s, sec\n" % a_task_execution_time )


print_d( "\n---------------------------------------------------------------------------\n" )
# Closing SSH connection
a_ssh_client.close()

# Cleaning tempral working folder
import shutil
shutil.rmtree( a_working_dir )


#---------------------------------------------------------------------------
# This refenrece value could be used further in cloud management pipeline
print a_container_name


print_d( "\n---------------------------------------------------------------------------\n" )
print_d( 'OK\n' )


#--------------------------------------------------------------------------------------
