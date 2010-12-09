
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
import options


#---------------------------------------------------------------------------
def command( the_ssh_client, the_command, the_bufsize = -1 ) :
    "Execution of secure shell command"
    from cloudflu.common import print_d
    print_d( "[%s]\n" % the_command )
    
    a_channel = the_ssh_client.get_transport().open_session()
    a_channel.exec_command( "source /etc/profile && " + the_command )

    a_stdin = a_channel.makefile( 'wb', the_bufsize )
    a_stdout = a_channel.makefile( 'rb', the_bufsize )
    a_stderr = a_channel.makefile_stderr( 'rb', the_bufsize )

    an_exit_status = a_channel.recv_exit_status()

    a_stderr_lines = a_stderr.readlines()
    for a_line in a_stderr_lines : print_d( "\t%s" % a_line )

    a_stdout_lines = a_stdout.readlines()
    for a_line in a_stdout_lines : print_d( "\t%s" % a_line )

    return a_stdout_lines


#--------------------------------------------------------------------------------------
def wait( the_ssh_connect, the_ssh_client, the_command ) :
    from cloudflu.common import print_d
    print_d( "ssh'ing " )
    
    while True :
        try :
            print_d( '.' )
            the_ssh_connect()
            command( the_ssh_client, the_command )
            break
        except :
            # import sys, traceback
            # traceback.print_exc( file = sys.stderr )
            continue
        pass

    pass


#--------------------------------------------------------------------------------------
def connect( the_password, the_identity_file, the_host_port, the_login_name, the_host_name, the_command = None ) :
    import paramiko
    a_ssh_client = paramiko.SSHClient()
    a_ssh_client.set_missing_host_key_policy( paramiko.AutoAddPolicy() )

    a_ssh_connect = None
    if the_password != None :
        a_ssh_connect = lambda : a_ssh_client.connect( hostname = the_host_name, port = the_host_port, username = the_login_name, password = the_password )
    else :
        a_rsa_key = paramiko.RSAKey( filename = the_identity_file )
        a_ssh_connect = lambda : a_ssh_client.connect( hostname = the_host_name, port = the_host_port, username = the_login_name, pkey = a_rsa_key )
        pass
    
    if the_command == None :
        from cloudflu.preferences import get
        the_command = get( 'common.ssh.command' )
        pass

    wait( a_ssh_connect, a_ssh_client, the_command ) 
    
    return a_ssh_client


#--------------------------------------------------------------------------------------
