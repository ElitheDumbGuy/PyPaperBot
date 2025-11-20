import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
  name = 'AcademicArchiver',
  packages = setuptools.find_packages(where="src"),
  package_dir={"": "src"},
  version = '2.0.0',
  license='MIT',
  description = 'AcademicArchiver is a Python tool for downloading scientific papers using Google Scholar, Crossref, and SciHub.',
  long_description=long_description,
  long_description_content_type="text/markdown",
  author = 'Vito Ferrulli', # Maintaining original author credit + contributors
  author_email = 'vitof970@gmail.com',
  url = 'https://github.com/ferru97/AcademicArchiver', # Updated URL
  download_url = 'https://github.com/ferru97/AcademicArchiver/archive/v2.0.0.tar.gz',
  keywords = ['download-papers','google-scholar', 'scihub', 'scholar', 'openalex', 'papers', 'archiver'],
  install_requires=[
        'astroid>=2.4.2',
        'beautifulsoup4>=4.9.1',
        'bibtexparser>=1.2.0',
        'certifi>=2020.6.20',
        'chardet>=3.0.4',
        'colorama>=0.4.3',
        'future>=0.18.2',
        'idna>=2.10,<3',
        'isort>=5.4.2',
        'lazy-object-proxy>=1.4.3',
        'mccabe>=0.6.1',
        'numpy',
        'pandas',
        'pyChainedProxy>=1.1',
        'pylint>=2.6.0',
        'pyparsing>=2.4.7',
        'python-dateutil>=2.8.1',
        'pytz>=2020.1',
        'ratelimit>=2.2.1',
        'requests>=2.24.0',
        'selenium>=4.0.0',
        'six>=1.15.0',
        'soupsieve>=2.0.1',
        'toml>=0.10.1',
        'undetected-chromedriver>=3.5.0',
        'urllib3>=1.25.10',
        'wrapt>=1.12.1',
        'lxml',
        'rapidfuzz'
      ],
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Science/Research',
    'Topic :: Scientific/Engineering',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
  ],
  entry_points={
    'console_scripts': ["AcademicArchiver=core.cli:main"],
  },
)
