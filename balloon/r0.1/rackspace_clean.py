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
RACKSPACE_USER = os.getenv( "RACKSPACE_USER" )
RACKSPACE_KEY = os.getenv( "RACKSPACE_KEY" )


#--------------------------------------------------------------------------------------
import cloudfiles
print "---------------- Delete CloudFiles ---------------"
a_cloudfiles_conn = cloudfiles.get_connection( RACKSPACE_USER, RACKSPACE_KEY, timeout = 500 )
for a_container_name in a_cloudfiles_conn.list_containers() :
    if a_container_name == 'cloudservers' :
        continue

    print a_container_name
    a_cloudfiles_container = a_cloudfiles_conn[ a_container_name ]
    an_objects = a_cloudfiles_container.get_objects()
    for an_object in an_objects :
        a_cloudfiles_container.delete_object( an_object )
        print "\t", an_object
        pass

    a_cloudfiles_conn.delete_container( a_cloudfiles_container ) 
    pass

print


#--------------------------------------------------------------------------------------
from libcloud.types import Provider 
from libcloud.providers import get_driver 
print "-------------- Destroy CloudServers --------------"
Driver = get_driver( Provider.RACKSPACE ) 
a_libcloud_conn = Driver( RACKSPACE_USER, RACKSPACE_KEY ) 
for a_node in a_libcloud_conn.list_nodes() :
    a_node.destroy()
    print a_node.name
    pass

print


#--------------------------------------------------------------------------------------
print "---------------------- OK ------------------------"


#--------------------------------------------------------------------------------------
