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
This script is responsible for the deployng of the 'cloudflu' package into appointed cloud instance
"""


#--------------------------------------------------------------------------------------
import cloudflu.common as common
from cloudflu.common import print_d, print_e, sh_command, Timer
from cloudflu.common import ssh

import deploy_options


#--------------------------------------------------------------------------------------
def main() :
    #----------------------- Defining utility command-line interface -------------------------    
    an_usage_description = "%prog"

    an_usage_description += deploy_options.usage_description()

    an_usage_description += ssh.options.usage_description()

    from cloudflu import VERSION
    a_version = "%s" % VERSION

    from optparse import IndentedHelpFormatter
    a_help_formatter = IndentedHelpFormatter( width = 127 )

    from optparse import OptionParser
    an_option_parser = OptionParser( usage = an_usage_description, version = a_version, formatter = a_help_formatter )


    #----------------------- Definition of the command line arguments ------------------------
    deploy_options.add( an_option_parser )

    ssh.options.add( an_option_parser )

    common.options.add( an_option_parser )
  
 
    #------------------ Extracting and verifying command-line arguments ----------------------
    an_options, an_args = an_option_parser.parse_args()

    an_enable_debug = common.options.extract( an_option_parser )
    
    a_password, an_identity_file, a_host_port, a_login_name, a_host_name, a_command = ssh.options.extract( an_option_parser )

    a_production, an_url = deploy_options.extract( an_option_parser )
    

    print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
    import sys; an_engine = sys.argv[ 0 ]

    a_call = "%s %s %s" % ( an_engine, 
                            deploy_options.compose( a_production, an_url ),
                            ssh.options.compose( a_password, an_identity_file, a_host_port, a_login_name, a_host_name ) )
    print_d( a_call + '\n' )


    print_d( "\n----------------------- Running actual functionality ----------------------\n" )
    ssh.options.echo( a_password, an_identity_file, a_host_port, a_login_name, a_host_name )
    a_ssh_client = ssh.connect( a_password, an_identity_file, a_host_port, a_login_name, a_host_name, a_command )

    if a_production == True : 
        ssh.command( a_ssh_client, "sudo easy_install %s" % an_url )
    else:
        import os.path; a_source_dir = os.path.abspath( os.curdir )
        sh_command( "cd %s && ./setup.py sdist" % a_source_dir )

        ssh.command( a_ssh_client, ( "sudo apt-get -y install python-setuptools" ) )
        ssh.command( a_ssh_client, ( "sudo apt-get -y install python-all-dev" ) )

        a_stdout_lines = ssh.command( a_ssh_client, 'python -c "import os, os.path, tempfile; print tempfile.mkdtemp()"' )
        a_working_dir = a_stdout_lines[ 0 ][ : -1 ]
        print_d( "a_working_dir = %s\n" % a_working_dir )

        import cloudflu
        a_cloudflu_name = "%s-%s" % ( cloudflu.NAME, cloudflu.VERSION )
        a_cloudflu_archive_name = a_cloudflu_name + os.extsep + "tar.gz"
        a_cloudflu_source_archive = os.path.join( a_source_dir, 'dist', a_cloudflu_archive_name )
        a_cloudflu_target_archive = os.path.join( a_working_dir, a_cloudflu_archive_name )

        # Uploading and installing into the cloud corresponding Python engine (itself)
        a_sftp_client = a_ssh_client.open_sftp()
        a_sftp_client.put( a_cloudflu_source_archive, a_cloudflu_target_archive )
        ssh.command( a_ssh_client, 'cd %s && tar -xzf %s' % ( a_working_dir, a_cloudflu_archive_name ) )
        a_cloudflu_setup_dir = os.path.join( a_working_dir, a_cloudflu_name )
        ssh.command( a_ssh_client, 'cd %s && sudo python ./setup.py install' % ( a_cloudflu_setup_dir ) )
    
        # ssh.command( a_ssh_client, """python -c 'import shutil; shutil.rmtree( "%s" )'""" % a_working_dir )
        pass

    # To enable 'cloudflu' debug mode by default
    ssh.command( a_ssh_client, """sudo bash -c "echo 'export __CLOUDFLU_DEBUG_ENABLE__=X' >> /etc/profile" """ ) 

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
