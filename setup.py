from setuptools import setup
setup(name='typecat',
      version='0.01',
      description='Sort, categorize, and find the right font',
      url='http://github.com/LordPharaoh/typecat',
      author='Varun Iyer and Timothy Kanarsky',
      author_email='vi.mail@protonmail.ch',
      license='MIT',
      packages=['typecat', 'typecat.display'],
      install_requires=['pillow', 'numpy'],
      keywords='font typography sort categorize search',
      include_package_data=True,
      zip_safe=False)
