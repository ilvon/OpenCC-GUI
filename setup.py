from setuptools import setup, find_packages

VERSION = '1.1.3a'
with open('README.md', 'r', encoding='utf-8') as f:
    LONG_DESC = f.read()

setup(
    name='OpenCC-GUI',
    version=VERSION,  
    author='iivon',
    packages=find_packages(),
    install_requires=[
        'chardet>=5.2.0',
        'CTkMessagebox>=2.5',
        'customtkinter>=5.2.2',
        'OpenCC>=1.1.7',
    ],
    description='A simple GUI for OpenCC',
    long_description=LONG_DESC,
    long_description_content_type='text/markdown',
    url='https://github.com/ilvon/OpenCC-GUI',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',
        'Operating System :: MacOS :: MacOS X',
    ],
    python_requires='>=3.10',
    entry_points={
        'console_scripts': [
            'OpenCC-GUI = src.OpenCC_gui:openCCgui'
        ]
    },
    package_data={
        'src': ['assets/favicon.ico', 'assets/right_arrow.png'],
    },
)