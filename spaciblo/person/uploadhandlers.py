from django.core.files.uploadhandler import FileUploadHandler, StopUpload
class QuotaUploadHandler(FileUploadHandler):
	""" This upload handler terminates the connection if more than a quota is uploaded. """
	QUOTA = 1 * 2**20 # 1 MB

	def __init__(self, request=None):
		super(QuotaUploadHandler, self).__init__(request)
		self.total_upload = 0

	def receive_data_chunk(self, raw_data, start):
		self.total_upload += len(raw_data)
		if self.total_upload >= self.QUOTA:
			raise StopUpload(connection_reset=True)
		return raw_data

	def file_complete(self, file_size):
		return None

# Copyright 2010 Trevor F. Smith (http://trevor.smith.name/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
