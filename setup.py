from distutils.core import setup

setup(
    name='Netscrape',
    version='1.0',
    packages=['netscrape', 'netscrape.navigators'],
    url='',
    license='MIT',
    author='nick petosa',
    author_email='nick.petosa@gmail.com',
    description='Automated, scheduled, intelligent web scraping server and client.',
    install_requires=['pytest==3.0.6']
)
