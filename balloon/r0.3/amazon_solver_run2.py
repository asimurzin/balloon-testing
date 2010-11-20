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
## See http://sourceforge.net/apps/mediawiki/balloon-foam
##
## Author : Alexey Petrov
##


#--------------------------------------------------------------------------------------
"""
This script is responsible for cluster environment setup for the given Amazon EC2 reservation
"""


#--------------------------------------------------------------------------------------
import balloon.common as common
from balloon.common import print_d, print_e, sh_command, Timer, WorkerPool

from balloon import amazon
from balloon.amazon import ec2


#--------------------------------------------------------------------------------------
class ResultHolder :
    def __init__( self ) :
        self._result = None
        pass

    def keep( self, the_result ) :
        self._result = the_result
        pass

    def get( self ) :
        return self._result
    
    pass


#--------------------------------------------------------------------------------------
class UploadStart( ResultHolder ) :
    def __init__( self ) :
        ResultHolder.__init__( self )
        pass

    def __call__( self, the_case_dir, the_credentials ) :
        print_d( "\n--------------------- Uploading case data to S3 ---------------------------\n" )
        an_study_name = sh_command( 'amazon_upload_start.py %s %s' % ( the_case_dir, the_credentials ) )[ 0 ][ : -1 ]

        self.keep( an_study_name )
        pass

    pass


#--------------------------------------------------------------------------------------
class BalloonDeploy( ResultHolder ) :
    def __init__( self ) :
        ResultHolder.__init__( self )
        pass

    def __call__( self, the_password, the_identity_file, the_host_port, the_login_name, the_host_name ) :
        print_d( 'ssh -o "StrictHostKeyChecking no" -i %s -p %d %s@%s\n' % ( an_identity_file, a_host_port, a_login_name, a_host_name ) )
        a_ssh_client = ssh.connect( the_password, the_identity_file, the_host_port, the_login_name, the_host_name )

        print_d( "\n------------------ Installing balloon to master node ----------------------\n" )
        # - In case of development version
        # sh_command( "./balloon_deploy.py --identity-file=%s --host-port=%s --login-name=%s --host-name=%s" %
        #             ( an_identity_file, a_host_port, a_login_name, a_host_name ) )

        # - In case of stable version
        # ssh.command( a_ssh_client, "sudo easy_install balloon" )

        # - In case of context dependant version (use exactly the same version as locally installed)
        import balloon
        an_install_requires = 'install_requires = [ "%s == %s"]' % ( balloon.NAME, balloon.VERSION )
        ssh.command( a_ssh_client, """sudo python -c 'from setuptools import setup; setup( name = "dummy", %s )' install""" % an_install_requires )

        self.keep( a_ssh_client )
        pass

    pass


#--------------------------------------------------------------------------------------
class Download2Run2Upload( ResultHolder ) :
    def __init__( self ) :
        ResultHolder.__init__( self )
        pass

    def __call__( self, the_reservation, the_instance2ssh, the_input_study, the_case_name, the_credentials,
                  the_password, the_identity_file, the_host_port, the_login_name, the_host_name ) :
        a_master_node = the_reservation.instances[ 0 ]
        a_ssh_client = an_instance2ssh[ a_master_node ]
        
        print_d( "\n------------- Downloading case data from S3 to the master node ------------\n"  )
        a_working_dir = ssh.command( a_ssh_client, 'python -c "import os, os.path, tempfile; print tempfile.mkdtemp()"' )[ 0 ][ : -1 ]
        print_d( "a_working_dir = '%s'\n" % a_working_dir )

        ssh.command( a_ssh_client, "amazon_download.py --study-name=%s --output-dir=%s %s" % ( the_input_study, a_working_dir, the_credentials ) )

        print_d( "\n--- Sharing the solver case folder for all the cluster nodes through NFS --\n" )
        ssh.command( a_ssh_client, "sudo sh -c 'echo %s *\(rw,no_root_squash,sync,subtree_check\) >> /etc/exports'" % ( a_working_dir ) )
        ssh.command( a_ssh_client, "sudo exportfs -a" ) # make changes effective on the running NFS server

        for an_instance in the_reservation.instances[ 1 : ] :
            a_host_name = an_instance.public_dns_name
            print_d( 'ssh -o "StrictHostKeyChecking no" -i %s -p %d %s@%s\n' % ( the_identity_file, the_host_port, the_login_name, the_host_name ) )
            
            a_ssh_client = ssh.connect( the_password, the_identity_file, the_host_port, the_login_name, the_host_name )
            ssh.command( a_ssh_client, "mkdir -p %s" % ( a_working_dir ) )
            ssh.command( a_ssh_client, "sudo mount %s:%s %s" % ( a_master_node.private_ip_address, a_working_dir, a_working_dir ) )
            
            the_instance2ssh[ an_instance ] = a_ssh_client
            pass
        

        print_d( "\n----------------------- Running of the solver case ------------------------\n" )
        a_solver_spent_time = Timer()
        
        a_ssh_client = an_instance2ssh[ a_master_node ]
        a_tagret_dir = os.path.join( a_working_dir, the_case_name )
        ssh.command( a_ssh_client, "source ~/.profile && %s/Allrun %d" % ( a_tagret_dir, len( a_reservation.instances ) ) ) # running the solver case
        
        print_d( "a_solver_spent_time = %s, sec\n" % a_solver_spent_time )
        
        
        print_d( "\n-----------------------  Uploading results to S3 --------------------------\n" )
        an_output_study = ssh.command( a_ssh_client, 'amazon_upload_start.py %s %s' % ( a_tagret_dir, the_credentials ) )[ 0 ][ : -1 ]
        print_d( "an_output_study = '%s'\n" % an_output_study )

        self.keep( an_output_study )
        pass

    pass


#--------------------------------------------------------------------------------------
# Defining utility command-line interface

an_usage_description = "%prog --case-dir='./damBreak'"
an_usage_description += ec2.use.add_usage_description()
an_usage_description += amazon.add_usage_description()
an_usage_description += common.add_usage_description()

from optparse import IndentedHelpFormatter
a_help_formatter = IndentedHelpFormatter( width = 127 )

from optparse import OptionParser
an_option_parser = OptionParser( usage = an_usage_description, version="%prog 0.1", formatter = a_help_formatter )

an_option_parser.add_option( "--case-dir",
                             metavar = "< location of the source OpenFOAM case dir >",
                             action = "store",
                             dest = "case_dir",
                             default = None )
an_option_parser.add_option( "--output-suffix",
                             metavar = "< folder suffix for the output results >",
                             action = "store",
                             dest = "output_suffix",
                             default = '.out' )
ec2.use.add_parser_options( an_option_parser )
amazon.add_parser_options( an_option_parser )
common.add_parser_options( an_option_parser )
  
 
#--------------------------------------------------------------------------------------
# Extracting and verifying command-line arguments

an_options, an_args = an_option_parser.parse_args()

an_enable_debug = common.extract_options( an_options )
AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.extract_options( an_options )
an_image_location, a_reservation_id, an_identity_file, a_host_port, a_login_name = ec2.use.extract_options( an_options )

if an_options.case_dir == None :
    an_option_parser.error( "Use '--case-dir' option to define folder containing solver case\n" )
    pass

import os
a_case_dir = os.path.abspath( an_options.case_dir )
if not os.path.isdir( a_case_dir ) :
    an_option_parser.error( "--case-dir='%s' should be a folder\n" % a_case_dir )
    pass

an_output_suffix = an_options.output_suffix


print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
import sys
an_engine = sys.argv[ 0 ]

a_call = "%s --case-dir='%s' %s" % ( an_engine, a_case_dir, ec2.use.compose_call( an_options ) )
print_d( a_call + '\n' )


print_d( "\n----------------------- Running actual functionality ----------------------\n" )
a_total_spent_time = Timer()

an_ec2_conn = ec2.region_connect( an_image_location, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
a_reservation = ec2.use.get_reservation( an_ec2_conn, a_reservation_id )

a_password = "" # No password
an_identity_file = an_identity_file
a_host_port = a_host_port
a_login_name = a_login_name

from balloon.common import ssh
an_instance2ssh = {}

a_credentials = "--aws-access-key-id=%s --aws-secret-access-key=%s" % ( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
a_master_node = an_instance = a_reservation.instances[ 0 ]
a_host_name = an_instance.public_dns_name


#--------------------------------------------------------------------------------------
a_worker_pool = WorkerPool( 2 )

an_upload_start = UploadStart()
a_worker_pool.charge( an_upload_start, ( a_case_dir, a_credentials ) )

a_balloon_deploy = BalloonDeploy()
a_worker_pool.charge( a_balloon_deploy, ( a_password, an_identity_file, a_host_port, a_login_name, a_host_name ) )

a_worker_pool.shutdown()
a_worker_pool.wait()

an_input_study = an_upload_start.get()
print_d( "an_input_study = '%s'\n" % an_input_study )

an_instance2ssh[ an_instance ] = a_ssh_client = a_balloon_deploy.get()


#--------------------------------------------------------------------------------------
a_worker_pool = WorkerPool( 2 )

an_upload_resume = lambda the_study_name, the_credentials : \
    sh_command( 'amazon_upload_resume.py --study-name=%s %s' % ( the_study_name, the_credentials ) )
a_worker_pool.charge( an_upload_resume, ( an_input_study, a_credentials ) )

a_download2run2upload = Download2Run2Upload()
a_case_name = os.path.basename( a_case_dir )
a_worker_pool.charge( a_download2run2upload, ( a_reservation, an_instance2ssh, an_input_study, a_case_name, a_credentials,
                                               a_password, an_identity_file, a_host_port, a_login_name, a_host_name ) )

a_worker_pool.shutdown()
a_worker_pool.wait()

an_output_study = a_download2run2upload.get()
print_d( "an_output_study = '%s'\n" % an_output_study )


#--------------------------------------------------------------------------------------
a_worker_pool = WorkerPool( 3 )

an_upload_resume = lambda the_study_name, the_credentials : \
    ssh.command( a_ssh_client, 'amazon_upload_resume.py --study-name=%s %s' % ( the_study_name, the_credentials ) )
a_worker_pool.charge( an_upload_resume, ( an_output_study, a_credentials ) )

import tempfile
an_output_dir = tempfile.mkdtemp()

a_download = lambda the_study_name, the_output_dir, the_credentials : \
    sh_command( "amazon_download.py --study-name=%s --output-dir=%s %s" % ( the_study_name, the_output_dir, the_credentials ) )
a_worker_pool.charge( a_download, ( an_output_study, an_output_dir, a_credentials ) )

a_rm_study = lambda the_study_name, the_credentials : \
    ssh.command( a_ssh_client, "amazon_rm_study.py %s %s" % ( the_study_name, the_credentials ) )
a_worker_pool.charge( a_rm_study, ( an_input_study, a_credentials ) )

a_worker_pool.shutdown()
a_worker_pool.wait()


#--------------------------------------------------------------------------------------
import shutil
a_tagret_dir = a_case_dir + an_output_suffix
print_d( "a_tagret_dir = '%s'\n" % a_tagret_dir )

shutil.rmtree( a_tagret_dir, True )
shutil.move( os.path.join( an_output_dir, a_case_name ), a_tagret_dir )
shutil.rmtree( an_output_dir, True )

# To speed-up the script execution; user can remove all these studies afterwards by the following command
#   amazon_ls.py | xargs amazon_rm_study.py
# sh_command( a_ssh_client, "amazon_rm_study.py %s %s" % ( an_output_study, a_credentials ) )

[ a_ssh_client.close() for a_ssh_client in an_instance2ssh.values() ]

print_d( "a_total_spent_time = %s, sec\n" % a_total_spent_time )


print_d( "\n------------------ Printing succussive pipeline arguments -----------------\n" )
ec2.use.print_options( *ec2.use.unpack( an_options ) )


print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
print_d( a_call + '\n' )


print_d( "\n-------------------------------------- OK ---------------------------------\n" )
