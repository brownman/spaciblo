import traceback
from types import *
import simplejson

from django.conf.urls.defaults import *
from django.http import HttpRequest
from django.db.models.query import QuerySet

from piston.utils import rc
from piston.handler import BaseHandler
from piston.resource import Resource
from piston.emitters import JSONEmitter
from piston.handler import typemapper, HandlerMetaClass

def to_json(data):
	"""Returns a string JSON representation using the same mechanism as the Piston based APIs"""
	handler = get_handler(type(data), False)
	if not handler:
		handler = PlainObjectHandler()
		data = PlainObjectHandler().flatten(data)
	emitter = JSONEmitter(data, typemapper, handler, anonymous=False)
	request = HttpRequest()
	request.method = 'GET'
	return emitter.render(request)

def from_json(obj, json_data):
	"""Takes all of the top level attributes from the json and tries to set them as attributes on the obj"""
	parsed_data = simplejson.loads(json_data)
	for key, val in parsed_data.items(): setattr(obj, key, val)
	return obj

def get_handler(model, anonymous):
	"""Find the Piston handler for a given model"""
	for klass, (km, is_anon) in typemapper.iteritems():
		if model is km and is_anon is anonymous: return klass

class PlainObjectHandler(object):
	"""
	A base class which provides Piston handling for non-model objects
	"""
	__metaclass__ = HandlerMetaClass

	allowed_methods = ('GET',) # 'POST', 'PUT', 'DELETE'
	anonymous = is_anonymous = False
	exclude = None
	fields =  None

	def exists(self, **kwargs): return hasattr(kwargs['obj'])

	def read(self, request, *args, **kwargs):
		return self.flatten(kwargs['obj'])
		#return rc.NOT_FOUND
		#return rc.BAD_REQUEST
		#return rc.NOT_IMPLEMENTED

	def create(self, request, *args, **kwargs):
		#return rc.DUPLICATE_ENTRY
		return rc.NOT_IMPLEMENTED

	def update(self, request, *args, **kwargs): return rc.NOT_IMPLEMENTED

	def delete(self, request, *args, **kwargs): raise NotImplementedError
	
	def flatten(self, obj):
		if isinstance(obj, NoneType): return obj
		if isinstance(obj, StringType): return obj
		if isinstance(obj, UnicodeType): return obj
		if isinstance(obj, BooleanType): return obj
		if isinstance(obj, IntType): return obj
		if isinstance(obj, FloatType): return obj
		if isinstance(obj, QuerySet):
			temp_array = []
			temp_array.extend(obj)
			return self.flatten(temp_array)
			
		if type(obj) == ListType or type(obj) == TupleType:
			return [self.flatten(item) for item in obj]
		elif type(obj) == DictType:
			result = {}
			for key in obj.keys(): result[key] = self.flatten(obj[key])
			return result
			
		if not hasattr(obj, '__dict__'): return str(obj)

		results = {}
		handler = get_handler(type(obj), False)
		for f in obj.__dict__:
			if handler and handler.fields and not len(handler.fields) == 0:
				if not f in handler.fields: continue
			if handler and handler.exclude and not len(handler.exclude) == 0:
				if f in handler.exclude: continue
			results[f] = self.flatten(getattr(obj, f))
		return results 

def all_attributes(cls):
	"""Returns a list of keys for attributes of obj, even if they are on base classes"""
	keys = [f for f in obj.__dict__]
