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
This script upload a file from web and publish it as 'study file' in S3
"""


#--------------------------------------------------------------------------------------
def usage_description() :
    return " --remote-location='/mnt'"


#--------------------------------------------------------------------------------------
from cloudflu.preferences import OptionGroup, PersistentOption, TransientOption
a_container = OptionGroup( 'amazon.credentials_deploy' )

a_container.add_option( TransientOption( "--aws-user-id",
                                         metavar = "< AWS User ID >",
                                         action = "store",
                                         dest = "aws_user_id",
                                         help = "(${AWS_USER_ID}, by default)",
                                         default = None ) )

a_container.add_option( TransientOption( "--ec2-private-key",
                                         metavar = "< EC2 Private Key >",
                                         action = "store",
                                         dest = "ec2_private_key",
                                         help = "(${EC2_PRIVATE_KEY}, by default)",
                                         default = None ) )

a_container.add_option( TransientOption( "--ec2-cert",
                                         metavar = "< EC2 Certificate >",
                                         action = "store",
                                         dest = "ec2_cert",
                                         help = "(${EC2_CERT}, by default)",
                                         default = None ) )

a_container.add_option( PersistentOption( "--remote-location",
                                          metavar = "< destination of the credendtials environemnt files >",
                                          action = "store",
                                          dest = "remote_location",
                                          help = "(\"%default\", by default)",
                                          default = '/tmp/.aws_credentialsrc' ) )


#--------------------------------------------------------------------------------------
def extract( the_option_parser ) :
    from cloudflu.preferences import resource_filename
    an_options, an_args = the_option_parser.parse_args()

    AWS_USER_ID = an_options.aws_user_id
    if AWS_USER_ID == None :
        import os; AWS_USER_ID = os.getenv( "AWS_USER_ID" )
        pass

    EC2_PRIVATE_KEY = an_options.ec2_private_key
    if EC2_PRIVATE_KEY == None :
        import os; EC2_PRIVATE_KEY = os.getenv( "EC2_PRIVATE_KEY" )
        pass

    if EC2_PRIVATE_KEY != None :
        EC2_PRIVATE_KEY = os.path.abspath( EC2_PRIVATE_KEY )
        if not os.path.isfile( EC2_PRIVATE_KEY ) :
            the_option_parser.error( "--ec2-private-key='%s' must be a file" % EC2_PRIVATE_KEY )
            pass
        pass

    EC2_CERT = an_options.ec2_cert
    if EC2_CERT == None :
        import os; EC2_CERT = os.getenv( "EC2_CERT" )
        pass

    if EC2_PRIVATE_KEY != None :
        EC2_CERT = os.path.abspath( EC2_CERT )
        if not os.path.isfile( EC2_CERT ) :
            the_option_parser.error( "--ec2-cert='%s' must be a file" % EC2_CERT )
            pass
        pass

    a_remote_location = os.path.abspath( an_options.remote_location )

    return AWS_USER_ID, EC2_PRIVATE_KEY, EC2_CERT, a_remote_location


#--------------------------------------------------------------------------------------
def compose( AWS_USER_ID, EC2_PRIVATE_KEY, EC2_CERT, the_remote_location ) :
    return "--remote-location='%s'" % ( the_remote_location )


#--------------------------------------------------------------------------------------
from cloudflu.preferences import template_add
add = lambda the_option_parser : template_add( the_option_parser, a_container )


#------------------------------------------------------------------------------------------
from cloudflu.preferences import template_dump
dump = lambda the_identation_level, the_output : template_dump( the_identation_level, a_container, the_output )


#------------------------------------------------------------------------------------------
