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
This script is responsible for cluster environment setup for the given Amazon EC2 reservation
"""


#--------------------------------------------------------------------------------------
import cloudflu.common as common
from cloudflu.common import print_d, print_e, sh_command, Timer
from cloudflu.common import ssh

from cloudflu import amazon
from cloudflu.amazon import ec2


#--------------------------------------------------------------------------------------
def main() :
    #----------------------- Defining utility command-line interface -------------------------    
    import data_transfer_options
    import solver_process_options

    an_usage_description = "%prog"
    an_usage_description += data_transfer_options.usage_description()
    an_usage_description += solver_process_options.usage_description()

    from cloudflu import VERSION
    a_version = "%s" % VERSION

    from optparse import IndentedHelpFormatter
    a_help_formatter = IndentedHelpFormatter( width = 127 )

    from optparse import OptionParser
    an_option_parser = OptionParser( usage = an_usage_description, version = a_version, formatter = a_help_formatter )


    #----------------------- Definition of the command line arguments ------------------------
    data_transfer_options.add( an_option_parser )

    solver_process_options.add( an_option_parser )

    common.concurrency_options.add( an_option_parser )

    amazon.security_options.add( an_option_parser )
    
    common.options.add( an_option_parser )
  
 
    #------------------ Extracting and verifying command-line arguments ----------------------
    an_options, an_args = an_option_parser.parse_args()
    
    an_enable_debug, a_log_file = common.options.extract( an_option_parser )
    
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.security_options.extract( an_option_parser )
    
    a_number_threads = common.concurrency_options.extract( an_option_parser )

    a_study_name = data_transfer_options.extract( an_option_parser )

    an_output_dir, a_before_hook, a_time_hook, an_after_hook = solver_process_options.extract( an_option_parser )
    

    print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
    import sys; an_engine = sys.argv[ 0 ]

    a_call = "%s %s %s" % ( an_engine,
                            data_transfer_options.compose( a_study_name ),
                            solver_process_options.compose( an_output_dir, a_before_hook, a_time_hook, an_after_hook ) )
    print_d( a_call + '\n' )


    #---------------------- To compose a before 'download' callback functor ------------------
    class BeforeHook :
        def __init__( self, the_hook ) :
            self._hook = the_hook
            pass

        def __call__( self, the_study_name, the_output_dir ) :
            try:
                import os; os.system( "%s '%s' '%s'" % ( self._hook, the_study_name, the_output_dir ) )
            except:
                pass
            pass

        pass
    
    if a_before_hook != None :
        a_before_hook = BeforeHook( a_before_hook )
        pass


    #---------------------- To compose a time 'download' callback functor --------------------
    class TimeHook :
        def __init__( self, the_hook ) :
            self._hook = the_hook
            pass

        def __call__( self, the_output_dir, the_located_file ) :
            try:
                a_time = float( the_located_file )
                import os; os.system( "%s '%s' '%s'" % ( self._hook, the_output_dir, a_time ) )
            except:
                pass
            pass

        pass
    
    if a_time_hook != None :
        a_time_hook = TimeHook( a_time_hook )
        pass


    #---------------------- To compose an after 'download' callback functor ------------------
    class AfterHook :
        def __init__( self, the_hook ) :
            self._hook = the_hook
            pass

        def __call__( self, the_output_dir ) :
            try:
                import os; os.system( "%s '%s'" % ( self._hook, the_output_dir ) )
            except:
                pass
            pass

        pass
    
    if an_after_hook != None :
        an_after_hook = AfterHook( an_after_hook )
        pass


    print_d( "\n----------------------- Running actual functionality ----------------------\n" )
    a_spent_time = Timer()

    from cloudflu.amazon.s3 import TRootObject
    a_root_object = TRootObject.get( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
    print_d( "a_root_object = %s\n" % a_root_object )
    
    import study_book; an_output_study = study_book.entry_point( a_root_object, a_study_name, True )

    def Download( the_study_object, the_output_dir, the_number_threads ) :
        if a_before_hook != None :
            a_before_hook( the_study_object.name(), the_output_dir )
            pass

        import download; download.entry_point( the_study_object, the_output_dir, None, the_number_threads, True, True, True, a_time_hook )

        if an_after_hook != None :
            an_after_hook( the_output_dir )
            pass

        pass

    Download( an_output_study, an_output_dir, a_number_threads )
    
    print_d( "a_spent_time = %s, sec\n" % a_spent_time )
    
    
    print_d( "\n------------------ Printing succussive pipeline arguments -----------------\n" )
    print a_study_name
    
    
    print_d( "\n--------------------------- Canonical substitution ------------------------\n" )
    print_d( a_call + '\n' )
    

    print_d( "\n-------------------------------------- OK ---------------------------------\n" )
    pass


#------------------------------------------------------------------------------------------
if __name__ == '__main__' :
    main()
    pass


#------------------------------------------------------------------------------------------
