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
from cloudflu.common import print_d, print_i, Timer

import cloudflu.common as common
import cloudflu.amazon as amazon


#------------------------------------------------------------------------------------------
def entry_point( the_root_object, the_file2locations, the_upload_seed_size, the_number_threads, the_study_name = None, the_booked = False ) :
    a_spent_time = Timer()
    
    import study_book; 
    a_study_object = study_book.entry_point( the_root_object, the_study_name, the_booked )
    print_d( '\n' )

    import upload_start; 
    a_study_object = upload_start.entry_point( a_study_object, the_file2locations, the_upload_seed_size, the_number_threads )
    print_d( '\n' )

    a_located_files = []
    for a_file, a_location in the_file2locations.iteritems() :
        import os.path; a_located_files.append( os.path.join( a_location, os.path.basename( a_file ) ) )
        pass
    print_d( "a_located_files = %s\n" % a_located_files )

    import upload_resume; 
    a_study_object = upload_resume.entry_point( a_study_object, a_located_files, the_number_threads )
    print_d( '\n' )
    
    print_d( "a_spent_time = %s, sec\n" % a_spent_time )

    return a_study_object
    

#--------------------------------------------------------------------------------------
def main() :
    #----------------------- Defining utility command-line interface -------------------------
    import data_upload_options
    import study_book_options
    import upload_start_options
    import data_seeding_options

    an_usage_description = "%prog"
    an_usage_description += upload_start_options.usage_description()
    an_usage_description += data_upload_options.usage_description()
    
    from cloudflu import VERSION
    a_version = "%s" % VERSION
    
    from optparse import IndentedHelpFormatter
    a_help_formatter = IndentedHelpFormatter( width = 127 )
    
    from optparse import OptionParser
    an_option_parser = OptionParser( usage = an_usage_description, version = a_version, formatter = a_help_formatter )
    

    #----------------------- Definition of the command line arguments ------------------------
    data_upload_options.add( an_option_parser )

    upload_start_options.add( an_option_parser )

    study_book_options.add( an_option_parser )

    data_seeding_options.add( an_option_parser )

    common.concurrency_options.add( an_option_parser )

    common.communication_options.add( an_option_parser )

    amazon.security_options.add( an_option_parser )
    
    common.options.add( an_option_parser )

    
    #------------------ Extracting and verifying command-line arguments ----------------------
    an_options, an_args = an_option_parser.parse_args()

    common.options.extract( an_option_parser )
    
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.security_options.extract( an_option_parser )
    
    common.communication_options.extract( an_option_parser )

    a_number_threads = common.concurrency_options.extract( an_option_parser )
    
    an_upload_seed_size = data_seeding_options.extract( an_option_parser )

    a_file2locations = upload_start_options.extract( an_option_parser )

    a_booked = data_upload_options.extract( an_option_parser )
    
    a_study_name = study_book_options.extract( an_option_parser )
    

    print_i( "--------------------------- Defining the study object ---------------------------\n" )
    from cloudflu.amazon.s3 import TRootObject
    a_root_object = TRootObject.get( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
    print_d( "a_root_object = %s\n" % a_root_object )
    

    print_i( "-------------------------- Running actual functionality -------------------------\n" )
    a_study_object = entry_point( a_root_object, a_file2locations, an_upload_seed_size, a_number_threads, a_study_name, a_booked )
    
    
    print_i( "-------------------- Printing succussive pipeline arguments ---------------------\n" )
    print a_study_object.name()

    
    print_i( "-------------------------------------- OK ---------------------------------------\n" )
    pass


#------------------------------------------------------------------------------------------
if __name__ == '__main__' :
    main()
    pass


#------------------------------------------------------------------------------------------
