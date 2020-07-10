#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup psycodebook installation."""
from setuptools import setup

if __name__ == '__main__':
    import versioneer
    from codebook.__about__ import __version__, DOWNLOAD_URL

    cmdclass = versioneer.get_cmdclass()

    setup(
        name='pycodebook',
        version=__version__,
        cmdclass=cmdclass,
        download_url=DOWNLOAD_URL
    )
