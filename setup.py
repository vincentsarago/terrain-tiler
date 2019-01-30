
from setuptools import setup, find_packages

with open('tiler/__init__.py') as f:
    for line in f:
        if line.find("__version__") >= 0:
            version = line.split("=")[1].strip()
            version = version.strip('"')
            version = version.strip("'")
            continue

# Runtime requirements.
inst_reqs = [
    "rio-tiler==1.0rc2",
    "lambda-proxy~=2.0",
    "rio_rgbify",
]

extra_reqs = {}


setup(name='tiler',
      version=version,
      description=u"""""",
      long_description=u"",
      python_requires='>=3',
      classifiers=[
          'Programming Language :: Python :: 3.6'
      ],
      keywords='',
      author=u"Vincent Sarago",
      author_email='vincent@developmentseed.org',
      url='https://github.com/developmentseed/terrain-tiler',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=inst_reqs,
      extras_require=extra_reqs)
