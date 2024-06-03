from setuptools import setup, find_packages

setup(
    name='SerialDBPy',
    version='0.1.4.8',
    author='G',
    author_email='serialdbpy@swimhdr.com',
    description='Lightweight Python ORM for basic CRUD operations.',
    license='MIT',
    url = 'https://github.com/publicsignal',
    download_url='https://github.com/publicsignal/SerialDBPy/tree/main/dist/SerialDBPy-0.1.4.8.tar.gz',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)