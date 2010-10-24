#!/usr/bin/python
from setuptools import setup, find_packages
setup(
	name = "spaciblo",
	version = "0.1.0",
	packages = ['spaciblo.sim'],
	
	install_requires = ['docutils>=0.3'],
	include_package_data = True,
	package_data = {
		'': ['*.txt', '*.rst', '*.html', '*.frag'],
	},
	
	author = "Trevor F. Smith",
	description = "A web service for shared 3D spaces.",
	license = "Apache License 2.0",
	keywords = "3D simulator webgl websockets",
	url = "http://spaciblo.org/"
)
