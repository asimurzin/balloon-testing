
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
from balloon.common import print_e, print_d, Timer


#--------------------------------------------------------------------------------------
def region_connect( the_image_location, the_aws_access_key_id, the_aws_secret_access_key ) :
    import boto.ec2
    a_regions = boto.ec2.regions()
    print_d( 'a_regions = %s\n' % [ str( a_region.name ) for a_region in a_regions ] )

    an_image_region = None
    for a_region in a_regions :
        if a_region.name == the_image_location :
            an_image_region = a_region
            pass
        pass
    if an_image_region == None :
        print_e( "There no region with such location - '%s'\n" % an_image_region )
        pass
    print_d( 'an_image_region = < %r >\n' % an_image_region )
    
    an_ec2_conn = an_image_region.connect( aws_access_key_id = the_aws_access_key_id, 
                                           aws_secret_access_key = the_aws_secret_access_key )
    print_d( 'an_ec2_conn = < %r >\n' % an_ec2_conn )

    return an_ec2_conn


#--------------------------------------------------------------------------------------
