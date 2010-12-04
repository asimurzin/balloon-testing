
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
from balloon.common import print_e, print_d, Timer


#--------------------------------------------------------------------------------------
def add_usage_description() :
    return " [ --password='P@ssw0rd' | --identity-file='~/.ssh/tmpraDD2j.pem' ] --host-port=22 --login-name='ubuntu' --host-name='ec2-184-73-11-20.compute-1.amazonaws.com'"


#--------------------------------------------------------------------------------------
def add_parser_options( the_option_parser ) :
    the_option_parser.add_option( "--password",
                                  metavar = "< password for the given host and login name >",
                                  action = "store",
                                  dest = "password",
                                  default = "" )
    the_option_parser.add_option( "--identity-file",
                                  metavar = "< selects a file from which the identity (private key) for RSA or DSA authentication is read >",
                                  action = "store",
                                  dest = "identity_file",
                                  default = "" )
    the_option_parser.add_option( "--host-port",
                                  metavar = "< port to be used >",
                                  type = "int",
                                  action = "store",
                                  dest = "host_port",
                                  default = None )
    the_option_parser.add_option( "--login-name",
                                  metavar = "< specifies the user to log in as on the remote machine >",
                                  action = "store",
                                  dest = "login_name",
                                  help = "(\"%default\", by default)",
                                  default = None )
    the_option_parser.add_option( "--host-name",
                                  metavar = "< instance public DNS >",
                                  action = "store",
                                  dest = "host_name",
                                  default = None )
    the_option_parser.add_option( "--command",
                                  metavar = "< command to be run on the remote machine >",
                                  action = "store",
                                  dest = "command",
                                  help = "('%default', by default)",
                                  default = "echo  > /dev/null" )
    return the_option_parser


#--------------------------------------------------------------------------------------
def unpack( the_options ) :
    a_password = the_options.password
    an_identity_file = the_options.identity_file
    a_host_port = the_options.host_port
    a_login_name = the_options.login_name
    a_host_name = the_options.host_name
    a_command = the_options.command

    return a_password, an_identity_file, a_host_port, a_login_name, a_host_name, a_command


#--------------------------------------------------------------------------------------
def print_call( the_password, the_identity_file, the_host_port, the_login_name, the_host_name, the_command = None ) :
    if the_password != "" :
        print_d( 'sshpass -p %s ssh -o "StrictHostKeyChecking no" -p %d %s@%s\n' % \
                     ( the_password, the_host_port, the_login_name, the_host_name ) )
    else :
        print_d( 'ssh -o "StrictHostKeyChecking no" -i %s -p %d %s@%s\n' % \
                     ( the_identity_file, the_host_port, the_login_name, the_host_name ) )
        pass

    pass


#--------------------------------------------------------------------------------------
def compose_call( the_options ) :
    a_password, an_identity_file, a_host_port, a_login_name, a_host_name, a_command = unpack( the_options )

    if a_password != "" :
        a_call = "--password='%s' --host-port=%d --login-name='%s' --host-name='%s' --command='%s'" % \
            ( a_password, a_host_port, a_login_name, a_host_name, a_command )
    else :
        a_call = "--identity-file='%s' --host-port=%d --login-name='%s' --host-name='%s' --command='%s'" % \
            ( an_identity_file, a_host_port, a_login_name, a_host_name, a_command )
        pass
    
    return a_call


#--------------------------------------------------------------------------------------
def extract_options( the_options ) :
    a_password = the_options.password
    an_identity_file = the_options.identity_file

    if a_password == "" and an_identity_file == "" :
        a_password = raw_input()
        an_identity_file = raw_input()
        pass
    the_options.password = a_password

    if an_identity_file != "" :
        import os.path
        an_identity_file = os.path.expanduser( an_identity_file )
        an_identity_file = os.path.abspath( an_identity_file )
        pass
    the_options.identity_file = an_identity_file

    a_host_port = the_options.host_port
    if a_host_port == None :
        a_host_port = int( raw_input() )
        pass
    the_options.host_port = a_host_port

    a_login_name = the_options.login_name
    if a_login_name == None :
        a_login_name = raw_input()
        pass
    the_options.login_name = a_login_name

    a_host_name = the_options.host_name
    if a_host_name == None :
        a_host_name = raw_input()
        pass
    the_options.host_name = a_host_name

    a_command = the_options.command

    return a_password, an_identity_file, a_host_port, a_login_name, a_host_name, a_command


#--------------------------------------------------------------------------------------
def print_options( the_password, the_identity_file, the_host_port, the_login_name, the_host_name, the_command = None ) :
    print the_password
    print the_identity_file
    print the_host_port
    print the_login_name
    print the_host_name

    pass


#---------------------------------------------------------------------------
def command( the_ssh_client, the_command ) :
    "Execution of secure shell command"
    print_d( "[%s]\n" % the_command )
    
    stdin, stdout, stderr = the_ssh_client.exec_command( the_command )

    a_stderr_lines = stderr.readlines()
    for a_line in a_stderr_lines : print_d( "\t%s" % a_line )

    a_stdout_lines = stdout.readlines()
    for a_line in a_stdout_lines : print_d( "\t%s" % a_line )

    return a_stdout_lines


#--------------------------------------------------------------------------------------
def wait( the_ssh_connect, the_ssh_client, the_command ) :
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
def connect( the_password, the_identity_file, the_host_port, the_login_name, the_host_name, the_command = 'echo  > /dev/null' ) :
    import paramiko
    a_ssh_client = paramiko.SSHClient()
    a_ssh_client.set_missing_host_key_policy( paramiko.AutoAddPolicy() )

    a_ssh_connect = None
    if the_password != "" :
        a_ssh_connect = lambda : a_ssh_client.connect( hostname = the_host_name, port = the_host_port, username = the_login_name, password = the_password )
    else :
        a_rsa_key = paramiko.RSAKey( filename = the_identity_file )
        a_ssh_connect = lambda : a_ssh_client.connect( hostname = the_host_name, port = the_host_port, username = the_login_name, pkey = a_rsa_key )
        pass
    
    wait( a_ssh_connect, a_ssh_client, the_command ) 
    
    return a_ssh_client


#--------------------------------------------------------------------------------------
