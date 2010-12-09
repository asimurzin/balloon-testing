

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
def wait4activation( the_instance ) :
    while True :
        try :
            print_d( '%s ' % the_instance.update() )
            break
        except :
            continue
        pass
    
    # Making sure that corresponding instances are ready to use
    while True :
        try :
            if the_instance.update() == 'running' :
                break
            print_d( '.' )
        except :
            continue
        pass
    
    print_d( ' %s\n' % the_instance.update() )

    pass


#--------------------------------------------------------------------------------------
def get_identity_filedir() :
    import os.path
    a_key_pair_dir = os.path.expanduser( "~/.ssh")

    if not os.path.exists( a_key_pair_dir ) :
        os.makedirs( a_key_pair_dir )
        pass

    return a_key_pair_dir


#--------------------------------------------------------------------------------------
def get_identity_filepath( the_key_pair_name ) :
    a_key_pair_dir = get_identity_filedir()

    an_identity_file = os.path.join( a_key_pair_dir, the_key_pair_name ) + os.path.extsep + "pem"
    
    return an_identity_file


#--------------------------------------------------------------------------------------
def run_reservation( the_image_id, the_cluster_location, the_instance_type, 
                     the_min_count, the_max_count, the_host_port,
                     the_aws_access_key_id, the_aws_secret_access_key ) :
    print_d( "\n-------------------------- Defining image location ------------------------\n" )
    an_instance_reservation_time = Timer()

    from common import region_connect
    an_ec2_conn = region_connect( the_cluster_location, the_aws_access_key_id, the_aws_secret_access_key )

    an_images = an_ec2_conn.get_all_images( image_ids = the_image_id )
    an_image = an_images[ 0 ]
    print_d( 'an_image = < %s >\n' % an_image )


    print_d( "\n---------------- Creating unique key-pair and security group --------------\n" )
    import tempfile
    an_unique_file = tempfile.mkstemp()[ 1 ]
    an_unique_name = os.path.basename( an_unique_file )
    os.remove( an_unique_file )
    print_d( "an_unique_name = '%s'\n" % an_unique_name )

    # Asking EC2 to generate a new ssh "key pair"
    a_key_pair_name = an_unique_name
    a_key_pair = an_ec2_conn.create_key_pair( a_key_pair_name )
    
    # Saving the generated ssh "key pair" locally
    a_key_pair.save( get_identity_filedir() )
    an_identity_file = get_identity_filepath( a_key_pair.name )
    print_d( "an_identity_file = '%s'\n" % an_identity_file )

    import stat; os.chmod( an_identity_file, stat.S_IRUSR )

    # Asking EC2 to generate a new "sequirity group" & apply corresponding firewall permissions
    a_security_group = an_ec2_conn.create_security_group( an_unique_name, 'temporaly generated' )
    a_security_group.authorize( 'tcp', the_host_port, the_host_port, '0.0.0.0/0' ) # ssh port
    
    
    print_d( "\n-------------------------------- Running image ----------------------------\n" )
    # Creating a EC2 "reservation" with all the parameters mentioned above
    a_reservation = an_image.run( instance_type = the_instance_type, min_count = the_min_count, max_count = the_max_count, 
                                  key_name = a_key_pair_name, security_groups = [ a_security_group.name ] )
    print_d( '< %r > : %s\n' % ( a_reservation, a_reservation.instances ) )

    for an_instance in a_reservation.instances :
        wait4activation( an_instance ) # Making sure that corresponding instances are ready to use
        pass

    return a_reservation, an_identity_file


#--------------------------------------------------------------------------------------
