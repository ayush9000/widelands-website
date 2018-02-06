#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Create the source code documenation.

This script covers all needed steps to create or recreate the documentation.
A recreating is done if the documentation was already build (the directory
'build' exists)

Needed dependency: Sphinx

"""

from __future__ import print_function
import os
import sys
import imp
import shutil
import glob
from subprocess import check_call, CalledProcessError


def get_local_settings():
    """Get local_settings from django.

    Because we are running this script from outside the Django
    environment, local_settings couldn't be imported as usual.

    """

    # Didn't find a better way to get the settings from the parent directory
    try:
        f, f_path, descr = imp.find_module('../local_settings')
        settings = imp.load_module('local_settings', f, f_path, descr)
    except ImportError as why:
        print("Couldn't find local_settings.py! ", why)
        sys.exit(1)
    else:
        f.close()

    return settings


def move_docs(settings, SPHINX_DIR):
    """Move the documentation created by sphinxdoc to the right folder.

    Dependent on Operating system create a temporary backup.

    """

    TARGET_DIR = os.path.join(settings.MEDIA_ROOT, 'documentation/new_html')
    if os.name == 'posix':
        # Creating symlinks is only available on unix systems
        LINK_NAME = os.path.join(settings.MEDIA_ROOT, 'documentation/html')
        TMP_DIR = os.path.join(settings.MEDIA_ROOT, 'documentation/old_html')

        if not os.path.exists(TARGET_DIR):
            # only needed on first run
            os.mkdir(TARGET_DIR)

        shutil.copytree(TARGET_DIR, TMP_DIR)

        if os.path.exists(LINK_NAME):
            # only needed if this script has already run
            os.remove(LINK_NAME)

        os.symlink(TMP_DIR, LINK_NAME)
        shutil.rmtree(TARGET_DIR)
        shutil.copytree(os.path.join(SPHINX_DIR, 'build/html'), TARGET_DIR)
        os.remove(LINK_NAME)
        os.symlink(TARGET_DIR, LINK_NAME)
        shutil.rmtree(TMP_DIR)
    else:
        # Non unix OS: Copy docs to main folder without using a symlink
        shutil.rmtree(TARGET_DIR)
        shutil.copytree(os.path.join(SPHINX_DIR, 'build/html'), 
                        os.path.join(settings.MEDIA_ROOT, 'documentation/html')
                        )


def create_docs():
    """Create the widelands source code documentation.

    Or renew the documenation.

    """

    settings = get_local_settings()
    SPHINX_DIR = os.path.join(settings.WIDELANDS_SVN_DIR, 'doc/sphinx')

    if not os.path.exists(SPHINX_DIR):
        print("Can't find the directory given by WIDELANDS_SVN_DIR in local_settings.py:\n", SPHINX_DIR)
        sys.exit(1)

    if os.path.exists(os.path.join(SPHINX_DIR, 'build')):

        # Clean build/html directory
        shutil.rmtree(os.path.join(SPHINX_DIR, 'build'))

        # Clean also the autogen* files created by extract_rst.py
        # This has to be done because sometimes such a file remains after
        # removing it from extract_rst. sphinx-build throughs an error then.
        try:
            for f in glob.glob(os.path.join(SPHINX_DIR, 'source/autogen*')):
                os.remove(f)
        except OSError:
            raise

    # Locally 'dirhtml' do not work because the staticfiles view disallow
    # directory indexes, but 'dirhtml' gives nicer addresses in production
    BUILDER = 'html'
    if hasattr(settings, 'DEBUG'):
        # In production we use DEBUG=False derived from local_settings
        BUILDER = 'dirhtml'

    try:
        check_call(['python', os.path.join(SPHINX_DIR, 'extract_rst.py')])
        check_call(['sphinx-build',
                    '-b', BUILDER,
                    '-d', os.path.join(SPHINX_DIR, 'build/doctrees'),
                    os.path.join(SPHINX_DIR, 'source'),
                    os.path.join(SPHINX_DIR, 'build/html')
                    ])
    except CalledProcessError as why:
        print("Coulnd't find path %s as defined in local_settings.py! " %
              SPHINX_DIR, why)
        sys.exit(1)

    move_docs(settings, SPHINX_DIR)

if __name__ == '__main__':
    sys.exit(create_docs())
