
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
Contains the package dedicated preferences
"""


#--------------------------------------------------------------------------------------
def usage_description() :
    return " [ --password='P@ssw0rd' | --identity-file='~/.ssh/tmpraDD2j.pem' ] --host-port=22 --login-name='ubuntu' --host-name='ec2-184-73-11-20.compute-1.amazonaws.com'"


#--------------------------------------------------------------------------------------
from cloudflu.preferences import OptionGroup, PersistentOption, TransientOption
a_container = OptionGroup( 'common.ssh' )

a_container.add_option( TransientOption( "--password",
                                         metavar = "< password for the given host and login name >",
                                         action = "store",
                                         dest = "password",
                                         default = None ) )

a_container.add_option( TransientOption( "--identity-file",
                                         metavar = "< private key for RSA or DSA authentication >",
                                         action = "store",
                                         dest = "identity_file",
                                         default = None ) )

a_container.add_option( TransientOption( "--host-port",
                                          metavar = "< port to be used >",
                                          type = "int",
                                          action = "store",
                                          dest = "host_port",
                                          help = "(\"%default\", by default)",
                                          default = None ) )

a_container.add_option( TransientOption( "--login-name",
                                          metavar = "< specifies the user to log in as on the remote machine >",
                                          action = "store",
                                          dest = "login_name",
                                          help = "(\"%default\", by default)",
                                          default = None ) )

a_container.add_option( TransientOption( "--host-name",
                                         metavar = "< instance public DNS >",
                                         action = "store",
                                         dest = "host_name",
                                         default = None ) )

a_container.add_option( PersistentOption( "--command",
                                          metavar = "< test command to be run on a remote host >",
                                          action = "store",
                                          dest = "command",
                                          help = "('%default', by default)",
                                          default = 'env | grep -vE "^AWS|^EC2"' ) )


#--------------------------------------------------------------------------------------
def extract( the_option_parser ) :
    from cloudflu.preferences import get_input
    an_options, an_args = the_option_parser.parse_args()

    a_password = an_options.password
    an_identity_file = an_options.identity_file

    if a_password == None and an_identity_file == None :
        a_password, an_args = get_input( an_args )
        an_identity_file, an_args = get_input( an_args )
        pass

    if an_identity_file != None :
        import os.path
        an_identity_file = os.path.expanduser( an_identity_file )
        an_identity_file = os.path.abspath( an_identity_file )
        pass

    a_host_port = an_options.host_port
    if a_host_port == None :
        a_host_port, an_args = get_input( an_args )
        a_host_port = int( a_host_port )
        pass

    a_login_name = an_options.login_name
    if a_login_name == None :
        a_login_name, an_args = get_input( an_args )
        pass

    a_host_name = an_options.host_name
    if a_host_name == None :
        a_host_name, an_args = get_input( an_args )
        pass

    a_command = an_options.command

    return a_password, an_identity_file, a_host_port, a_login_name, a_host_name, a_command


#--------------------------------------------------------------------------------------
def echo( the_password, the_identity_file, the_host_port, the_login_name, the_host_name ) :
    from cloudflu.common import print_d

    if the_password != None :
        print_d( 'sshpass -p %s ssh -o "StrictHostKeyChecking no" -p %d %s@%s\n' % \
                 ( the_password, the_host_port, the_login_name, the_host_name ) )
    else :
        print_d( 'ssh -o "StrictHostKeyChecking no" -i %s -p %d %s@%s\n' % \
                 ( the_identity_file, the_host_port, the_login_name, the_host_name ) )
        pass

    pass


#--------------------------------------------------------------------------------------
def compose( the_password, the_identity_file, the_host_port, the_login_name, the_host_name ) :
    if the_password != None :
        a_call = "--password='%s' --host-port=%d --login-name='%s' --host-name='%s'" % \
                 ( the_password, the_host_port, the_login_name, the_host_name )
    else :
        a_call = "--identity-file='%s' --host-port=%d --login-name='%s' --host-name='%s'" % \
                 ( the_identity_file, the_host_port, the_login_name, the_host_name )
        pass
    
    return a_call


#--------------------------------------------------------------------------------------
def track( the_password, the_identity_file, the_host_port, the_login_name, the_host_name ) :
    if the_password != None :
        print the_password
    else:
        print "''"
        pass
    
    if the_identity_file != None :
        print the_identity_file
    else:
        print "''"
        pass

    print the_host_port
    print the_login_name
    print the_host_name

    pass


#--------------------------------------------------------------------------------------
from cloudflu.preferences import template_add
add = lambda the_option_parser : template_add( the_option_parser, a_container )


#------------------------------------------------------------------------------------------
from cloudflu.preferences import template_dump
dump = lambda the_identation_level, the_output : template_dump( the_identation_level, a_container, the_output )


#------------------------------------------------------------------------------------------
