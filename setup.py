#!/usr/bin/python
from setuptools import setup, find_packages
setup(
	name = "Spaciblo",
	version = "0.1a1",
	packages = find_packages(),
	
	install_requires = ['docutils>=0.3'],
	include_package_data = True,
	package_data = {
		'': ['*.txt', '*.rst', '*.html', '*.frag'],
	},
	
	author = "Trevor F. Smith",
	description = "A web service for shared 3D spaces.",
	license = "Apache License 2.0",
	keywords = "3D simulator webgl",
	url = "http://spaciblo.org/"
)