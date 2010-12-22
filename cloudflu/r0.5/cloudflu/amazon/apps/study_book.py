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


#------------------------------------------------------------------------------------------
"""
This script is responsible for efficient uploading of multi file data
"""


#------------------------------------------------------------------------------------------
import cloudflu.common as common
from cloudflu.common import print_d, print_i, print_e, sh_command
from cloudflu.common import Timer, WorkerPool, compute_md5

import cloudflu.amazon as amazon
from cloudflu.amazon.s3 import generate_uploading_dir
from cloudflu.amazon.s3 import TRootObject, TStudyObject, TFileObject, TSeedObject

import sys, os, os.path, uuid, hashlib


#------------------------------------------------------------------------------------------
def entry_point( the_root_object, the_study_name = None, the_booked = False ) :
    a_spent_time = Timer()
    
    if the_study_name == None :
        import uuid; the_study_name = 'tmp-' + str( uuid.uuid4() )
        pass

    print_d( "the_study_name = '%s'\n" % the_study_name )

    a_study_object = None
    if the_booked == True :
        a_study_object = TStudyObject.get( the_root_object, the_study_name )
    else:
        from cloudflu.preferences import get
        a_location = get( 'amazon.data_transfer.location' )

        a_study_object = TStudyObject.create( the_root_object, a_location, the_study_name )
        pass

    print_d( "a_study_object = %s\n" % a_study_object )
    
    print_d( "a_spent_time = %s, sec\n" % a_spent_time )

    return a_study_object
    

#--------------------------------------------------------------------------------------
def main() :
    #----------------------- Defining utility command-line interface -------------------------
    import study_book_options

    an_usage_description = "%prog"
    an_usage_description += study_book_options.usage_description()
    
    from cloudflu import VERSION
    a_version = "%s" % VERSION
    
    from optparse import IndentedHelpFormatter
    a_help_formatter = IndentedHelpFormatter( width = 127 )
    
    from optparse import OptionParser
    an_option_parser = OptionParser( usage = an_usage_description, version = a_version, formatter = a_help_formatter )
    

    #----------------------- Definition of the command line arguments ------------------------
    study_book_options.add( an_option_parser )

    common.communication_options.add( an_option_parser )

    amazon.security_options.add( an_option_parser )
    
    common.options.add( an_option_parser )

    
    #------------------ Extracting and verifying command-line arguments ----------------------
    an_options, an_args = an_option_parser.parse_args()

    common.options.extract( an_option_parser )
    
    common.communication_options.extract( an_option_parser )

    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.security_options.extract( an_option_parser )
    
    a_study_name = study_book_options.extract( an_option_parser )
    
    
    print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
    import sys; an_engine = sys.argv[ 0 ]

    a_call = "%s %s" % ( an_engine, study_book_options.compose( a_study_name ) )
    print_d( a_call + '\n' )


    print_i( "--------------------------- Defining the study object ---------------------------\n" )
    a_root_object = TRootObject.get( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
    print_d( "a_root_object = %s\n" % a_root_object )
    

    print_i( "-------------------------- Running actual functionality -------------------------\n" )
    a_study_object = entry_point( a_root_object, a_study_name ) 
    
    
    print_i( "-------------------- Printing succussive pipeline arguments ---------------------\n" )
    print a_study_object.name()

    
    print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
    print_d( a_call + '\n' )
    

    print_i( "-------------------------------------- OK ---------------------------------------\n" )
    pass


#------------------------------------------------------------------------------------------
if __name__ == '__main__' :
    main()
    pass


#------------------------------------------------------------------------------------------
