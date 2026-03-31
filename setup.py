from setuptools import setup, find_packages

from boremapper import const

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()
    
setup(
    name=const.APP_NAME,
    version=const.APP_VERSION,
    description=const.APP_DESCRIPTION,
    long_description=readme,
    author=const.APP_AUTHOR,
    author_email=const.APP_AUTHOR_EMAIL,
    url=const.APP_REPO_URL,
    license=license,
    packages=find_packages(exclude=('tests', 'docs', 'data'))
)
