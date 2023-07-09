import json
from attr_dict import *
from utils import *
import os.path

class Prompt(AttrDict):

	def __init__(self, prompt):
		super().__init__()
		self['prompt'] = prompt

	def astr(self,variables):	
		return self['prompt'].format(**variables)

class Prompts(AttrDict):

	def add(self, name, prompt):
		log(f'Adding new prompt : {name}')
		if isinstance(prompt, Prompt) : self[name] = prompt
		if isinstance(prompt, str) : self[name] = Prompt(prompt)
		else:
			throw('Wrong prompt ....')
		
	def remove(self, name):
		log(f'Removing prompt : {name}')
		if name in self : del self[name]
			
	def names(self) : return self.keys()

	def save(self, file_name):
		with open(file_name + '.json', 'w') as f:
			json.dump(self, f)
			# pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)
		log(f'Saved : {file_name}')

	def load(self, file_name):
		if not os.path.isfile(file_name) :
			err(f'load: File does not exists : {file_name}')
			return
		with open(file_name + '.json', 'rb') as f:
			return Prompts(json.load(f))
			# return pickle.load(f)
		log(f'Load : {file_name}')
