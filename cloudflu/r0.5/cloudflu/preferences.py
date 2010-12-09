
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
import optparse
class OptionGroup( optparse.OptionContainer ) :
    def __init__( self, the_namespace, the_title = None, the_description = None ) :
        optparse.OptionContainer.__init__( self, optparse.Option, "error", the_description )
        self._create_option_mappings()

        self._namespace = the_namespace
        self._title = the_title
        pass

    def _create_option_list( self ) :
        self.option_list = []
        pass

    def get_namespace( self ) :
        return self._namespace
    
    def get_subnamespace( self ) :
        return self._namespace.split( '.' )[ -1 ]
    
    def get_title( self ) :
        return self._title
    
    def __len__( self ) :
        return len( self.option_list )
    
    pass


#--------------------------------------------------------------------------------------
import optparse
class PersistentOption( optparse.Option ) :
    def __init__( self, *opts, **attrs ) :
        optparse.Option.__init__( self, *opts, **attrs )
        pass

    pass


#--------------------------------------------------------------------------------------
import optparse
class TransientOption( optparse.Option ) :
    def __init__( self, *opts, **attrs ) :
        optparse.Option.__init__( self, *opts, **attrs )
        pass

    pass


#--------------------------------------------------------------------------------------
def resource_filename() :
    # If user explicitly appointed a specific resource file - use it
    import os; an_rcfilename = os.getenv( "BALLOON_RCFILE" )

    if an_rcfilename == None or an_rcfilename == '' : # If no user defined file, generate a proper one
        import cloudflu; an_rcfilename = "~/.%src-%s.py" % ( cloudflu.NAME, cloudflu.VERSION )
        pass

    return an_rcfilename


#--------------------------------------------------------------------------------------
IDENTATION_PREFFIX = "    "

def ident( the_identation_level ) :
    an_identation = ""
    for id in range( the_identation_level ) :
        an_identation += IDENTATION_PREFFIX
        pass
    
    return an_identation


#--------------------------------------------------------------------------------------
def dump_resume( the_identation_level, the_option_group, the_output ) :
    for an_option in the_option_group.option_list :
        if not isinstance( an_option, PersistentOption ) :
            continue
        
        a_default = an_option.default
        a_dest = an_option.dest

        if a_dest in [ 'cluster_location', 'image_id', 'data_location', 'enable_debug', 'production', 'instance_type' ] :
            a_default = 'a_helper.%s()' % a_dest
            pass

        a_metavar = an_option.metavar
        # a_metavar = a_metavar.title()
        a_metavar = a_metavar.replace( '< ', '' )
        a_metavar = a_metavar.replace( ' >', '' )
        a_metavar = a_metavar[ 0 ].upper() + a_metavar[ 1 : ]

        a_value_format = "%r"

        if isinstance( a_default, str ) :
            a_value_format = "'%s'"
            pass

        if a_default != an_option.default :
            a_value_format = "%s"
            pass

        a_formatted_value = a_value_format % a_default

        the_output.write( ident( the_identation_level + 1 ) + "%s = %s # %s\n" %
                          ( a_dest, a_formatted_value, a_metavar ) )

        pass
    pass


#--------------------------------------------------------------------------------------
def dump_begin( the_identation_level, the_option_group, the_output ) :
    # if len( the_option_group ) == 0 :
    #     return
    
    a_section_comment = ''
    a_title = the_option_group.get_title()
    if a_title != None :
        a_section_comment = ' # %s' % a_title
        pass

    a_section_name = the_option_group.get_subnamespace();
    the_output.write( ident( the_identation_level ) + "class %s :%s\n" % ( a_section_name, a_section_comment ) )

    a_description = the_option_group.get_description()
    if a_description != None :
        the_output.write( ident( the_identation_level + 1 ) + "\"\"\" %s \"\"\"\n" % ( a_description ) )
        pass
    
    dump_resume( the_identation_level, the_option_group, the_output )

    # the_output.write( "\n" )
    pass
    

#--------------------------------------------------------------------------------------
def dump_end( the_identation_level, the_option_group, the_output ) :
    # if len( the_option_group ) == 0 :
    #     return

    the_output.write( ident( the_identation_level + 1 ) + "pass\n\n" )
    pass


#--------------------------------------------------------------------------------------
__PICKUP_CALLED__ = None

def pickup() :
    global __PICKUP_CALLED__
    if __PICKUP_CALLED__ != None:
        return
    
    from preferences import resource_filename
    an_rcfilename = resource_filename()

    import os.path;
    an_rcfilename = os.path.expanduser( an_rcfilename )
    an_rcfilename = os.path.abspath( an_rcfilename )
    if not os.path.isfile( an_rcfilename ) :
        # If resource file does not exist - write a predefined one
        an_rcfile = open( an_rcfilename, "w" )
        import cloudflu; an_rcfile.write( """
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
## Author : Automatically generated (%s-%s)
##


#--------------------------------------------------------------------------------------
REGION2PARAMS = { 'us-east-1' : [ '', { 'openfoam171_0-1ubuntu2' : 'ami-ecf50385', 
                                        'openfoam171_0-1' : 'ami-62fa0c0b', 
                                        'openfoam-dev-1.5' : 'ami-98f701f1' } ] }


#--------------------------------------------------------------------------------------
class Helper :
    def __init__( self, the_ec2_region, the_openfoam_version, the_debug = False, the_develop = False ) :
        self._cluster_location = the_ec2_region
        self._data_location = REGION2PARAMS[ the_ec2_region ][ 0 ]
        self._image_id = REGION2PARAMS[ the_ec2_region ][ 1 ][ the_openfoam_version ]

        self._enable_debug = the_debug
        self._develop = the_develop

        self._instance_type = 'c1.xlarge'
        if the_debug == True :
            self._instance_type = 'm1.large'
            pass

        pass

    def cluster_location( self ) :
        return self._cluster_location

    def image_id( self ) :
        return self._image_id
    
    def data_location( self ) :
        return self._data_location
    
    def enable_debug( self ) :
        return self._enable_debug
    
    def production( self ) :
        return not self._develop
    
    def instance_type( self ) :
        return self._instance_type
    
    pass


#--------------------------------------------------------------------------------------
a_helper = Helper( 'us-east-1', 'openfoam171_0-1ubuntu2' )


#--------------------------------------------------------------------------------------
""" % ( cloudflu.NAME, cloudflu.VERSION ) )

        import cStringIO
        an_output = cStringIO.StringIO()

        from common.options import dump as common_dump;  common_dump( 0, an_output )

        from amazon.options import dump as amazon_dump;  amazon_dump( 0, an_output )
        
        an_rcfile.write( an_output.getvalue() )

        an_rcfile.write( '\n' )
        an_rcfile.write( '#--------------------------------------------------------------------------------------' )
        an_rcfile.write( '\n' )
    
        an_rcfile.close()

        import stat
        # os.chmod( an_rcfilename, stat.S_IRUSR ) # To protect user data
        pass

    __PICKUP_CALLED__ = True

    pass

    
#--------------------------------------------------------------------------------------
PREFERENCES2ENVIROMENT={ 'amazon.cluster.location' : '__CLOUDFLU_IMAGE_LOCATION__',
                         'amazon.data_transfer.location' : '__CLOUDFLU_S3_LOCATION__' }


#--------------------------------------------------------------------------------------
def get_from_enviroment( the_namespace ):
    import os; a_value = os.getenv( PREFERENCES2ENVIROMENT[ the_namespace ] )
    if a_value == None or a_value == '':
        raise Exception()
    
    return a_value


#--------------------------------------------------------------------------------------
def check_disabled( the_namespace ):
    if the_namespace in [ 'common.proxy.proxy_address', 'common.proxy.proxy_port', 'common.proxy.proxy_user', 'common.proxy.proxy_pass' ] :
        return None
    
    raise Exception()


#--------------------------------------------------------------------------------------
def get( the_namespace ) :
    try:
        return get_from_enviroment( the_namespace )
    except:
        pass
    
    try:
        return check_disabled( the_namespace )
    except:
        pass
    
    a_value = None
    try:
        import pickup
        an_expression = 'a_value = pickup.%s' % ( the_namespace )

        exec an_expression

        if a_value != None and a_value != 'None' :
            return a_value
        
        pass
    except :
        import sys, traceback
        traceback.print_exc( file = sys.stderr )
        raise Exception()
        pass
    
    return None


#--------------------------------------------------------------------------------------
def add_options( the_option_parser, the_option_group ) :
    an_option_prefix = the_option_group.get_namespace()

    a_title = the_option_group.get_title()
    if a_title == None :
        a_title = an_option_prefix
        pass
    
    an_option_group = None
    for a_group in the_option_parser.option_groups :
        if a_title == a_group.title :
            an_option_group = a_group
            break
        
        pass

    a_description = the_option_group.get_description()

    if an_option_group == None :
        an_option_group = optparse.OptionGroup( the_option_parser, a_title, a_description )
        pass

    import pickup
    for an_option in the_option_group.option_list :
        if isinstance( an_option, PersistentOption ) :
            try:
                a_value = None
                an_expression = 'a_value = pickup.%s.%s' % ( an_option_prefix, an_option.dest )

                exec an_expression
                
                if a_value != None and a_value != 'None' :
                    an_option.default = a_value
                    pass
                
                pass
            except :
                import sys, traceback
                traceback.print_exc( file = sys.stderr )
                raise Exception()
                pass
            
            pass

        an_option_group.add_option( an_option )
        pass

    if len( the_option_group ) > 0 and not an_option_group in the_option_parser.option_groups :
        the_option_parser.add_option_group( an_option_group )
        pass
    
    pass


#--------------------------------------------------------------------------------------
def template_add( the_option_parser, the_container ) :
    add_options( the_option_parser, the_container)
    pass


#------------------------------------------------------------------------------------------
def template_dump( the_identation_level, the_container, the_output ) :
    from cloudflu.preferences import dump_begin
    dump_begin( the_identation_level, the_container, the_output )

    from cloudflu.preferences import dump_end
    dump_end( the_identation_level, the_container, the_output )
    pass


#--------------------------------------------------------------------------------------
def correct_value( the_value ) :
    if the_value == "" or the_value == "''" :
        return None
    
    if the_value.startswith( '/dev/fd/' ) :
        from cloudflu.common import sh_command
        a_stdout_lines = sh_command( 'cat %s' % the_value )
        the_value = a_stdout_lines[ 0 ][ : -1 ]
        pass

    return the_value


#--------------------------------------------------------------------------------------
def get_raw_input() :
    try:
        a_values = raw_input()
    except:
        import sys, os; sys.exit( os.EX_UNAVAILABLE )
        pass
    
    a_values = a_values.split( ' ' )
    
    return correct_value( a_values[ 0 ] ), a_values[ 1 : ]


#--------------------------------------------------------------------------------------
def get_input( the_args ) :
    try:
        return correct_value( the_args[ 0 ] ), the_args[ 1 : ]
    except:
        pass

    return get_raw_input()


#--------------------------------------------------------------------------------------
def correct_values( the_values ) :
    a_values = []
    for a_value in the_values :
        if a_value == "" or a_value == "''" :
            a_values.append( None )
        else:
            a_values.append( a_value )
            pass
        pass
    
    return a_values


#--------------------------------------------------------------------------------------
def get_inputs( the_args ) :
    if len( the_args ) > 0 :
        return correct_values( the_args )

    try:
        a_values = [ raw_input() ]
    except:
        import sys, os; sys.exit( os.EX_UNAVAILABLE )
        pass
    
    return correct_values( a_values )


#--------------------------------------------------------------------------------------
