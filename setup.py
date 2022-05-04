try:
    from setuptools import setup
    from setuptools import Extension
except ImportError:
    from distutils.core import setup
    from distutils.extension import Extension

from Cython.Distutils import build_ext

ext_modules = [Extension("Autobet", ["Autobet.pyx"]), Extension(
    "bet365_browser", ["bet365_browser.pyx"])]

setup(
    name='Generic model class',
    cmdclass={'build_ext': build_ext},
    ext_modules=ext_modules)
