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
This script helps to perform a command into remote cloud instance through ssh protocol,
  where the main problem is to establish proper connection 
  (server inocation & ssh timeout problems)
"""


#--------------------------------------------------------------------------------------
import cloudflu.common as common
from cloudflu.common import print_d, print_e, sh_command, Timer
from cloudflu.common import ssh


#--------------------------------------------------------------------------------------
def main() :
    #----------------------- Defining utility command-line interface -------------------------    
    an_usage_description = "%prog"

    from run_options import usage_description as usage_description_options
    an_usage_description += usage_description_options()
    
    from cloudflu import VERSION
    a_version = "%s" % VERSION

    from optparse import IndentedHelpFormatter
    a_help_formatter = IndentedHelpFormatter( width = 127 )

    from optparse import OptionParser
    an_option_parser = OptionParser( usage = an_usage_description, version = a_version, formatter = a_help_formatter )


    #----------------------- Definition of the command line arguments ------------------------
    from run_options import add as add_options
    add_options( an_option_parser )

    ssh.options.add( an_option_parser )

    common.options.add( an_option_parser )
  
 
    #------------------ Extracting and verifying command-line arguments ----------------------
    an_options, an_args = an_option_parser.parse_args()

    common.options.extract( an_option_parser )
    
    a_password, an_identity_file, a_host_port, a_login_name, a_host_name, a_command = ssh.options.extract( an_option_parser )

    from run_options import extract as extract_options
    a_scripts, a_script_args, a_sequence_file = extract_options( an_option_parser )


    print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
    import sys; an_engine = sys.argv[ 0 ]
    
    from run_options import compose as compose_options
    a_call = "%s %s %s" % ( an_engine, compose_options( a_scripts, a_script_args, a_sequence_file ),
                            ssh.options.compose( a_password, an_identity_file, a_host_port, a_login_name, a_host_name ) )
    
    print_d( a_call + '\n' )
    ssh.options.echo( a_password, an_identity_file, a_host_port, a_login_name, a_host_name )


    print_d( "\n----------------------- Running actual functionality ----------------------\n" )
    a_ssh_client = ssh.connect( a_password, an_identity_file, a_host_port, a_login_name, a_host_name, a_command )

    if a_scripts != None :
        for an_id in range( len( a_scripts ) ) :
            a_script_file = a_scripts[ an_id ]
            a_script_arg = a_script_args[ an_id ]
        
            a_working_dir = ssh.command( a_ssh_client, 'python -c "import os, os.path, tempfile; print tempfile.mkdtemp()"' )[ 0 ][ : -1 ]
            import os; a_target_script = os.path.join( a_working_dir, os.path.basename( a_script_file ) )
        
            a_sftp_client = a_ssh_client.open_sftp() # Instantiating a sftp client
            a_sftp_client.put( a_script_file, a_target_script )
            
            ssh.command( a_ssh_client, 'chmod 755 "%s"' % a_target_script )
            ssh.command( a_ssh_client, 'sudo "%s" %s' % ( a_target_script, a_script_arg ) )
            
            # ssh.command( a_ssh_client, """python -c 'import shutil; shutil.rmtree( "%s" )'""" % a_working_dir )
            pass
        pass

    if a_sequence_file != None :
        a_file = open( a_sequence_file )
        for a_line in a_file.readlines() :
            if a_line[ 0 ] == "#" or a_line[ 0 ] == "\n" :
                continue
            ssh.command( a_ssh_client, 'sudo %s' % a_line[ : -1 ] )
            pass
        a_file.close()
        pass
    
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
