import os
import glob
from attr_dict import AttrDict
import tomlkit
import shutil
from utils import *

PROFILES_DIR = 'profiles'
CFG_FILE = 'profile.toml'

class Profile(AttrDict): 

	def __init__(self, root_dir): 
		super().__init__()
		self['root_dir'] = root_dir

	def load(self):
		slash = '' if self.root_dir.endswith('/') else '/'
		file = f'{self.root_dir}{slash}{CFG_FILE}'
		log(f'Loading profile : {file}')
		with open(file, 'r') as f :
			txt = f.read()
			self.update(tomlkit.parse(txt))

	#pick : return shortcut/alias
	def db_alias(self, db_name): return self['dbs'][db_name]
	def model_alias(self, model_name): return self['models'][model_name]

	def db_list(self): return list(self['dbs'].keys())
	def model_list(self): return list(self['models'].keys())

	def abs_path(self, rel_path):
		slash = '' if self.root_dir.endswith('/') else '/'
		return f"{self.root_dir}{slash}{rel_path}"

	def db_path(self, db_name) : 
		if db_name not in self.dbs : #default if missing
			return self.abs_path(f'dbs/{db_name}')
		else :	
			return self.abs_path(self.dbs[db_name]['path'])

	def ingest_path(self, db_name) : 
		if db_name not in self.ingest : #default if missing
			return self.abs_path(f'src/{db_name}')
		else :	
			return self.abs_path(self.ingest[db_name]['path'])

	def db_exists(self, db_name: str) -> bool:
		"""
		Checks if vectorstore exists
		"""
		db_path = self.db_path(db_name)
		print('ex:  ',db_path)
		if os.path.exists(os.path.join(db_path, 'index')):
			if os.path.exists(os.path.join(db_path, 'chroma-collections.parquet')) and os.path.exists(os.path.join(db_path, 'chroma-embeddings.parquet')):
				list_index_files = glob.glob(os.path.join(db_path, 'index/*.bin'))
				list_index_files += glob.glob(os.path.join(db_path, 'index/*.pkl'))
				# At least 3 documents are needed in a working vectorstore
				if len(list_index_files) > 3 : return True
		return False

	def create(self, profile, root='./'):
		pdir = f"{self.ps_root(root)}/{profile}"
		src = f"{pdir}/src"
		print(f'Creating docs source dir : {src}')
		os.makedirs(src, exist_ok=True)
		dbs_main = f"{pdir}/dbs/main"
		print(f'Creating main db dir : {dbs_main}')
		os.makedirs(dbs_main, exist_ok=True)
		print('Copying profile template ...')
		shutil.copyfile(f'{self.ps_root(root)}/profile.template', f'{pdir}/{CFG_FILE}')

		

class Profiles(AttrDict):

	def __init__(self, root_dir): 
		super().__init__()
		self['root_dir'] = root_dir

	def profile_alias(self, profile): return self[profile]

	def load_profile(self, profile):
		slash = '' if self.root_dir.endswith('/') else '/'
		self[profile] = Profile(f'{self.root_dir}{slash}{profile}')
		# self[profile].set_root(f'{self.root_dir}{slash}{profile}')
		self[profile].load()



