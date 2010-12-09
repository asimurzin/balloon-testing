
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
from preferences import pickup; pickup()
from preferences import resource_filename; an_rcfilename = resource_filename()

import os.path;
an_rcfilename = os.path.expanduser( an_rcfilename )
an_rcfilename = os.path.abspath( an_rcfilename )

an_rcfile = open( an_rcfilename )
a_preferences = compile( "".join( an_rcfile.readlines() ), an_rcfilename, 'exec' )
an_rcfile.close()

exec a_preferences


#--------------------------------------------------------------------------------------
