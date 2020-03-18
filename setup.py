from setuptools import setup, find_packages

setup(
    name='model_converter',
    version='1.3',
    packages=find_packages(),
    install_requires=["parglare==0.10.0", "typhoon-hil-api"],
    url='https://www.typhoon-hil.com/',
    include_package_data=True,
    license='MIT',
    author='Aleksa Domic',
    author_email='aleksaREPLACEWITHDOTdomicREPLACEWITHAT'
                 'typhoon-hilREPLACEWITHDOTcom',
    description='Typhoon HIL Model Converter'
)
