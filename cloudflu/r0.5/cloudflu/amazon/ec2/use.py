

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
from cloudflu.common import print_e, print_d, Timer

import os, os.path


#--------------------------------------------------------------------------------------
import use_options as options


#--------------------------------------------------------------------------------------
def get_reservation( the_ec2_conn, the_cluster_id ) :
    for a_reservation in the_ec2_conn.get_all_instances() :
        if a_reservation.id == the_cluster_id :
            an_instance = a_reservation.instances[ 0 ]
            a_status = an_instance.update()
            if a_status != 'terminated' :
                return a_reservation
            pass
        pass
    
    raise LookupError( "There is no cluster - '%s'" % the_cluster_id )


#--------------------------------------------------------------------------------------
def get_security_group( the_ec2_conn, the_reservation ) :
    a_security_group = the_ec2_conn.get_all_security_groups( [ the_reservation.groups[ 0 ].id ] )[ 0 ]

    return a_security_group


#--------------------------------------------------------------------------------------
