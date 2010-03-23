"""A set of functions for generating and parsing JSON for python objects which are decorated by a HydrationMeta class:

	class HydrationMeta:
		attributes = ['id', 'name', 'slug', 'created']
		ref_attributes = ['power_pane', ('site','better_name_for_site')]
		nodes = ['groups', 'peeps', 'notes', 'photos']
		element_name = 'fantastico'
		text_node = 'blue_thing'
"""
from types import *
import simplejson

from django.utils.encoding import smart_unicode
from django.contrib.auth.models import User

meta_name = 'HydrationMeta'
attributes_name = 'attributes' # simple attributes on the element
reference_attributes_name  = 'ref_attributes' # names of members whose ids should be set as attributes or 
reference_by_attributes_name  = 'ref_by_attributes' # tuples of <member name, member attribute> which should be set as an attribute, for example [('site', 'name')]
nodes_name = 'nodes' # members which should be dehydrated and included as children
raw_nodes_name = 'raw_nodes' # members which should are native python types and can be passed directly to the json serializer
text_node_name = 'text_node' # member which should be used as the text node
element_name = 'element_name' # what the element should be named, defaults to __class__.__name__

class HydrationError(Exception): pass

class Hydration:
	"""This is a serializer.  There are many like it.  This one is mine."""

	@classmethod
	def dehydrate(cls, source):
		hydrator = Hydration()
		return hydrator.serialize(hydrator.prep(source))

	@classmethod
	def dehydrate_list(cls, input_list, start=None, end=None):
		"""Return a JSON string with four elements: a start index, an end index, a total length of the list, and a slice of the list"""
		hydrator = Hydration()
		return hydrator.serialize(hydrator.prep_list(input_list, start, end))
	
	@classmethod
	def hydrate(cls, source, data):
		"""This currently only tries to assign the top level attributes to the source"""
		parsed_data = simplejson.loads(data)
		if not parsed_data.has_key('attributes'): return
		for attribute in parsed_data['attributes']:
			setattr(source, attribute, parsed_data['attributes'][attribute])
		return source

	def serialize(self, prepped_data):
		"""Convert the prepped_data to a JSON string"""
		return simplejson.dumps(prepped_data)
		
	def prep_list(self, input_list, start=None, end=None):
		"""Return a serialization-ready map for dehydrate_list"""
		if start == None: start = 0
		if end == None:
			end = len(input_list)
		else:
			end = min(end, len(input_list))
		
		result = {
			'start':start,
			'end':end,
			'total-length':len(input_list),
			'list': [self.prep(source) for source in input_list[start:end]]
		}
		return result

	def prep_value(self, value):
		if isinstance(value, StringType): return smart_unicode(value)
		if isinstance(value, IntType) or isinstance(value, FloatType) or isinstance(value, LongType) or isinstance(value, BooleanType): return value
		
		return smart_unicode(value)

	def get_element_name(self, source):
		if hasattr(source, meta_name): 
			meta = getattr(source, meta_name)
			if hasattr(meta, element_name): return getattr(meta, element_name)
		return smart_unicode(source.__class__.__name__)

	def prep(self, source):
		if isinstance(source, StringType): return source
		if isinstance(source, UnicodeType): return source
		if isinstance(source, IntType): return source
		if isinstance(source, FloatType): return source
		
		element_name = self.get_element_name(source)
		result = {'type': element_name }
		
		if not hasattr(source, meta_name): # no HydrationMeta, so do the best we can
			if isinstance(source, DictType):
				attributes = {}
				for (key, value) in source.items(): attributes[key] = self.prep_value(value)
				result['attributes'] = attributes
			elif isinstance(source, ListType):
				result['value'] = [self.prep_value(val) for val in source]
			else:
				text = self.prep_value(source)
				if len(text.strip()) == 0: return None
				result['value'] = text
			return result
			
		prepped_attributes = {}
		meta = getattr(source, meta_name)
		if hasattr(meta, attributes_name):
			attributes = getattr(meta, attributes_name)
			for attribute in attributes:
				value = getattr(source, attribute)
				if value is None: continue
				if isinstance(value, ListType):
					if len(value) == 0: continue
					value_string = '%s' % value
					prepped_attributes[attribute] = value_string[1:len(value_string) - 1]
				else:
					prepped_value = self.prep_value(value)
					if len(str(prepped_value).strip()) == 0: continue
					prepped_attributes[attribute] = prepped_value

		if hasattr(meta, reference_attributes_name):
			attributes = getattr(meta, reference_attributes_name)
			for attribute in attributes:
				value = getattr(source, attribute)
				if value is None: continue
				if hasattr(value, 'id'):
					pk = getattr(value, 'id')
				elif hasattr(value, 'pk'):
					pk = getattr(value, 'pk')
				else:
					raise HydrationError('reference attribute %s has no id or pk attribute' % value)
				prepped_attributes[attribute] = self.prep_value(pk)

		if hasattr(meta, reference_by_attributes_name):
			attributes = getattr(meta, reference_by_attributes_name)
			for attribute in attributes:
				if not isinstance(attribute, TupleType): raise HydrationError('Reference by attributes name values must be tuples')
				attribute_name = attribute[0]
				attribute_property = attribute[1]
				value = getattr(source, attribute_name)
				if value is None: continue
				if not hasattr(value, attribute_property): raise HydrationError("Reference by attributes name property does not exist: %s - %s" % (attribute, attribute_property))
				prepped_attributes[attribute_name] = self.prep_value(getattr(value,attribute_property))

		if hasattr(meta, raw_nodes_name):
			nodes = getattr(meta, raw_nodes_name)
			for node in nodes:
				data = getattr(source, node)
				result[node] = data

		if hasattr(meta, nodes_name):
			nodes = getattr(meta, nodes_name)
			for node in nodes:
				data = getattr(source, node)
				if data is None: continue
				if hasattr(data, 'all'):
					if data.all().count() == 0: continue
					result[node] = []
					for datum in data.all():
						datum_doc = self.prep(datum)
						if datum_doc: result[node].append(datum_doc)
				elif isinstance(data, ListType):
					if len(data) == 0: continue
					result[node] = []
					for datum in data:
						datum_doc = self.prep(datum)
						if datum_doc: result[node].append(datum_doc)
				elif isinstance(data, DictType):
					if len(data) == 0: continue
					result[node] = {}
					for (key, value) in data.items():
						result[node][key] = self.prep(value)
				elif hasattr(data, meta_name):
					result[node] = self.prep(data)
				else:
					data_string = self.prep_value(data)
					if not data_string or len(data_string.strip()) == 0: continue
					result[node] = data_string
		
		if hasattr(meta, text_node_name):
			name = getattr(meta, text_node_name)
			value = getattr(source, name)
			if value is not None:
				result[name] = value

		if len(prepped_attributes) != 0: result['attributes'] = prepped_attributes
		return result

class UserHydrationMeta:
	"""Sets up hydration for the Django auth User model"""
	attributes = ['id', 'username']
User.HydrationMeta = UserHydrationMeta

from django.db.models.fields.files import ImageFieldFile
class ImageHydrationMeta:
	"""Sets up hydration for Django's image field"""
	element_name = 'image'
	attributes = ['name', 'width', 'height']
ImageFieldFile.HydrationMeta = ImageHydrationMeta

# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
