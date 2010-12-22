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
def create_test_file( the_size ) :
    import tempfile
    a_filename = tempfile.mkstemp( prefix = '%d-' % the_size )[ 1 ]

    import os
    os.system( 'dd if=/dev/zero of=%s bs=%d count=1 > /dev/null 2>&1' % ( a_filename, the_size ) )

    return a_filename


#--------------------------------------------------------------------------------------
def delete_object( the_object ):
    an_allright = False
    while not an_allright:
       try:
         the_object.delete()
         an_allright = True
       except:
         pass 
    pass
    

#--------------------------------------------------------------------------------------
class SeedSizeMesurement :
    #------------------------------------------------------------------------------------
    def __init__( self, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, the_region, the_initial_size = 8192 ) :
        #---------------------------- Adjust 'boto' functionality -----------------------------
        import ConfigParser
        a_config_parser = ConfigParser.SafeConfigParser()
        a_config_parser.add_section( 'Boto' )
        a_config_parser.set( 'Boto', 'num_retries', '0' )

        import tempfile
        self._config_file = tempfile.mkstemp()[ 1 ]
        a_boto_config = open( self._config_file, 'w' )
        a_config_parser.write( a_boto_config )
        a_boto_config.close()

        import os
        os.environ[ 'BOTO_CONFIG' ] = self._config_file

        #------------------------------ Create a testing bucket -------------------------------
        from boto.s3.connection import S3Connection
        self._conn = S3Connection( aws_access_key_id = AWS_ACCESS_KEY_ID, 
                                   aws_secret_access_key = AWS_SECRET_ACCESS_KEY )
        import uuid
        a_backet_name = "config-" + str( uuid.uuid4() )
        self._backet = self._conn.create_bucket( a_backet_name, location = the_region )


        #---------------------------- Estimate the timeout value ------------------------------
        a_filesize = the_initial_size
        a_filename = create_test_file( a_filesize )
        
        from boto.s3.key import Key    
        a_key = Key( self._backet, a_filename )

        import time
        a_start_time = time.time()
        a_key.set_contents_from_filename( a_filename )
        a_end_time = time.time()
        self._timeout = a_end_time - a_start_time
        print "timeout = %3.2f sec" % ( self._timeout )

        import socket
        socket.setdefaulttimeout( self._timeout )

        delete_object( a_key )
        import os; os.remove( a_filename )
        pass


    #------------------------------------------------------------------------------------
    def timeout( self ):
        return self._timeout + 1.0


    #------------------------------------------------------------------------------------
    def __call__( self, the_filesize ):
      a_filename = create_test_file( the_filesize )

      from boto.s3.key import Key
      a_key_name = 'test_' + str( the_filesize )
      a_key = Key( self._backet, a_filename )

      a_speed = 0
      try:
          import time
          a_start_time = time.time()
          a_key.set_contents_from_filename( a_filename )
          a_end_time = time.time()
          
          delete_object( a_key )

          a_time = a_end_time - a_start_time
          a_speed = ( float( the_filesize * 8 ) / a_time ) / 1024          
      except Exception, exc:
          delete_object( a_key )
          pass

      import os; os.remove( a_filename )

      return a_speed
    
    
    #------------------------------------------------------------------------------------
    def __del__( self ) :
        import os; os.remove( self._config_file )
        delete_object( self._backet )
        print '__del__'
        pass
    pass


#--------------------------------------------------------------------------------------
class TFilterFunctor :
    def __init__( self, the_start, the_end, the_precision = 1.0E-8 ) :
        self._precision = the_precision
        self._start = the_start
        self._end = the_end
        pass

    def __call__( self, the_x ) :
        return ( self._start - the_x ) < self._precision and ( the_x - self._end ) < self._precision
    
    pass


#--------------------------------------------------------------------------------------
def print_dict( the_x2y ) :
    a_xs = the_x2y.keys()
    a_xs.sort()
    for a_x in a_xs :
        print "%4d : %4.0f" % ( a_x, the_x2y[ a_x ] )
        pass
    pass


#--------------------------------------------------------------------------------------
def print2_dict( the_sub_xs, the_x2y ) :
    a_counter = 1
    an_y_integral = 0.0

    a_xs = the_x2y.keys()
    a_xs.sort()
    for a_x in a_xs :
        if a_x in the_sub_xs :
            print " + ", 
        else:
            print " - ", 
            pass
        print "%4d : %4.0f" % ( a_x, the_x2y[ a_x ] )
        a_counter += 1
        pass
    pass


#--------------------------------------------------------------------------------------
def find_center( the_x2y, the_sub2_nb_attempts ) :
    an_average_y = {}

    a_xs = the_x2y.keys()
    a_nb_attempts = len( a_xs )

    a_xs.sort()
    for an_id in range( a_nb_attempts ) :
        a_center_x = a_x = a_xs[ an_id ]
        an_y = the_x2y[ a_x ]

        a_neighbor_nb_attemps = 0

        # print "[", 
        if an_id < the_sub2_nb_attempts :
            a_neighbor_nb_attemps += an_id
            for a_sub_id in range( an_id ) :
                a_x = a_xs[ a_sub_id ]
                an_y += the_x2y[ a_x ]
                # print "%4d" % a_x,
                pass
            pass
        else:
            a_neighbor_nb_attemps += the_sub2_nb_attempts
            for a_sub_id in range( an_id - the_sub2_nb_attempts, an_id ) :
                a_x = a_xs[ a_sub_id ]
                an_y += the_x2y[ a_x ]
                # print "%4d" % a_x,
                pass
            pass

        # print "| %4d |" % a_center_x,

        if a_nb_attempts - an_id < the_sub2_nb_attempts :
            a_neighbor_nb_attemps += a_nb_attempts - an_id
            for a_sub_id in range( an_id, a_nb_attempts ) :
                a_x = a_xs[ a_sub_id ]
                an_y += the_x2y[ a_x ]
                # print "%4d" % a_x,
                pass
            pass
        else:
            a_neighbor_nb_attemps += the_sub2_nb_attempts
            for a_sub_id in range( an_id, an_id + the_sub2_nb_attempts ) :
                a_x = a_xs[ a_sub_id ]
                an_y += the_x2y[ a_x ]
                # print "%4d" % a_x, 
                pass
            pass
        an_average_y[ a_center_x ] = an_y / a_neighbor_nb_attemps
        # print "] = %4d" % an_average_y[ a_center_x ]

        pass

    #------------------------------------------------------------------------------------------
    # Finding out the best interval based on the corresponding average values
    a_max_average_y = 0.0
    an_average_y_index = 0
    for an_id in range( len( a_xs ) ) :
        a_x = a_xs[ an_id ]
        an_y = an_average_y[ a_x ]

        if an_y > a_max_average_y :
            an_average_y_index = an_id
            a_max_average_y = an_y
            pass

        pass

    a_center_x = a_xs[ an_average_y_index ]

    #------------------------------------------------------------------------------------------
    # Shift the 'center' to avoid mesurement of the same points
    if an_average_y_index == 0 :
        a_center_x -= ( a_xs[ an_average_y_index + 1 ] - a_xs[ an_average_y_index ] ) / 3.0
    elif an_average_y_index == a_nb_attempts - 1 :
        a_center_x += ( a_xs[ an_average_y_index ] - a_xs[ an_average_y_index - 1 ] ) / 3.0
    else:
        a_left_x = a_xs[ an_average_y_index - 1 ]
        a_right_x = a_xs[ an_average_y_index + 1 ]
        if an_average_y[ a_left_x ] < an_average_y[ a_right_x ] :
            a_center_x += ( a_right_x - a_center_x ) / 3.0
        else:
            a_center_x -= ( a_center_x - a_left_x ) / 3.0
            pass
        pass

    print "center: %4d - < value >: %4d\n" % ( a_center_x, a_max_average_y )    
    
    return a_center_x, a_max_average_y


#--------------------------------------------------------------------------------------
def update_x2y( the_fun, the_x2y, the_x ) :
    the_x2y[ the_x ] = the_fun( the_x )
    pass


#--------------------------------------------------------------------------------------
def get_stats( the_fun, the_x2y, the_cost, the_center_x, the_region_x, the_nb_attempts ) :
    a_half_area = ( the_center_x * the_region_x ) / 100.0
    a_start_x = the_center_x - a_half_area
    an_end_x = the_center_x + a_half_area

    an_area = 2.0 * a_half_area
    if a_start_x < 1.0 : # The special Amazon workaround
        a_start_x = 1000.0
        an_area = an_end_x - a_start_x
        pass

    print "[ %4d - %4d ] : " % ( a_start_x, an_end_x )

    a_sub_xs = []
    a_x = an_end_x
    a_step = an_area / float( the_nb_attempts )
    for an_id in range( the_nb_attempts + 1 ) :
        if not the_x2y.has_key( a_x ) : 
            update_x2y( the_fun, the_x2y, a_x )
            a_sub_xs.append( a_x )
            the_cost += a_x
            pass
        a_x -= a_step
        pass

    print2_dict( a_sub_xs, the_x2y )
    print "cost : %4d\n" % the_cost

    return the_x2y, the_cost, an_area


#--------------------------------------------------------------------------------------
def entry_point( the_fun, the_center_x, the_region_x, the_precision, the_nb_attempts, the_get_stats = get_stats ) :
    """The idea of this algorithm is very close to the 'interval' one; it supposes that the best value of a 
    probabilty nature function - F( x ) had better be defined through a some 'neighborhood', which could give
    more realistic representation of what is happenning in fact, not a precise point.

    This algorithm, like 'interval' one, designed in that way that it accumulates the statistics to be able 
    to make more 'proven' choice in whatever time over all the obtained results, not just currently calculated.
    So, it has good level of resistance to be caught in a local trap.
    
    Note, that the cost of F( x ) mesurement is much higher than whatever algorithmic tricks are applied over 
    the mesured results.
    
    The 'success' condition for this algorithm is when the function values on successive neighborhoods start
    differ less than the given 'precision'.

    This algorithm overcomes the initial limitation of the other two ( 'division by two' & 'interval probability' )
    in the point that it does not look for a solution within a given 'interval', instead it just starts to look
    from a given point with a given neighborhood, but can move in whatever direction and scale to reach the 'success'.
    
    As well, this algorithm is more universal in compare with 'interval' one, because it does not use any insights 
    about the possible shape and function behaviour. From this point, it could be used for any application of that 
    sort.
    
    The result for this algorithm is the central point in the most successful 'neighborhod', which would give us
    the higher combination of F( x ) * P( x ) expression.

    Attention, this algorithm will be satisfied even with low 'probability' behaviour functions, but the result 
    could be not what you are looking for. So, the best practise to use this algorithm it is to start it from a steady
    'probability'neighborhod that the algorithm will be able to distinguish the right trend ( in some ways, it works 
    like a dog; you need to give him a good hook first to make sure that he understood what you are looking for ).
    """
    a_center_x = the_center_x
    print "%4d - %4d\n" % ( a_center_x, 0.0 )
    a_sub_nb_attempts = the_nb_attempts / 1
    a_cost = 0.0
    a_x2y = {}

    #------------------------------------------------------------------------------------------
    a_max_average_y = 0.0
    a_precision = float( the_precision / 100.0 )
    while True:
        a_max_average_y2 = a_max_average_y
        a_center_x2 = a_center_x

        a_x2y, a_cost, an_area = the_get_stats( the_fun, a_x2y, a_cost, a_center_x, the_region_x, the_nb_attempts )
        a_center_x, a_max_average_y = find_center( a_x2y, a_sub_nb_attempts )

        if a_max_average_y < a_precision :
            continue

        import math
        if math.fabs( a_max_average_y - a_max_average_y2 ) / a_max_average_y > a_precision :
            continue

        if math.fabs( a_center_x - a_center_x2 ) / a_center_x > a_precision :
            continue

        break


    #------------------------------------------------------------------------------------------
    an_optimize_x = a_center_x
    print "solution : %4d / cost : %4d\n" % ( an_optimize_x, a_cost )

    return an_optimize_x, a_cost


#--------------------------------------------------------------------------------------
def main() :
    #----------------------- Defining utility command-line interface -------------------------    
    from cloudflu import amazon

    an_usage_description = "%prog --precision=10 --start-size=65536 --solution-window=50 --number-mesurements=5"

    from cloudflu import VERSION
    a_version = "%s" % VERSION

    from optparse import IndentedHelpFormatter
    a_help_formatter = IndentedHelpFormatter( width = 127 )

    from optparse import OptionParser
    an_option_parser = OptionParser( usage = an_usage_description, version = a_version, formatter = a_help_formatter )


    #----------------------- Definition of the command line arguments ------------------------
    an_option_parser.add_option( "--precision",
                                 metavar = "< algorithm precision, % >",
                                 type = "int",
                                 action = "store",
                                 dest = "precision",
                                 help = "(%default, by default)",
                                 default = 10 )
    
    an_option_parser.add_option( "--start-size",
                                 metavar = "< start value for the search algorithm, bytes >",
                                 type = "int",
                                 action = "store",
                                 dest = "start_size",
                                 help = "(%default, by default)",
                                 default = 65536 )
    
    an_option_parser.add_option( "--solution-window",
                                 metavar = "< initial solution window considered to, %>",
                                 type = "int",
                                 action = "store",
                                 dest = "solution_window",
                                 help = "(%default, by default)",
                                 default = 50 )
                             
    an_option_parser.add_option( "--number-mesurements",
                                 metavar = "< number mesurements to be done in the solution window>",
                                 type = "int",
                                 action = "store",
                                 dest = "number_mesurements",
                                 help = "(%default, by default)",
                                 default = 5 )
    
    amazon.security_options.add( an_option_parser )

    
    #------------------ Extracting and verifying command-line arguments ----------------------
    an_options, an_args = an_option_parser.parse_args()

    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = amazon.security_options.extract( an_option_parser )

    a_precision = an_options.precision

    a_center_x = an_options.start_size

    a_region_x = an_options.solution_window

    a_nb_attempts = an_options.number_mesurements

    from cloudflu.preferences import get
    a_data_location = get( 'amazon.data_transfer.location' )

    an_engine = SeedSizeMesurement( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, a_data_location )

    from cloudflu.common import Timer
    a_spent_time = Timer()

    an_optimize_x, a_cost = entry_point( an_engine, a_center_x, a_region_x, a_precision, a_nb_attempts, get_stats )

    from preferences import resource_filename; an_rcfilename = resource_filename()

    import time; an_rcfilename_save = '%s_%s' % ( an_rcfilename, time.strftime( '%Y-%m-%d_%H:%M' ) )

    import os; os.system( "cp %s %s" % ( an_rcfilename, an_rcfilename_save ) )

    import os; os.system( "perl -p -i -e 's/(socket_timeout =)\s*[0-9]+/\\1 %d/' %s" % 
                          ( an_engine.timeout(), an_rcfilename ) )

    import os; os.system( "perl -p -i -e 's/(upload_seed_size =)\s*[0-9]+/\\1 %d/' %s" % 
                          ( an_optimize_x, an_rcfilename ) )

    print "a_spent_time = %s, sec\n" % a_spent_time
    pass


#------------------------------------------------------------------------------------------
if __name__ == '__main__' :
    main()
    pass


#------------------------------------------------------------------------------------
