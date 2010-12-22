
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
import options
import communication_options
import concurrency_options
import ssh


#--------------------------------------------------------------------------------------
import os, os.path, sys, hashlib
from subprocess import *


#---------------------------------------------------------------------------
import threading; PRINTING_LOCK = threading.Lock()
PRINTING_DEPTH = 0

def get_preffix( the_preffix, the_printing_depth ) :
    "Calaculate a preffix identation according to the current printing stack depth"
    a_preffix = ""
    for id in range( the_printing_depth ) :
        a_preffix += the_preffix
        pass

    return a_preffix


#---------------------------------------------------------------------------
def print_d( the_message, the_printing_depth = 0 ) :
    "Optional printing of debug messages"
    PRINTING_LOCK.acquire()

    from options import is_debug
    if is_debug() : 
        sys.stderr.write( get_preffix( "    ", the_printing_depth ) + the_message )
    else:
        sys.stderr.write( '.' )
        pass

    PRINTING_LOCK.release()
    pass


#---------------------------------------------------------------------------
def print_i( the_message, the_printing_depth = 0 ) :
    "Optional printing of debug messages"
    print_d( "\n" )

    print_d( the_message, the_printing_depth )

    pass


#---------------------------------------------------------------------------
def print_list( the_list, the_printing_depth = 0 ) :
    "Optional printing of debug messages"
    from options import is_debug

    if not is_debug() : 
        return

    for an_item in the_list :
        print_d( "%s\n" % ( an_item ), the_printing_depth ) 
        pass
    pass


#---------------------------------------------------------------------------
def print_traceback( the_printing_depth = 0 ) :
    "Optional printing of debug messages"
    import cStringIO, traceback

    a_stream = cStringIO.StringIO()
    traceback.print_exc( file = a_stream )
    
    print_list( a_stream.getvalue().split( "\n" ), the_printing_depth )
    pass


#---------------------------------------------------------------------------
def print_e( the_message, the_exit = True ) :
    "Printing of error message and quit"
    PRINTING_LOCK.acquire()

    sys.stderr.write( "\n" )
    sys.stderr.write( "---------------------------------- ERROR ----------------------------------\n" )

    sys.stderr.write( the_message )
    
    sys.stderr.write( "----------------------------------- KO ------------------------------------\n" )

    PRINTING_LOCK.release()

    if the_exit == True :
        os._exit( os.EX_USAGE )
        pass

    pass


#---------------------------------------------------------------------------
def sh_command( the_command, the_printing_depth = 0 ) :
    "Execution of shell command"
    print_d( "(%s)\n" % the_command, the_printing_depth )
    
    a_pipe = Popen( the_command, stdout = PIPE, stderr = PIPE, shell = True )

    a_return_code = os.waitpid( a_pipe.pid, 0 )[ 1 ]

    a_stderr_lines = a_pipe.stderr.readlines()
    for a_line in a_stderr_lines : print_d( "\t%s" % a_line )

    a_stdout_lines = a_pipe.stdout.readlines()
    for a_line in a_stdout_lines : print_d( "\t%s" % a_line )

    if a_return_code != 0 :
        raise OSError( "(%s)\n" % the_command )
        pass
    
    return a_stdout_lines


#--------------------------------------------------------------------------------------
def arg_list_separator():
    import os
    if os.getenv( "__CLOUDFLU_ARG_LIST_SEPARATOR__" ) != None:
       return os.getenv( "__CLOUDFLU_ARG_LIST_SEPARATOR__" )

    return '|'


#---------------------------------------------------------------------------
def print_args( the_args, the_separator ) :
    "Prints command-line args through given  separator"
    a_result = ''
    an_args_length = len( the_args )
    for an_id in range( an_args_length ) :
        an_arg = the_args[ an_id ]

        if an_arg == None :
            continue

        a_result += the_args[ an_id ]

        if an_id == an_args_length - 1 :
            break

        a_result += the_separator
        pass

    return a_result


#--------------------------------------------------------------------------------------
class Timer :
    def __init__( self ) :
        import time
        self.initial = time.time()
        pass

    def __str__( self ) :
        import time
        return str( "%f" % ( time.time() - self.initial ))

    pass


#------------------------------------------------------------------------------------------
import workerpool
from workerpool.pools import default_worker_factory

class WorkerPool( workerpool.WorkerPool ) :
    "Run all the registered tasks in parallel"
    def __init__( self, size = 1, maxjobs = 0, worker_factory = default_worker_factory ) :
        workerpool.WorkerPool.__init__( self, size, maxjobs, worker_factory )

        from workerpool.pools import Queue
        self.results = Queue()
        pass

    def charge( self, the_function, *the_args ) :
        "Perform a map operation distributed among the workers. Will block until done."
        from workerpool import SimpleJob
        self.put( SimpleJob( self.results, the_function, *the_args ) )

        pass

    def is_all_right( self ) :
        self.join()

        a_result = True
        for i in range( self.results.qsize() ):
            a_result &= self.results.get()
            self.results.task_done()
            pass

        return a_result

    pass


#--------------------------------------------------------------------------------------
class TaggedWorkerPool( WorkerPool ) :
    "Run all the registered tasks in parallel"
    def __init__( self, size = 1, maxjobs = 0, worker_factory = default_worker_factory ) :
        WorkerPool.__init__( self, size, maxjobs, worker_factory )

        self._unique_tag_names = set()
        pass

    def charge( self, the_tag_name, the_function, *the_args ) :
        "Perform a map operation distributed among the workers. Will block until done."

        if the_tag_name != None :
            if the_tag_name in self._unique_tag_names :
                return 

            self._unique_tag_names.add( the_tag_name )
            pass

        WorkerPool.charge( self, the_function, *the_args )
        pass

    pass


#--------------------------------------------------------------------------------------
def compute_md5( the_file_pointer ) :
    from boto.s3.key import Key

    return Key().compute_md5( the_file_pointer )


#--------------------------------------------------------------------------------------
