from setuptools import setup, find_packages
import unittest


def test_suite():
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    return suite


setup(name='B3-Propagation',
      version='0.1.5',
      description='B3 header access and propagation for Python.',
      author='David Carboni',
      author_email='david@carboni.io',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.2',
          'Topic :: System :: Logging',
          'Topic :: Internet :: Log Analysis',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
      ],
      keywords=['logging', 'b3', 'distributed', 'tracing', 'zipkin'],
      url='https://github.com/davidcarboni/B3-Propagation',
      license='MIT',
      packages=find_packages(),
      test_suite='setup.test_suite',
      include_package_data=True,
      zip_safe=True,
      )
