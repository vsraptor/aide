## What is this ?

This in general is a Shell around Large Language Model (LLM), at least for now.
It is based on [privateGPT](https://github.com/imartinez/privateGPT) code, which I refactored, componetized and enchanced with additional features.

In short this tool allows you to interact with different document-sets OR simply query a LLM.

**Everything runs locally.**

### Features

	1. Profile support
		- multiple docs stores and ability to switch between them on the fly.
		- multiple models and ability to switch between them on the fly.
	2. Non-question Commands support to do usefull things
	3. System prompts support
	4. Better CLI interface
	5. Direct and QA query modes.
	6. Keeps .history of the commands
	7. Keeps .chat_history
 	8. Multiline support (use Alt+Enter to commit a question)



### Supported LLMs

It should support all the models that work on privateGPT (type: LlamaCpp and GPT4All).

Here are some I used from huggingface :

	$ ls ./models
	TheBloke_OpenAssistant-SFT-7-Llama-30B-GGML
	TheBloke_WizardLM-13B-Uncensored-GGML
	TheBloke_WizardLM-7B-GGML
	TheBloke_Guanaco-65-GGML
	TheBloke_orca_mini_7B-GGML
	TheBloke_WizardLM-30B-Uncensored-GGML
	TheBloke_WizardLM-7B-Landmark

### Profiles

The idea of profiles is to keep multiple configurations and be able to switch between them.
Every profile can have many document stores. This allows you to separate them thematicaly f.e. one docs store for **economics** another for **history** ...etc

For now you have to create manually the directory structure and configuration if you want to use other profile than 'main'.

Here is the directory structure for the 'main' profile:

	tree -d ./profiles -L 3
	
	./profiles
	└── main
	    ├── dbs
	    │    ├── main
	    │    └── test
	    └── src
	        ├── main
	        └── test

.. and the config file should be in the profile base directory :

	profiles/main/profile.toml

The cfg is using **.toml** format.
https://toml.io/en/

### Installation

	git clone git@github.com:vsraptor/aide.git
	cd aide
	pip install -r requirments.txt

### Running

0. Create 'models' directory or symlink to the directory where you host your LLM's
1. Download a model in the ./models directory. (make a subdir for the specific model)
   
	F.e. from here : https://huggingface.co/TheBloke/WizardLM-7B-GGML/tree/main

3. Configure the model in **profiles/main/profile.toml**

	Example (you can use any argument supported by Langchain LlamaCpp : https://github.com/mmagnesium/langchain/blob/master/langchain/llms/llamacpp.py):

		........
		[models.main]
			type='LlamaCpp'
			target_source_chunks=4
			embeddings_model='all-MiniLM-L6-v2'
			
			model_path='./models/TheBloke_WizardLM-7B-GGML/wizardLM-7B.ggmlv3.q4_1.bin'
			n_ctx=1000
			n_batch=16
			max_tokens=512


4. Then copy the source docs (.txt, .pdf ...) to the corresponding 'src'-sub-directory (look above dir structure)

5. Next ingest them. This will create/update the relevant vector-db under 'dbs' dir

		python3 ingest_docs.py --profile main --db main

6. Run the shell

		python3 run_aide.py --profile main --db main


-----

	$ python3 ingest_docs.py --help
	usage: ingest_docs.py [-h] [--profile PROFILE] [--db DB]
	
	AIDE: Ask questions to your documents without an internet connection, using the power of LLMs.
	
	options:
	  -h, --help            show this help message and exit
	  --profile PROFILE, -p PROFILE
	                        Select profile.
	  --db DB, -d DB        Select db.


	
	$ python3 run_aide.py --help
	usage: run_aide.py [-h] [--mute-stream] [--multiline MULTILINE] [--profile PROFILE] [--model MODEL] [--db DB]
	
	AIDE: Ask questions to your documents without an internet connection, using the power of LLMs.
	
	options:
	  -h, --help            show this help message and exit
	  --mute-stream, -M     Use this flag to disable the streaming StdOut callback for LLMs.
	  --multiline MULTILINE, -l MULTILINE
	                        Use multiline mode. Alt-Enter commits the question. Default: false
	  --profile PROFILE, -p PROFILE
	                        Select profile. Default: main
	  --model MODEL, -m MODEL
	                        Select model. Default: main
	  --db DB, -d DB        Select db. Default: main

-----

### Interact

Check the available commands with !help

	aide: !help
	
	quit - exit the session					
	!mode <qa|direct> - switch the mode of quering. 'qa' uses the docs DB to answer the question. 'direct' asks the model directly.
	? <question> - ask the question using the opposite mode					
	!result - print the result structure of the last query
	!docs <number> - return the nth text snippet used as a context to answer the query
	!source <number> - source file of the nth document of the result
	!time - how long it took to generate an answer
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
				
-----

#### Example of a simple chat

	$ python3 run_aide.py --profile main --db main
	Loading profile : .//profiles/main/profile.toml
	Profile: main
	Model: main
	DB: main
	Using embedded DuckDB with persistence: data will be stored in: .//profiles/main/dbs/main
	{'model_path': './models/TheBloke_WizardLM-7B-GGML/wizardLM-7B.ggmlv3.q4_1.bin', 'n_ctx': 1000, 'n_batch': 16, 'n_gpu_layers': 20, 'max_tokens': 512}
	llama.cpp: loading model from ./models/TheBloke_WizardLM-7B-GGML/wizardLM-7B.ggmlv3.q4_1.bin
	................	
	
	aide: who are the spartans ?
	Llama.generate: prefix-match hit
	 The Spartans were a group of people from ancient Greece who were known for their military prowess and strict way of life. They lived in the city of Sparta and were considered one of the most powerful city-states in Greece during the 5th century BCE.
	aide: !time
	41.41 
	aide: !docs 1
	city of busy trade. Sparta was an armed camp where people were soldiers
	for the sake of being soldiers. The people of Athens loved to sit in the
	sun and discuss poetry or listen to the wise words of a philosopher.
	The Spartans, on the other hand, never wrote a single line that was
	considered literature, but they knew how to fight, they liked to fight,
	and they sacrificed all human emotions to their ideal of military
	preparedness.
	aide: !source 1
	./profiles/main/src/main/story-of-mankind.txt
	aide: !mode direct
	aide: who are the spartans ?
	
	The Spartans were a group of ancient Greeks who lived in the city-state of Sparta, located in the southern part of the country. They were known for their toughness and discipline, as well as their rigorous military training and lifestyle. The Spartans played a key role in defending Greece against invading Persian forces in the 5th century BCE, and they were also famous for their political system, which was based on a strict hierarchy of rulers and warriors. Today, the term "Spartan" is often used as a metaphor for strength, discipline, and toughness.
	aide: !time
	19.11

#### Using multiple sources/dbs

	$ python3 ingest_docs.py --profile main --db test
	Loading profile : ./profiles/main/profile.toml
	Profile: main
	Model: main
	DB: test
	Creating new vectorstore
	Loading documents from ./profiles/main/src/test
	Loading new documents: 100%|██████████████████████| 4/4 [00:00<00:00, 21.34it/s]
	Loaded 4 new documents from ./profiles/main/src/test
	Split into 6326 chunks of text (max. 500 tokens each)
	Creating embeddings. May take some minutes... ./profiles/main/dbs/test
	Using embedded DuckDB with persistence: data will be stored in: ./profiles/main/dbs/test
	Ingestion complete! You can now query your documents
	
	
	$ python3 run_aide.py --profile main --db main
	Loading profile : .//profiles/main/profile.toml
	Profile: main
	Model: main
	DB: main
	................

 	# switch to qa mode
	aide: !mode qa
	aide: what is law ?
	 Law refers to the set of rules and regulations established by the government and enforced by the legal system to govern the behavior of citizens and maintain order in society.
	aide: !docs 1
	The penal statutes form a very small proportion of the sixty-two books of the Code and Pandects; and in all judicial proceedings, the life or death of a citizen is determined with less caution or delay than the most ordinary question of covenant or inheritance. This singular distinction, though something may be allowed for the urgent necessity of defending the peace of society, is derived from the nature of criminal and civil jurisprudence. Our duties to the state are simple and uniform: the
	aide: !source 1
	./profiles/main/src/main/hist-rome.txt

 	#switch the db to test
	aide: !switch db test
	Switching to DB : test
	Using embedded DuckDB with persistence: data will be stored in: .//profiles/main/dbs/test
	
	aide: what is law ?
	 Law is the collective organization of the individual right to lawful defense.
	aide: !docs 1
	What is law? What ought it to be? What is its domain? What are its limits? Where, in fact, does the prerogative of the legislator stop?
	
	I have no hesitation in answering, Law is common force organized to prevent injustice;--in short, Law is Justice.
	
	It is not true that the legislator has absolute power over our persons and property, since they pre-exist, and his work is only to secure them from injury.
	aide: !source 1
	./profiles/main/src/test/bastiat-the-law.txt
	
	#ask in direct mode ... ? toggles the mode
	aide: ?what is law ?
	
	Law is a set of rules and regulations that are established by the government or other authoritative bodies to govern the behavior of individuals and organizations within a particular society. These laws are designed to promote order, justice, and fairness in society, and to protect citizens from harm. Law can be written or unwritten, and can cover a wide range of topics such as contract law, criminal law, tort law, property law, and environmental law


#### Using System prompt

For now very rudimentary ... probably will extend this functionality.

Use {body} to specify where you want to insert your question.

	aide: !prompt new task You have the following objective "{body}". Create a list of step by step actions to accomplish the goal.
	Adding new prompt : task
	aide: !prompt list
	{'task': {'prompt': 'You have the following objective "{body}". Create a list of step by step actions to accomplish the goal.'}}
 
	aide: > task How can I sum two numbers ?
	Q: You have the following objective "How can I sum two numbers ?". Create a list of step by step actions to accomplish the goal.
	
	
	1. Check if the user has entered the correct syntax for adding two numbers. 
	2. Prompt the user to enter the first number they want to add. 
	3. Prompt the user to enter the second number they want to add. 
	4. Add the two numbers and display the result to the user. 
	5. Check if the user wants to enter another number or not. If yes, repeat steps 2-4 until no more numbers are entered. 
	6. If the user does not want to enter another number, thank them for using the program and exit.
