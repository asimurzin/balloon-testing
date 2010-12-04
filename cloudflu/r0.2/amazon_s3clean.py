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


#--------------------------------------------------------------------------------------
"""
Cleans all nodes from cloudservers and cloudfiles that correspond to defined rackspace account
"""

#--------------------------------------------------------------------------------------
import os
AWS_ACCESS_KEY_ID = os.getenv( "AWS_ACCESS_KEY_ID" )
AWS_SECRET_ACCESS_KEY = os.getenv( "AWS_SECRET_ACCESS_KEY" )


#--------------------------------------------------------------------------------------
import boto

import balloon.common as common
from balloon.common import print_d, print_i, print_e, sh_command, Timer, WorkerPool


#--------------------------------------------------------------------------------------
print "--------------- Delete S3 buckets ----------------"
a_s3_conn = boto.connect_s3( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )

a_worker_pool = WorkerPool( 8 )

# First remove all the bucket keys
for a_bucket in a_s3_conn.get_all_buckets() :
    try :
        a_s3_bucket_keys = a_bucket.get_all_keys()
        print "'%s' : %d" % ( a_bucket.name, len( a_s3_bucket_keys ) )
        
        for a_s3_bucket_key in a_bucket.list() :
            print "\t'%s'" % ( a_s3_bucket_key.name )
            a_worker_pool.charge( lambda the_s3_bucket_key : the_s3_bucket_key.delete(), [ a_s3_bucket_key ] )
            
            pass
    except :
        pass

    pass

a_worker_pool.join()
print

# Remove the bucket itself
for a_bucket in a_s3_conn.get_all_buckets() :
    print "'%s'" % ( a_bucket.name )
    a_worker_pool.charge( lambda the_s3_bucket : the_s3_bucket.delete(), [ a_bucket ] )

    pass

a_worker_pool.shutdown()
a_worker_pool.join()
print


print "---------------------- OK ------------------------"
#--------------------------------------------------------------------------------------
