
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
from cloudflu.common import print_e, print_d, WorkerPool

import os, os.path, hashlib


#--------------------------------------------------------------------------------------
class TRootObject :
    "Represents S3 dedicated implementation of study root"

    def __init__( self, the_s3_conn, the_bucket, the_id ) :
        "Use static corresponding functions to an instance of this class"
        self._connection = the_s3_conn

        self._bucket = the_bucket
        self._id = the_id

        pass
    
    def __str__( self ) :

        return "'%s'- %s" % ( self._id, self._bucket )

    @staticmethod
    def get( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY ) :
        "Looking for study root"

        from cloudflu.preferences import get
        a_proxy_address = get( 'common.proxy.proxy_address' )
        a_proxy_port = get( 'common.proxy.proxy_port' )
        a_proxy_user = get( 'common.proxy.proxy_user' )
        a_proxy_pass = get( 'common.proxy.proxy_pass' )

        import boto
        a_s3_conn = boto.connect_s3( AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,
                                     proxy = a_proxy_address, 
                                     proxy_port = a_proxy_port, 
                                     proxy_user = a_proxy_user, 
                                     proxy_pass = a_proxy_pass )
        an_id = a_s3_conn.get_canonical_user_id()

        import hashlib
        a_bucket_name = hashlib.md5( an_id ).hexdigest()

        a_bucket = None
        try :
            a_bucket = a_s3_conn.get_bucket( a_bucket_name )
        except :
            a_bucket = a_s3_conn.create_bucket( a_bucket_name )
            pass
        
        return TRootObject( a_s3_conn, a_bucket, an_id )
    
    def _next( self ) :
        for a_study_key in self._bucket.list( prefix = _decorate_key_name( study_name_prefix() ) ) :
            try :
                yield TStudyObject._get( self, get_key_name( a_study_key ) )
            except :
                print_d( "study '%s' has no corresponding bucket\n" % get_key_name( a_study_key ) )
                pass
            
            pass
        
        pass

    def __iter__( self ) :
        "Iterates through study files"
        
        return self._next()

    pass


#--------------------------------------------------------------------------------------
def api_version() :

    return '0.5'


#--------------------------------------------------------------------------------------
def _id_separator( the_api_version ) :
    if the_api_version == 'dummy' :
        return '|'

    return ' | '


#--------------------------------------------------------------------------------------
def generate_id( the_parent_id, the_child_name, the_api_version ) :
    a_separator = _id_separator( the_api_version )
    a_child_id = '%s%s%s' % ( the_parent_id, a_separator, the_child_name )

    a_bucket_name = hashlib.md5( a_child_id ).hexdigest()

    return a_child_id, a_bucket_name


#--------------------------------------------------------------------------------------
def _decorate_key_name( the_name ) :
    # This workaround make possible to use '/' symbol at the beginning of the key name

    return '# %s' % the_name


#--------------------------------------------------------------------------------------
def get_key_name( the_key ) :

    return the_key.name[ 2 : ]


#--------------------------------------------------------------------------------------
def get_key( the_parent_bucket, the_name ) :
    a_decorated_name = _decorate_key_name( the_name )

    from boto.s3.key import Key

    return Key( the_parent_bucket, a_decorated_name )


#--------------------------------------------------------------------------------------
class TSealingObject :
    """"Provides generic sealing functionality"""
    def __init__( self, the_bucket ) :
        "Use static corresponding functions to an instance of this class"
        self._bucket = the_bucket
        self._prefix = None
        pass

    def _seal_name( self ) :
        "Ontains an unique seal name for each study object"
        if self._bucket == None : # in case of broken entity
            return None
        a_seal_name = self._prefix + "_seal"
        return a_seal_name

    def prefix( self ):
        return self._prefix
        
    def _seal_key( self ) :
        "Generates an unique seal key for each study object"
        return get_key( self._bucket, self._seal_name() )

    def seal( self ) :
        "To mark the everything was sucessfuly uploaded"
        self._seal_key().set_contents_from_string( 'x' )
        pass

    def sealed( self ) :
        try:
            self._seal_key().get_contents_as_string()
            return True
        except:
            pass

        return False

    class TIterator :
        def __init__( self, the_bucket, the_seal_name, the_prefix ) :
            self._bucket = the_bucket
            self._seal_name = the_seal_name
            self._prefix = _decorate_key_name( the_prefix )
            pass

        def __iter__( self ) :
            if self._bucket == None : # in case of broken entity
                return 

            for an_entity_key in self._bucket.list( prefix = self._prefix ) :
                if get_key_name( an_entity_key ) == self._seal_name :
                    continue

                yield an_entity_key
                pass
        
            pass

        pass

    def iterator( self ) :
        return self.TIterator( self._bucket, self._seal_name(), self._prefix )

    def delete( self ) :
        if self._bucket == None :
            return

        self._seal_key().delete()
        pass

    pass

#--------------------------------------------------------------------------------------
def create_region_bucket_name( the_root_id, the_location ):
    import hashlib
    a_bucket_name = hashlib.md5( the_root_id + "_" + the_location ).hexdigest()

    return a_bucket_name


#--------------------------------------------------------------------------------------
def check_study_name( the_root_bucket, the_study_name ):
    a_study_key_name = _decorate_key_name( study_key_name( the_study_name ) )
    
    a_result = the_root_bucket.lookup( a_study_key_name )
    if a_result != None :
       raise NameError(" '%s' study already exists " % the_study_name )
    pass


#--------------------------------------------------------------------------------------
def study_name_prefix():
    return "studies"


#--------------------------------------------------------------------------------------
def study_key_name( the_study_name ):
    a_study_key_name = os.path.join( study_name_prefix(), the_study_name )
    return a_study_key_name


#--------------------------------------------------------------------------------------
def get_study_name( the_study_key_name ):
    a_study_name = os.path.relpath( the_study_key_name, study_name_prefix() )
    return a_study_name


#--------------------------------------------------------------------------------------
def study_props_prefix( the_api_version ):
    return "props"


#--------------------------------------------------------------------------------------
def study_props_key_name( the_study_name, the_api_version ):
    a_study_props_key_name = os.path.join( study_props_prefix( the_api_version ), the_study_name )
    return a_study_props_key_name


#--------------------------------------------------------------------------------------
def study_props_separator( the_api_version ):
    return "%"


#--------------------------------------------------------------------------------------
def read_study_props( the_study_props, the_api_version ):
    a_study_props = the_study_props.split( study_props_separator( the_api_version ) )
    
    a_location = a_study_props[ 0 ]
    return a_location


#--------------------------------------------------------------------------------------
class TStudyObject( TSealingObject ) :
    "Represents S3 dedicated implementation of study object"

    def __init__( self, the_root_object, the_key, the_props_key, the_bucket, the_api_version ) :
        "Use static corresponding functions to an instance of this class"
        TSealingObject.__init__( self, the_bucket )

        self._root_object = the_root_object

        self._key = the_key
        self._props_key = the_props_key
        self._bucket = the_bucket

        self._api_version = the_api_version
        self._prefix = file_name_prefix( self.name() )
        pass
    
    def root( self ) :

        return self._root_object

    def name( self ) :
        a_study_key_name = get_key_name( self._key )
        a_study_name = get_study_name( a_study_key_name )
        return a_study_name

    def connection( self ) :

        return self._root_object._connection

    def get_location( self ):
        
        return str( self._bucket.get_location() )
    
    def __str__( self ) :

        return "'%s' - '%s' - %s - %s" % ( self.name(), self._api_version, self.sealed(), self._bucket )

    @staticmethod
    def create( the_root_object, the_location, the_study_name ) :
        check_study_name( the_root_object._bucket, the_study_name )
       
        an_api_version = api_version()
        a_study_key_name = study_key_name( the_study_name )
        a_study_key = get_key( the_root_object._bucket, a_study_key_name )
        a_study_key.set_contents_from_string( an_api_version )
        
        a_study_props_key_name = study_props_key_name( the_study_name, an_api_version )
        a_study_props_key = get_key( the_root_object._bucket, a_study_props_key_name )
        a_separator = study_props_separator( an_api_version )
        a_study_props_key.set_contents_from_string( the_location + a_separator )
        
        a_bucket_name = create_region_bucket_name( the_root_object._bucket.name, the_location )
        
        try:
           a_bucket = the_root_object._connection.get_bucket( a_bucket_name )
        except:
           a_bucket = the_root_object._connection.create_bucket( a_bucket_name, location = the_location )
           
        return TStudyObject( the_root_object, a_study_key, a_study_props_key, a_bucket, an_api_version )

    @staticmethod
    def get( the_root_object, the_study_name ):
       
        a_study_key_name = study_key_name( the_study_name )
       
        return TStudyObject._get( the_root_object, a_study_key_name )
        
    @staticmethod
    def _get( the_root_object, the_study_key_name ) :
        a_study_key = get_key( the_root_object._bucket, the_study_key_name )
        
        an_api_version = None
        try:
            an_api_version = a_study_key.get_contents_as_string()
        except:
            from cloudflu.common import print_traceback
            print_traceback()

            raise NameError( "There is no '%s' study" % the_study_name )
            pass

        a_location = None
        a_study_name = get_study_name( the_study_key_name )
        a_study_props_key_name = study_props_key_name( a_study_name, an_api_version )
        a_study_props_key = get_key( the_root_object._bucket, a_study_props_key_name )
        try:
            a_study_props = a_study_props_key.get_contents_as_string()
            a_location = read_study_props( a_study_props, an_api_version )
        except:
            from cloudflu.common import print_traceback
            print_traceback()
            pass

        
        a_bucket_name = create_region_bucket_name( the_root_object._bucket.name, a_location )
        a_bucket = None
        try: # in case of broken entities
            a_bucket = the_root_object._connection.get_bucket( a_bucket_name )
        except :
            import sys, traceback
            traceback.print_exc( file = sys.stderr )
            pass
    
        return TStudyObject( the_root_object, a_study_key, a_study_props_key, a_bucket, an_api_version )

    def __iter__( self ) :
        "Iterates through study files"
        for a_file_key in self.iterator() :
            try:
                yield TFileObject._get( self, get_key_name( a_file_key ) )
            except:
                from cloudflu.common import print_traceback
                print_traceback()
            pass

            pass
        
        pass

    def delete( self, the_number_threads, the_printing_depth ) :
        print_d( "deleteting - %s\n" % self, the_printing_depth )

        a_worker_pool = WorkerPool( the_number_threads )

        a_deleter = lambda the_object, the_number_threads, the_printing_depth : \
            the_object.delete( the_number_threads, the_printing_depth )

        for a_file_object in self :
            a_worker_pool.charge( a_deleter, ( a_file_object, the_number_threads, the_printing_depth + 1 ) )
            pass
        
        TSealingObject.delete( self )
        
        a_worker_pool.shutdown()
        a_worker_pool.join()

        self._key.delete()
        self._props_key.delete()
        pass

    pass


#--------------------------------------------------------------------------------------
def file_name_prefix( the_study_name ):
    a_filename_prefix = os.path.join( the_study_name, "files" )
    return a_filename_prefix


#--------------------------------------------------------------------------------------
def _file_key_separator( the_api_version ) :
    if the_api_version < '0.3' : 
        raise NotImplementedError( "Not supported for API vesion low than 0.3" )

    return ' :: '


#--------------------------------------------------------------------------------------
def _read_file_props( the_key, the_api_version ):
    a_hex_md5, a_file_path = None, None
    a_contents = the_key.get_contents_as_string()

    if the_api_version >= "0.3" and the_api_version != 'dummy':
        a_separator = _file_key_separator( the_api_version )
        a_hex_md5, a_file_path = a_contents.split( a_separator )
    else:
        a_file_path = get_key_name( the_key )
        a_hex_md5 = a_contents
        pass

    return a_hex_md5, a_file_path


#--------------------------------------------------------------------------------------
def generate_uploading_dir( the_file_path ) :
    # import os.path; a_file_dirname = os.path.dirname( the_file_path )
    import tempfile; a_file_dirname = tempfile.gettempdir()

    import os.path; a_file_basename = os.path.basename( the_file_path )

    a_sub_folder = hashlib.md5( a_file_basename ).hexdigest()
    a_working_dir = os.path.join( a_file_dirname, a_sub_folder )
    
    return a_working_dir


#--------------------------------------------------------------------------------------
class TFileObject( TSealingObject ) :
    "Represents S3 dedicated implementation of file object"

    def __init__( self, the_study_object, the_key, the_hex_md5, the_file_path ) :
        "Use static corresponding functions to an instance of this class"
        TSealingObject.__init__( self, the_study_object._bucket )

        self._study_object = the_study_object

        self._key = the_key
        self._bucket = the_study_object._bucket

        self._hex_md5 = the_hex_md5
        self._file_path = the_file_path

        self._prefix = seed_name_prefix( self.study_name(), self.located_file() )

        pass
    
    def file_path( self ) :
        return self._file_path

    def hex_md5( self ):
        return self._hex_md5

    def located_file( self ): 
        if self.api_version() < '0.3' or self.api_version() == 'dummy':

           return get_key_name( self._key )[ 1 : ]
        
        a_located_file = get_key_name( self._key )
        a_located_file = os.path.relpath( a_located_file, self._study_object.prefix() )
        
        return a_located_file
        
    def key( self ):
        return get_key_name( self._key )
    
    def connection( self ) :
        return self._study_object._connection

    def api_version( self ) :
        return self._study_object._api_version

    def study_name( self ):
        return self._study_object.name()
    
    def __str__( self ) :
        return "'%s' - %s - '%s' - %s" % ( self.key(), self.sealed(), self._hex_md5, self._bucket )

    @staticmethod
    def create( the_study_object, the_file_path, the_file_location, the_hex_md5 ) :
        a_file_name = os.path.basename( the_file_path )
        
        a_located_file = os.path.join( the_study_object.prefix(), the_file_location, a_file_name )

        a_key = get_key( the_study_object._bucket, a_located_file )
        
        an_api_version = the_study_object._api_version

        a_separator = _file_key_separator( an_api_version )
        
        a_key.set_contents_from_string( the_hex_md5 + a_separator + the_file_path )
        
        return TFileObject( the_study_object, a_key, the_hex_md5, the_file_path )

    @staticmethod
    def get( the_study_object, the_located_file ):
        a_file_key = os.path.join( the_study_object.prefix(), the_located_file )
        
        return TFileObject._get( the_study_object, a_file_key )
    
    @staticmethod
    def _get( the_study_object, the_file_key ) :
        a_key = get_key( the_study_object._bucket, the_file_key )
        
        an_api_version = the_study_object._api_version
        
        a_hex_md5, a_file_path = _read_file_props( a_key, an_api_version )
    
        return TFileObject( the_study_object, a_key, a_hex_md5, a_file_path )

    def __iter__( self ) :
        "Iterates through file items"
        for a_seed_key in self.iterator() :
            yield TSeedObject.get( self, a_seed_key )
            pass
        
        pass

    def delete( self, the_number_threads, the_printing_depth ) :
        print_d( "deleting - %s\n" % self, the_printing_depth )

        a_worker_pool = WorkerPool( the_number_threads )

        a_deleter = lambda the_object, the_printing_depth : \
            the_object.delete( the_printing_depth )

        for a_seed_object in self :
            a_worker_pool.charge( a_deleter, ( a_seed_object, the_printing_depth + 1 ) )
            pass

        TSealingObject.delete( self )
        
        a_worker_pool.shutdown()
        a_worker_pool.join()

        self._key.delete()
        pass

    def seal( self, the_working_dir ) :
        "To mark the everything was sucessfuly uploaded"
        os.rmdir( the_working_dir )

        TSealingObject.seal( self )
        pass

    pass


#--------------------------------------------------------------------------------------
def _seed_key_separator( the_api_version ) :
    if the_api_version == 'dummy' :
        return ':'

    return ' % '


#--------------------------------------------------------------------------------------
def seed_name_prefix( the_study_name, the_located_file):
    a_seedname_prefix = os.path.join(  the_study_name, "seeds", the_located_file ) + "/"
    return a_seedname_prefix


#--------------------------------------------------------------------------------------
def generate_seed_name( the_file_object, the_hex_md5, the_file_seed, the_api_version ) :
    a_separator = _seed_key_separator( the_api_version )

    if the_api_version == 'dummy' :
        return '%s%s%s' % ( the_file_seed, a_separator, the_hex_md5 )

    if the_api_version == '0.1' :
        return '%s%s%s' % ( the_hex_md5, a_separator, the_file_seed )
    
    a_seed_prefix = the_file_object.prefix()
    a_file_seed = os.path.join( a_seed_prefix, the_file_seed )
    
    return '%s%s%s' % ( a_file_seed, a_separator, the_hex_md5 )


#--------------------------------------------------------------------------------------
def _read_seed_props( the_seed_key_name, the_api_version ) :
    a_separator = _seed_key_separator( the_api_version )

    a_seed_name, a_hex_md5 = None, None
    try:
        if the_api_version == 'dummy' :
            a_seed_name, a_hex_md5 = the_seed_key_name.split( a_separator )
        elif the_api_version == '0.1' :
            a_hex_md5, a_seed_name = the_seed_key_name.split( a_separator )
        else :
            a_seed_name, a_hex_md5 = the_seed_key_name.split( a_separator )
            pass
    except :
        pass

    return a_hex_md5, a_seed_name


#--------------------------------------------------------------------------------------
class TSeedObject :
    "Represents S3 dedicated implementation of item object"

    def __init__( self, the_file_object, the_key, the_name, the_hex_md5 ) :
        "Use static corresponding functions to an instance of this class"
        self._file_object = the_file_object

        self._key = the_key
        self._name = the_name
        self._hex_md5 = the_hex_md5

        pass
    
    def basename( self ):
        return os.path.basename( self._name )
            
    def hex_md5( self ) :
        return self._hex_md5

    def download( self, the_file_path ) :
        self._key.get_contents_to_filename( the_file_path )
        pass

    def __str__( self ) :
        return "%s" % ( self._key )

    @staticmethod
    def create( the_file_object, the_seed_name, the_seed_path ) :
        a_file_pointer = open( the_seed_path, 'rb' )

        from cloudflu.common import compute_md5
        a_md5 = compute_md5( a_file_pointer )
        a_hex_md5, a_base64md5 = a_md5

        an_api_version = the_file_object.api_version()
        
        a_seed_name = generate_seed_name( the_file_object, a_hex_md5, the_seed_name, an_api_version )

        a_seed_key = get_key( the_file_object._bucket, a_seed_name )
        # a_part_key.set_contents_from_file( a_file_pointer, md5 = a_md5 ) # this method is not thread safe
        a_seed_key.set_contents_from_file( a_file_pointer, 
                                           headers = { 'Content-Type' : 'application/x-tar' },
                                           reduced_redundancy = True ) # To speed-up the preformance
        a_file_pointer.close()
        os.remove( the_seed_path )

        return TSeedObject( the_file_object, a_seed_key, the_seed_name, a_hex_md5 )

    @staticmethod
    def get( the_file_object, the_seed_key ) :
        an_api_version = the_file_object.api_version()

        a_hex_md5, a_seed_name = _read_seed_props( get_key_name( the_seed_key ), an_api_version )

        return TSeedObject( the_file_object, the_seed_key, a_seed_name, a_hex_md5 )

    def delete( self, the_printing_depth ) :
        print_d( "deleting - %s\n" % self, the_printing_depth )

        self._key.delete()

        pass

    pass


#--------------------------------------------------------------------------------------

