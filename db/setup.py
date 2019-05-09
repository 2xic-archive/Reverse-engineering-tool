from distutils.core import setup, Extension

module = Extension('triforce_db',
					sources = ['db.c'])

setup (name = 'triforce_db',
	   ext_modules = [module])