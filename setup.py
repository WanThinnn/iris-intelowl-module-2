from setuptools import setup

setup(
    name='iris-intelowl-module-2',
    python_requires='>=3.8',
    version='0.1.2',
    packages=['iris_intelowl_module_2', 'iris_intelowl_module_2.intelowl_handler'],
    url='https://github.com/dfir-iris/iris-intelowl-module',
    license='Apache Software License 3.0',
    author='dfir-iris',
    author_email='contact@dfir-iris.org',
    description='`iris-intelowl-module` is a IRIS processor module providing open-source threat intelligence leveraging IntelOlw analyzers, to enrich indicators of compromise',
    install_requires=['pyintelowl>=4.4.0']
)
