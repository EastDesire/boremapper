from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()
    
setup(
    name='BoreMapper',
    version='0.1.0',
    description='A tool for mapping the bore profile of woodwind instruments with a split bore',
    long_description=readme,
    author='Jan Odvárko',
    author_email='jan@odvarko.cz',
    url='https://github.com/EastDesire/boremapper',
    license=license,
    packages=find_packages(exclude=('tests', 'docs', 'data'))
)
