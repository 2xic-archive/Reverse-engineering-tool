from distutils.core import setup, Extension

module = Extension('triforce_extender',
					sources = ['extender.c'])

setup (name = 'triforce_extender',
	   ext_modules = [module])