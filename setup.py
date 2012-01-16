from setuptools import setup, find_packages

version = '1.0'

long_description = (
    open('README.rst').read()
    + '\n' +
    open('CHANGES.rst').read()
    + '\n')

setup(
    name='collective.bpzope',
    version=version,
    description="Zope and Plone utils for the bpython interpreter",
    long_description=long_description,
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
      "Programming Language :: Python",
      ],
    keywords='plone zope bpython interpreter',
    author='Six Feet Up, Inc.',
    author_email='info@sixfeetup.com',
    url='http://github.com/collective/collective.bpzope',
    license='D-FSL',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['collective'],
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'setuptools',
        'bpython',
    ],
    # This is just here to install the script via buildout
    entry_points={'console_scripts': ['bpzope = bpython.cli:main']},
    )
