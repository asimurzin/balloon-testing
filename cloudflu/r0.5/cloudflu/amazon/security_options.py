

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
    return " --aws-access-key-id=${AWS_ACCESS_KEY_ID} --aws-secret-access-key=${AWS_SECRET_ACCESS_KEY}"


#--------------------------------------------------------------------------------------
from cloudflu.preferences import OptionGroup, PersistentOption, TransientOption
a_container = OptionGroup( 'amazon.security' )

a_container.add_option( PersistentOption( "--aws-access-key-id",
                                          metavar = "< Amazon key id >",
                                          action = "store",
                                          dest = "aws_access_key_id",
                                          help = "(${AWS_ACCESS_KEY_ID}, by default)",
                                          default = None ) )

a_container.add_option( PersistentOption( "--aws-secret-access-key",
                                          metavar = "< Amazon secret key >",
                                          action = "store",
                                          dest = "aws_secret_access_key",
                                          help = "(${AWS_SECRET_ACCESS_KEY}, by default)",
                                          default = None ) )


#--------------------------------------------------------------------------------------
def extract( the_option_parser ) :
    from cloudflu.preferences import resource_filename
    an_options, an_args = the_option_parser.parse_args()

    AWS_ACCESS_KEY_ID = an_options.aws_access_key_id
    if AWS_ACCESS_KEY_ID == None :
        import os
        AWS_ACCESS_KEY_ID = os.getenv( "AWS_ACCESS_KEY_ID" )
        pass
    
    if AWS_ACCESS_KEY_ID == None or AWS_ACCESS_KEY_ID == '' :
        the_option_parser.error( "\n"
                                 "To proceed define first :\n"
                                 "\t'--aws-access-key-id' command-line option,\n"
                                 "\tor ${AWS_ACCESS_KEY_ID} environment variable,\n"
                                 "\tor'amazon.aws_access_key_id' key in '%s' resource file\n" % resource_filename() )
        pass

    AWS_SECRET_ACCESS_KEY = an_options.aws_secret_access_key
    if AWS_SECRET_ACCESS_KEY == None :
        import os
        AWS_SECRET_ACCESS_KEY = os.getenv( "AWS_SECRET_ACCESS_KEY" )
        pass
    
    if AWS_SECRET_ACCESS_KEY == None or AWS_SECRET_ACCESS_KEY == '' :
        the_option_parser.error( "\n"
                                 "To proceed define first :\n"
                                 "\t'--aws-secret-access_key' command-line option,\n"
                                 "\tor${AWS_SECRET_ACCESS_KEY} environment variable,\n"
                                 "\tor'amazon.aws_secret_access_key' key in '%s' resource file\n" % resource_filename() )
        pass

    return AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


#--------------------------------------------------------------------------------------
from cloudflu.preferences import template_add
add = lambda the_option_parser : template_add( the_option_parser, a_container )


#------------------------------------------------------------------------------------------
from cloudflu.preferences import template_dump
dump = lambda the_identation_level, the_output : template_dump( the_identation_level, a_container, the_output )


#------------------------------------------------------------------------------------------
