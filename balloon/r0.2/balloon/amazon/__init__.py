

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
from balloon.common import print_e, print_d

import os


#--------------------------------------------------------------------------------------
def add_usage_description() :
    return " --aws-access-key-id=${AWS_ACCESS_KEY_ID} --aws-secret-access-key=${AWS_SECRET_ACCESS_KEY}"


#--------------------------------------------------------------------------------------
def add_parser_options( the_option_parser ) :
    the_option_parser.add_option( "--aws-access-key-id",
                                  metavar = "< Amazon key id >",
                                  action = "store",
                                  dest = "aws_access_key_id",
                                  help = "(${AWS_ACCESS_KEY_ID}, by default)",
                                  default = os.getenv( "AWS_ACCESS_KEY_ID" ) )
    
    the_option_parser.add_option( "--aws-secret-access-key",
                                  metavar = "< Amazon secret key >",
                                  action = "store",
                                  dest = "aws_secret_access_key",
                                  help = "(${AWS_SECRET_ACCESS_KEY}, by default)",
                                  default = os.getenv( "AWS_SECRET_ACCESS_KEY" ) )
    pass


#--------------------------------------------------------------------------------------
def unpack( the_options ) :
    AWS_ACCESS_KEY_ID = the_options.aws_access_key_id
    AWS_SECRET_ACCESS_KEY = the_options.aws_secret_access_key

    return AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


#--------------------------------------------------------------------------------------
def compose_call( the_options ) :
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = unpack( the_options )

    a_call = "--aws-access-key-id=${AWS_ACCESS_KEY_ID} --aws-secret-access-key=${AWS_SECRET_ACCESS_KEY}"
    
    return a_call


#--------------------------------------------------------------------------------------
def extract_options( the_options ) :
    AWS_ACCESS_KEY_ID = the_options.aws_access_key_id
    if AWS_ACCESS_KEY_ID == None :
        print_e( "Define AWS_ACCESS_KEY_ID parameter through '--aws-access-key-id' option\n" )
        pass

    AWS_SECRET_ACCESS_KEY = the_options.aws_secret_access_key
    if AWS_SECRET_ACCESS_KEY == None :
        print_e( "Define AWS_SECRET_ACCESS_KEY parameter through '--aws-secret-access-key' option\n" )
        pass

    return AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


#--------------------------------------------------------------------------------------
def add_threading_usage_description() :
    return " --number-threads=7"


#--------------------------------------------------------------------------------------
def add_threading_parser_options( the_option_parser ) :
    the_option_parser.add_option( "--number-threads",
                                  metavar = "< number of threads to use >",
                                  type = "int",
                                  action = "store",
                                  dest = "number_threads",
                                  help = "(\"%default\", by default)",
                                  default = 2 )
    pass


#--------------------------------------------------------------------------------------
def extract_threading_options( the_options, the_option_parser ) :
    if the_options.number_threads < 1 :
        the_option_parser.error( "'--number-threads' must be at least 1" )
        pass

    return the_options.number_threads


#--------------------------------------------------------------------------------------
def add_timeout_usage_description() :
    return " --socket-timeout=3"


#--------------------------------------------------------------------------------------
def add_timeout_options( the_option_parser ) :
    the_option_parser.add_option( "--socket-timeout",
                                  metavar = "< socket timeout time >",
                                  type = "int",
                                  action = "store",
                                  dest = "socket_timeout",
                                  help = "(\"%default\", by default)",
                                  default = None )
    pass


#--------------------------------------------------------------------------------------
def extract_timeout_options( the_options, the_option_parser ) :
    import socket
    socket.setdefaulttimeout( the_options.socket_timeout )

    return the_options.socket_timeout


#--------------------------------------------------------------------------------------
