#!/usr/bin/env python
# encoding: utf-8

import os
import sys

from setuptools import setup, find_packages


if sys.version_info < (2, 6):
    raise SystemExit("Python 2.6 or later is required.")

exec(open(os.path.join("marrow", "monitor", "collector", "release.py")))



setup(
        name = "marrow.monitor.collector",
        version = release,
        
        description = "A rich, efficient method of gathering server statistics.",
        long_description = """\
For full documentation, see the README.textile file present in the package,
or view it online on the GitHub project page:

https://github.com/marrow/marrow.monitor.collector""",
        
        author = "Alice Bevan-McGregor",
        author_email = "alice+marrow@gothcandy.com",
        url = "https://github.com/marrow/marrow.monitor.collector",
        license = "MIT",
        
        install_requires = [
            'marrow.util < 2.0',
            'MongoEngine',
            'marrow.script'
        ],
        
        test_suite = 'nose.collector',
        tests_require = [
            'nose',
            'coverage'
        ],
        
        classifiers = [
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2.6",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.1",
            "Programming Language :: Python :: 3.2",
            "Topic :: Software Development :: Libraries :: Python Modules",
        ],
        
        packages = find_packages(exclude=['examples', 'tests']),
        zip_safe = True,
        include_package_data = True,
        package_data = {'': ['README.textile', 'LICENSE']},
        
        namespace_packages = ['marrow', 'marrow.monitor', 'marrow.monitor.collector', 'marrow.monitor.collector.ext'],
        
        entry_points = {
                'collector': [
                        'load = marrow.monitor.collector.ext.load:LoadExtension',
                    ],
                
                'collector.load': [
                        'default = marrow.monitor.collector.ext.load:generic_backend',
                        'generic = marrow.monitor.collector.ext.load:generic_backend',
                        'linux = marrow.monitor.collector.ext.load:linux_backend',
                        'posix = marrow.monitor.collector.ext.load:posix_backend'
                    ],
                
                'collector.cpu': [
                        'default = marrow.monitor.collector.ext.cpu:mpstat_backend',
                        'mpstat = marrow.monitor.collector.ext.cpu:mpstat_backend'
                    ]
            }
    )
