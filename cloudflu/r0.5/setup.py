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
"""
This script is responsible for the task packaging and sending it for execution in a cloud
"""

#--------------------------------------------------------------------------------------
import sys, os, os.path

# To avoid using previoulsy cached contents for the distributed package
an_engine = sys.argv[ 0 ]
an_engine_dir = os.path.abspath( os.path.dirname( sys.argv[ 0 ] ) )
a_manifest_file = os.path.join( an_engine_dir, 'MANIFEST' )
if os.path.isfile( a_manifest_file ) :
    os.remove( a_manifest_file )
    pass

an_engine = os.path.basename( an_engine )

# To generate list of automatically distributed scripts
a_scripts = []
for a_file in os.listdir( an_engine_dir ) :
    if a_file == an_engine :
        continue

    if os.path.isfile( a_file ) : 
        if os.access( a_file, os.X_OK ) :
            a_scripts.append( a_file )
            pass
        pass
    pass


#-------------------------------------------------------------------------------------
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages
import cloudflu

os.chdir( an_engine_dir ) # Run from the proper folder

setup( name = cloudflu.NAME,
       description = 'Delivers "Cloud Computing" commodities for OpenFOAM(R) users',
       long_description = """Sends user data in a cloud cluster, runs the appointed solver and feteches the output results back to the user""",
       author = 'Alexey Petrov',
       author_email = 'alexey.petrov.nnov@gmail.com', 
       license = 'Apache License, Version 2.0',
       url = 'http://sourceforge.net/projects/cloudflu',
       install_requires = [ 'boto >= 2.0b3', 'workerpool', 'paramiko', 'pexpect' ],
       platforms = [ 'linux' ],
       version = cloudflu.VERSION,
       classifiers = [ 'Development Status :: 3 - Alpha',
                       'Environment :: Console',
                       'Intended Audience :: Science/Research',
                       'License :: OSI Approved :: Apache Software License',
                       'Operating System :: POSIX',
                       'Programming Language :: Python',
                       'Topic :: Scientific/Engineering',
                       'Topic :: Utilities' ],
       packages = find_packages(),
       scripts = a_scripts,
       entry_points = { 'console_scripts': [
           'cloudflu-config = cloudflu.config:main',

           'cloudflu-reservation-run = cloudflu.amazon.apps.reservation_run:main',

           'cloudflu-reservation-ls = cloudflu.amazon.apps.reservation_ls:main',
           'cloudflu-cluster-ls = cloudflu.amazon.apps.reservation_ls:main',

           'cloudflu-cluster-rm = cloudflu.amazon.apps.reservation_rm:main',

           'cloudflu-instance-extract = cloudflu.amazon.apps.instance_extract:main',

           'cloudflu-deploy = cloudflu.common.deploy:main',

           'cloudflu-credentials-deploy = cloudflu.amazon.apps.credentials_deploy:main',

           'cloudflu-ssh = cloudflu.common.ssh.run:main',

           'cloudflu-openmpi-config = cloudflu.amazon.apps.openmpi_config:main',

           'cloudflu-nfs-config = cloudflu.amazon.apps.nfs_config:main',

           'cloudflu-solver-start = cloudflu.amazon.apps.solver_start:main',

           'cloudflu-solver-process = cloudflu.amazon.apps.solver_process:main',

           'cloudflu-study-book = cloudflu.amazon.apps.study_book:main',

           'cloudflu-upload-start = cloudflu.amazon.apps.upload_start:main',

           'cloudflu-upload-resume = cloudflu.amazon.apps.upload_resume:main',

           'cloudflu-study-upload = cloudflu.amazon.apps.data_upload:main',

           'cloudflu-timestamps-upload = cloudflu.amazon.apps.timestamps_upload:main',

           'cloudflu-study-seal = cloudflu.amazon.apps.study_seal:main',

           'cloudflu-download = cloudflu.amazon.apps.download:main',

           'cloudflu-ls = cloudflu.amazon.apps.ls:main',

           'cloudflu-study-rm = cloudflu.amazon.apps.study_rm:main',

           'cloudflu-rm = cloudflu.amazon.apps.rm:main',

           'cloudflu-servers-clean = cloudflu.amazon.apps.servers_clean:main',

           'cloudflu-files-clean = cloudflu.amazon.apps.files_clean:main'
           ] },
       zip_safe = True )


#--------------------------------------------------------------------------------------

