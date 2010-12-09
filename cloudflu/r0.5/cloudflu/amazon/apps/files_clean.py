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
Cleans all nodes from cloudservers and cloudfiles that correspond to defined rackspace account
"""

#--------------------------------------------------------------------------------------
import cloudflu.common as common
from cloudflu.common import print_d, print_i, print_e
from cloudflu.common import Timer, WorkerPool

import cloudflu.amazon as amazon


#--------------------------------------------------------------------------------------
def main() :
    #----------------------- Defining utility command-line interface -------------------------
    an_usage_description = "%prog"
    an_usage_description += common.concurrency_options.usage_description()
    
    from cloudflu import VERSION
    a_version = "%s" % VERSION
    
    from optparse import IndentedHelpFormatter
    a_help_formatter = IndentedHelpFormatter( width = 127 )
    
    from optparse import OptionParser
    an_option_parser = OptionParser( usage = an_usage_description, version = a_version, formatter = a_help_formatter )
    

    #----------------------- Definition of the command line arguments ------------------------
    common.concurrency_options.add( an_option_parser )

    common.communication_options.add( an_option_parser )

    amazon.security_options.add( an_option_parser )
    
    common.options.add( an_option_parser )

    
    #------------------ Extracting and verifying command-line arguments ----------------------
    an_options, an_args = an_option_parser.parse_args()

    common.options.extract( an_option_parser )
    
    common.communication_options.extract( an_option_parser )

    a_number_threads = common.concurrency_options.extract( an_option_parser )
    
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.security_options.extract( an_option_parser )


    print_i( "-------------------------- Running actual functionality -------------------------\n" )
    import boto; a_s3_conn = boto.connect_s3( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )

    a_worker_pool = WorkerPool( a_number_threads )


    print_i( "------------------------ Remove all the bucket keys, first ----------------------\n" )
    for a_bucket in a_s3_conn.get_all_buckets() :
        try :
            a_s3_bucket_keys = a_bucket.get_all_keys()
            print_d( "'%s' : %d\n" % ( a_bucket.name, len( a_s3_bucket_keys ) ) )
        
            for a_s3_bucket_key in a_bucket.list() :
                print_d( "\t'%s'\n" % ( a_s3_bucket_key.name ) )
                a_worker_pool.charge( lambda the_s3_bucket_key : the_s3_bucket_key.delete(), [ a_s3_bucket_key ] )
                pass
        except :
            pass
        
        pass

    a_worker_pool.join()


    print_i( "--------------------------- Remove the buckets itself ---------------------------\n" )
    for a_bucket in a_s3_conn.get_all_buckets() :
        print_d( "'%s'\n" % ( a_bucket.name ) )
        a_worker_pool.charge( lambda the_s3_bucket : the_s3_bucket.delete(), [ a_bucket ] )
        pass
    
    a_worker_pool.shutdown()
    a_worker_pool.join()


    print_i( "-------------------------------------- OK ---------------------------------------\n" )
    pass


#------------------------------------------------------------------------------------------
if __name__ == '__main__' :
    main()
    pass


#------------------------------------------------------------------------------------------
