import re

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.formatted_text import HTML

import argparse
from aide import *
from utils import *
from prompts import *


class History:

	def __init__(self, file_name):
		self.file_name = file_name
		self.file = open(file_name,'a')

	def log(self, text):
		self.file.write(text)	

	def close(self):
		self.file.close()	


class Shell:

	def __init__(self):
		self.args = self.parse_arguments()

		self.mode = 'direct'
		self.res = None
		self.prompts = Prompts()
		self.shell_history = FileHistory(".history")
		self.chat_history = History('.chat_history')

		self.session = PromptSession(history=self.shell_history)
		self.aide = AIDE(self.args.profile, self.args.model, self.args.db, self.args.mute_stream)


	def parse_arguments(self):
		parser = argparse.ArgumentParser(description='AIDE: Ask questions to your documents without an internet connection, using the power of LLMs.')
		parser.add_argument("--mute-stream", "-M", action='store_true', help='Use this flag to disable the streaming StdOut callback for LLMs.')
		parser.add_argument("--multiline", "-l", default=False, type=bool, help='Use multiline mode. Alt-Enter commits the question. Default: false')
		parser.add_argument("--profile", "-p", default='main', help='Select profile. Default: main')
		parser.add_argument("--model", "-m", default='main', help='Select model.  Default: main')
		parser.add_argument("--db", "-d", default='main', help='Select db.  Default: main')

		args = parser.parse_args()
		if 'help' in args :
			parser.print_help()
			exit()

		return args



	def parse_cmd(self, text):
		els = re.split('\s+',text)
		if len(els) > 1 :
			cmd, opts = els[0], els[1:]
		else :
			cmd, opts = els[0], []
		return cmd, opts


	def cmd(self, text):
		cmd, opts = self.parse_cmd(text)
		# print(f'cmd:{cmd}, opts:{opts}')
		sub_cmd = opts[0] if len(opts) > 0 else None

		match cmd :
			case 'result' : say(self.res)
			case 'docs' :
				if self.res is not None and 'source_documents' in self.res :
					ix = 1
					if len(opts) > 0 : ix = int(opts[0]) 
					say(self.res['source_documents'][ix-1].page_content)
			case 'source' :
				if self.res is not None and 'source_documents' in self.res :
					ix = 1
					if len(opts) > 0 : ix = int(opts[0]) 
					say(self.res['source_documents'][ix-1].metadata["source"])

			case 'db' : 
				match sub_cmd :
					case 'list' : say(self.aide.p.db_list())
			case 'model' : 
				match sub_cmd :
					case 'list' : say(self.aide.p.model_list())
			case 'show' :
				match sub_cmd: 
					case 'profile' : say(self.aide.p)
					case 'model' : say(self.aide.m)
					case 'db' : say(self.aide.p['dbs'][self.aide.db_name])
			case 'time' :
				if 'time' in self.res : say(self.res['time'])
			case 'mode' :
				if len(opts) == 0 : say(self.mode)
				else : self.mode = opts[0]
			case 'switch' :
				match sub_cmd :
					case 'db' :
						if len(opts) > 1 : self.aide.switch_db(opts[1])
				match sub_cmd :
					case 'model' :
						if len(opts) > 1 : self.aide.switch_model(opts[1])

			case 'prompt' :
				match sub_cmd :
					case 'list' : say(self.prompts)
					case 'show' : 
						if opts[1] in self.prompts : say(self.prompts[opts[1]])
					case 'names' : say(self.prompts.names())
					case 'new' :
						self.prompts.add(name=opts[1], prompt=' '.join(opts[2:]))
					case 'del' :
						self.prompts.remove(file_name=opts[1])
					case 'save' :
						self.prompts.save(file_name=opts[1])
					case 'load' :
						pts = self.prompts.load(name=opts[1])
						if pts is not None : self.prompts = pts


			case 'help' :
				say('''
quit - exit the session					
!mode <qa|direct> - switch the mode of quering. 'qa' uses the docs DB to answer the question. 'direct' asks the model directly.
? <question> - ask the question using the opposite mode					
!result - print the result structure of the last query
!docs <number> - return the nth text snippet used as a context to answer the query
!source <number> - source file of the nth document of the result
!time - how long it took to generate answer
!db list - list the profile DB's
!model list - list all models in the profile
!show - show the configuration of ... 
	profile <name>
	model <name>
	db <name>
!switch
	db <name> - switch the database for QA mode
	model <name> - switch the Model
> <name> <question> - Insert the question inside the prompt in the place of {body} variable and ask the question.
!prompt
	list - list all template prompts
	names - list the names all template prompts
	show <name>	- show a prompt template by specified name
	del <name>	- delete a prompt template by specified name
	save <file-name> - save the prompts to a file
	load <file-name> - load the prompts from a file	
				''')	

	def quit(self): pass
	
	def bottom_toolbar(self):
		return HTML(f'profile: <b><style bg="ansired">{self.aide.profile_name}</style></b> | model: <b>{self.aide.model_name}</b> | db: <b>{self.aide.db_name}</b> | mode: <b>{self.mode}</b>| multi: <b>{self.args.multiline}</b>')


	def step(self, text):
		xmode = self.mode
		question = text
		if text[0] == '?' : 
			xmode = 'direct' if self.mode == 'qa' else 'qa'
			question = text[1:]

		self.res = self.aide.step(question, mode=xmode)
		print()
		if self.args.mute_stream : print(self.res['result'])
		self.chat_history.log(f"Q: {question}\nA: {self.res['result']}\n")


	def run(self):
		
		while True:
		
			text = self.session.prompt("aide: ", auto_suggest=AutoSuggestFromHistory(), bottom_toolbar=self.bottom_toolbar, multiline=self.args.multiline)

			if text == 'quit' :
				self.quit()
				self.chat_history.close()
				break
			elif len(text) < 2: pass
			elif text[0] == '>' : 
				name, parsed = self.parse_cmd(re.sub('\s*>\s*', '', text))
				if name not in self.prompts :
					err(f'Prompt <{name}> does not exists !')
					continue
				question = ' '.join(parsed)
				q = self.prompts[name].astr({'body':question})
				log(f'Q: {q}')
				self.step(q)
			elif text[0] == '!' : 
				self.cmd(text[1:])
			else:
				self.step(text)



