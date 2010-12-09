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
    import data_transfer_options
    import solver_start_options
    import data_seeding_options
    import openmpi_config_options

    an_usage_description = "%prog"
    an_usage_description += ec2.use.options.usage_description()
    an_usage_description += data_transfer_options.usage_description()
    an_usage_description += solver_start_options.usage_description()

    from cloudflu import VERSION
    a_version = "%s" % VERSION

    from optparse import IndentedHelpFormatter
    a_help_formatter = IndentedHelpFormatter( width = 127 )

    from optparse import OptionParser
    an_option_parser = OptionParser( usage = an_usage_description, version = a_version, formatter = a_help_formatter )


    #----------------------- Definition of the command line arguments ------------------------
    ec2.use.options.add( an_option_parser )
    
    data_transfer_options.add( an_option_parser )

    solver_start_options.add( an_option_parser )

    data_seeding_options.add( an_option_parser )

    common.concurrency_options.add( an_option_parser )

    openmpi_config_options.add( an_option_parser )

    amazon.security_options.add( an_option_parser )
    
    common.options.add( an_option_parser )
  
 
    #------------------ Extracting and verifying command-line arguments ----------------------
    an_options, an_args = an_option_parser.parse_args()
    
    an_enable_debug, a_log_file = common.options.extract( an_option_parser )
    
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.security_options.extract( an_option_parser )
    
    a_cluster_id = ec2.use.options.extract( an_option_parser )

    a_hostfile = openmpi_config_options.extract( an_option_parser )

    a_number_threads = common.concurrency_options.extract( an_option_parser )

    an_upload_seed_size = data_seeding_options.extract( an_option_parser )

    a_case_dir, a_run_hook = solver_start_options.extract( an_option_parser )

    a_study_name = data_transfer_options.extract( an_option_parser )
    
    from cloudflu.preferences import get
    a_cluster_location = get( 'amazon.cluster.location' )
    a_host_port = int( get( 'amazon.cluster.host_port' ) )
    a_login_name = get( 'amazon.cluster.login_name' )


    print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
    import sys; an_engine = sys.argv[ 0 ]

    a_call = "%s %s %s %s %s" % ( an_engine,
                                  ec2.use.options.compose( a_cluster_id ),
                                  data_transfer_options.compose( a_study_name ), 
                                  solver_start_options.compose( a_case_dir, a_run_hook ),
                                  openmpi_config_options.compose( a_hostfile ) )
    print_d( a_call + '\n' )


    print_d( "\n----------------------- Running actual functionality ----------------------\n" )
    a_spent_time = Timer()

    an_ec2_conn = ec2.common.region_connect( a_cluster_location, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
    a_reservation = ec2.use.get_reservation( an_ec2_conn, a_cluster_id )
    print_d( '< %r > : %s\n' % ( a_reservation, a_reservation.instances ) )

    a_master_node = an_instance = a_reservation.instances[ 0 ]


    print_d( "\n--------------------- Uploading case data to S3 ---------------------------\n"  )
    import os; a_case_name = os.path.basename( a_case_dir )

    from cloudflu.amazon.s3 import TRootObject
    a_root_object = TRootObject.get( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
    print_d( "a_root_object = %s\n" % a_root_object )
    
    import data_upload
    an_input_study = data_upload.entry_point( a_root_object, { a_case_dir : '' }, an_upload_seed_size, a_number_threads )

    an_input_study_name = an_input_study.name()
    print_d( "an_input_study_name = '%s'\n" % an_input_study_name )
    

    print_d( "\n------------------ Installing cloudflu to master node ----------------------\n"  )
    a_password = None
    a_host_name = an_instance.public_dns_name
    an_identity_file = ec2.run.get_identity_filepath( an_instance.key_name )
    
    ssh.options.echo( a_password, an_identity_file, a_host_port, a_login_name, a_host_name )
    a_ssh_client = ssh.connect( a_password, an_identity_file, a_host_port, a_login_name, a_host_name )
    
    an_instance2ssh = {}
    an_instance2ssh[ an_instance ] = a_ssh_client
    

    print_d( "\n------------- Downloading case data from S3 to the master node ------------\n"  )
    a_stdout_lines = ssh.command( a_ssh_client, 'python -c "import os, os.path, tempfile; print tempfile.mkdtemp()"' )
    a_working_dir = a_stdout_lines[ 0 ][ : -1 ]
    print_d( "a_working_dir = '%s'\n" % a_working_dir )

    ssh.command( a_ssh_client, "cloudflu-download --study-name=%s --output-dir=%s --remove" % ( an_input_study_name, a_working_dir ) )
    
    print_d( "\n--- Sharing the solver case folder for all the cluster nodes through NFS --\n" )
    ssh.command( a_ssh_client, "sudo sh -c 'echo %s *\(rw,no_root_squash,sync,subtree_check\) >> /etc/exports'" % ( a_working_dir ) )
    ssh.command( a_ssh_client, "sudo exportfs -a" ) # make changes effective on the running NFS server

    for an_instance in a_reservation.instances[ 1 : ] :
        a_host_name = an_instance.public_dns_name
        ssh.options.echo( a_password, an_identity_file, a_host_port, a_login_name, a_host_name )
        
        a_ssh_client = ssh.connect( a_password, an_identity_file, a_host_port, a_login_name, a_host_name )
        ssh.command( a_ssh_client, "mkdir -p %s" % ( a_working_dir ) )
        ssh.command( a_ssh_client, "sudo mount %s:%s %s" % ( a_master_node.private_ip_address, a_working_dir, a_working_dir ) )
        
        an_instance2ssh[ an_instance ] = a_ssh_client
        pass
    
    print_d( "\n------------------------ Get access the booked study ----------------------\n" )
    import study_book; 
    an_output_study = study_book.entry_point( a_root_object, a_study_name, True )


    print_d( "\n----------------------- Running of the solver case ------------------------\n" )
    a_num_nodes = len( a_reservation.instances )

    a_target_dir = os.path.join( a_working_dir, a_case_name )

    an_additional_args = "--study-name='%s' --booked --upload-seed-size=%d" % ( a_study_name, an_upload_seed_size )

    a_ssh_client = an_instance2ssh[ a_master_node ]
    ssh.command( a_ssh_client, "%s/%s %d '%s' %s" % ( a_target_dir, a_run_hook, a_num_nodes, a_hostfile, an_additional_args ) )

    an_output_study.seal()

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
