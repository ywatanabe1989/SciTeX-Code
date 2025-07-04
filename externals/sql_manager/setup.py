import os
import json
import codecs
from pathlib import Path
from setuptools import setup, find_packages


BASE_DIR = Path(__file__).resolve().parent
version_info = json.loads(BASE_DIR.joinpath('sql_manager', 'version', 'version.json').read_text())


setup(
    name=version_info['prog'],
    version=version_info['version'],
    author=version_info['author'],
    author_email=version_info['author_email'],
    description=version_info['desc'],
    long_description=BASE_DIR.joinpath('README.md').read_text(),
    long_description_content_type="text/markdown",
    url='https://github.com/suqingdong/sql_manager',
    project_urls={
        'Documentation': 'https://sql_manager.readthedocs.io',
        'Tracker': 'https://github.com/suqingdong/sql_manager/issues',
    },
    license='BSD License',
    install_requires=BASE_DIR.joinpath('requirements.txt').read_text().strip().split('\n'),
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries'
    ]
)
