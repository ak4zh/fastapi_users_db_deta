#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', ]

test_requirements = [ ]

setup(
    author="Akash Agarwal",
    author_email='agwl.akash@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Sub-package for Deta Base support in FastAPI Users.",
    entry_points={
        'console_scripts': [
            'fastapi_users_db_deta=fastapi_users_db_deta.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='fastapi_users_db_deta',
    name='fastapi_users_db_deta',
    packages=find_packages(include=['fastapi_users_db_deta', 'fastapi_users_db_deta.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/ak4zh/fastapi_users_db_deta',
    version='0.2.2',
    zip_safe=False,
)
