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
import boto.ec2

import balloon.common as common
from balloon.common import print_d, print_i, print_e, sh_command, Timer, WorkerPool


#--------------------------------------------------------------------------------------
def stop_instance( the_instance ) :
    a_status = the_instance.update()
    if a_status != 'terminated' :
        print "%s : %s : '%s'" % ( the_instance, a_status, the_instance.dns_name )
        the_instance.stop()

        pass

    pass


#--------------------------------------------------------------------------------------
def delete_key_pair( the_key_pair ) :
    print the_key_pair.name

    # an_ec2_conn.delete_key_pair( the_key_pair ) # Does not work (bug)
    the_key_pair.delete()

    a_key_pair_dir = os.path.expanduser( "~/.ssh")
    a_key_pair_file = os.path.join( a_key_pair_dir, the_key_pair.name ) + os.path.extsep + "pem"

    if os.path.isfile( a_key_pair_file ) :
        os.remove( a_key_pair_file )
        pass
    
    pass


#--------------------------------------------------------------------------------------
def delete_security_group( the_ec2_conn, the_security_group ) :
    if the_security_group.name != 'default' :
        print the_security_group.name
        the_ec2_conn.delete_security_group( the_security_group.name )
        
        pass
    pass


#--------------------------------------------------------------------------------------
a_worker_pool = WorkerPool( 8 )

for a_region in boto.ec2.regions( aws_access_key_id = AWS_ACCESS_KEY_ID, aws_secret_access_key = AWS_SECRET_ACCESS_KEY ) :
    an_ec2_conn = a_region.connect()
    print a_region

    print "-------------- Delete EC2 instances --------------"
    for a_reservation in an_ec2_conn.get_all_instances() :
        for an_instance in a_reservation.instances :
            # a_worker_pool.charge( stop_instance, ( an_instance ) )
            stop_instance( an_instance )
            pass
        pass
    print
    a_worker_pool.join()

    print "-------------- Delete EC2 key pairs --------------"
    for a_key_pair in an_ec2_conn.get_all_key_pairs() :
        # a_worker_pool.charge( delete_key_pair, ( a_key_pair ) )
        delete_key_pair( a_key_pair )
        pass
    print


    print "----------- Delete EC2 security groups -----------"
    for a_security_group in an_ec2_conn.get_all_security_groups() :
        # a_worker_pool.charge( delete_security_group, ( an_ec2_conn, a_security_group ) )
        delete_security_group( an_ec2_conn, a_security_group )
        pass
    print

    a_worker_pool.join()
    pass


print "---------------- Delete SQS queues ---------------"
a_sqs_conn = boto.connect_sqs( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY )
for a_queue in a_sqs_conn.get_all_queues() :
    print "'%s' : %d" % ( a_queue.name, a_queue.count() )
    a_queue.clear()
    a_queue.delete()
    pass

print


a_worker_pool.shutdown()
a_worker_pool.join()


print "---------------------- OK ------------------------"

