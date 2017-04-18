from bs4 import BeautifulSoup
import re
import requests
import time
import json
import copy

def match(regex, text):
	# Lower down in this code I recommend you compile your regex
	s = re.search("("+regex+")", text)
	if s:
		if s.group(1):
			return True
		else:
			return False
	else:
		return False
class Pokemon():
	def __init__(self):
		self.name = "BLANK"
		self.id = -1
		self.imgSrc = "BLANK"
		self.generations = []
		self.types = []
		self.stats = {}
		self.evolutions = []
	# Really quickly: when you write Python you should snake_case except
	# when you're defining classes. Variables and functions should be snaked
	# JS is a camel case language, python is snake case.
	def getDictRep(self):
		d = {}
		d['name'] = self.name
		d['id'] = self.id
		d['imgSrc'] = self.imgSrc
		d['generations'] = self.generations
		d['types'] = self.types
		d['stats'] = self.stats
		d['evolutions'] = self.evolutions
		return d
	def loadFromDict(self, d):
		self.name = d['name']
		self.id = d['id']
		self.imgSrc = d['imgSrc']
		self.generations = d['generations']
		self.types = d['types']
		self.stats = d['stats']
		self.evolutions = d['evolutions']
	def __str__(self):
		return json.dumps(self.getDictRep(), indent=4, separators=(',', ': '))
class PkmDatabase():
	def __init__(self):
		# the pokemon objects indexed by their id
		self.pokemon = {}
		# mapping the pokemon names to their id
		self.pokemonNames = {}
		self.debug = False
		self.generation = -1
	def debugPrint(self, p, s):
		if self.debug:
			print("["+str(p)+"] "+str(s))
			# Try print("[{}] {}".format(p,s)) instead
			# or even "[%s] %s" % (p,s) as string concat is slow and
			# difficult to read
	def raiseError(self, s):
		raise Exception(s)
	def addPokemon(self, pkm):
		# This is interesting. You can do this but generally people in
		# Python don't because it supports duck typing; https://en.wikipedia.org/wiki/Duck_typing
		# If you really want stricter typing in your code, you can use type annotations which are available in Python 3.5ish
		if not isinstance(pkm, Pokemon):
			self.raiseError("Object supplied of invalid type: "+type(pkm))
		try:
			self.pokemon[pkm.id].append(pkm)
		except:
			self.pokemon[pkm.id]=[pkm]
		# To be honest I wouldn't bother storing a separate index of name => id
		# because there aren't enough pikmin to warrant it (and as below, you need to maintain that state of the index)
		# but neat idea.
		self.pokemonNames[pkm.name] = pkm.id
	def removePokemon(self, **kwargs):
		# You picked up kwargs!! v nice!
		if 'id' in kwargs:
			pkmId = kwargs['id']
			pkm = self.pokemon[pkmId]
			# Since you don't actually need the popped value,
			# and you never break out of this for loop
			# you could probably just remove the item rather than
			# pop it.
			for p in pkm:
				self.pokemonNames.pop(p.name)
			self.pokemon.pop(pkmId)
		elif 'name' in kwargs:
			# This one makes more sense
			pkmName = kwargs['name']
			pkmId = self.pokemonNames[pkmName]
			self.pokemonNames.pop(pkmName)
			toRemove = None
			for p in self.pokemon[pkmId]:
				if p.name == pkmName:
					toRemove = p
					break
			self.pokemon[pkmId].remove(p)
			# If I had to do it differently I'd go:
			pkmName = kwargs['name']

			if pkmName in self.pokemonNames:
				pkmId = self.pokemonNames[pkmName]
				self.pokemonNames.remove(pkmName)
				for identifier in self.pokemon:
					all_pokemon_for_identifier = self.pokemon[identifier]
					# Filters are nice and useful here :D
					# Also they are far more declarative, meaning the intent is more clear
					self.pokemon[identifier] = filter(lambda p: p.name != pkmName, all_pokemon_for_identifier)

			else:
				# Throw a key error here or print something or do whatever
				# Note that generally python says
				# "beg forgiveness rather than ask for permission"
				# so different people will deal with the 'finding a key in a dictionary' problem
				# in different ways.

	def clear(self):
		self.pokemon = {}
		self.pokemonNames = {}

		# Don't be afraid to put a line break between your functions :)

	# At this point I'd probably move all the below functions into another class
	# like a factory class or something because they're not
	# necessarily functions of the Pokedex concept itself
	def getPokeId(self, pkm, array):
		# This is super vague and hard to read...what is array?
		"""
		Write docstrings to easily show people what this function does
		because I don't know what it does :(
		Does it take a Pokemon object and find it's id?
		"""
		try:
			return array.index(pkm)+1
		except:
			# Also neat tip: if you're going to be running a regex
			# five billion times, you can get an amazing speed boost by compiling
			# your regex pattern upfront - this is applicable to most languages (including the dreaded VBA)
			# Google how to do it in Python - it's super easy
			# (Fun fact: I halved application runtime at work once by using compiled regex in VBA)
			if match("^\w+-", pkm):
				return array.index(pkm.split("-")[0])+1
			else:
				self.raiseError("No pokemon id found for pokemon "+pkm)

	def cloneGenerationFromWeb(self, gen):
		if gen == 1:
			self.debugPrint("web clone", "Extracting Pokemon from generation 1 (Pkm Red/Blue)")
			self.cloneFromWeb("http://www.smogon.com/dex/rb/pokemon/")
			self.generation = 1
		elif gen == 2:
			self.debugPrint("web clone", "Extracting Pokemon from generation 2 (Pkm Gold/Silver)")
			self.cloneFromWeb("http://www.smogon.com/dex/gs/pokemon/")
			self.generation = 2
		elif gen == 3:
			self.debugPrint("web clone", "Extracting Pokemon from generation 3 (Pkm Ruby/Sapphire)")
			self.cloneFromWeb("http://www.smogon.com/dex/rs/pokemon/")
			self.generation = 3
		elif gen == 4:
			self.debugPrint("web clone", "Extracting Pokemon from generation 4 (Pkm Diamond/Pearl)")
			self.cloneFromWeb("http://www.smogon.com/dex/dp/pokemon/")
			self.generation = 4
		elif gen == 5:
			self.debugPrint("web clone", "Extracting Pokemon from generation 5 (Pkm Black/White)")
			self.cloneFromWeb("http://www.smogon.com/dex/bw/pokemon/")
			self.generation = 5
		elif gen == 6:
			self.debugPrint("web clone", "Extracting Pokemon from generation 6 (Pkm X/Y)")
			self.cloneFromWeb("http://www.smogon.com/dex/xy/pokemon/")
			self.generation = 6
		elif gen == 7:
			self.debugPrint("web clone", "Extracting Pokemon from generation 7 (Pkm Sun/Moon)")
			self.cloneFromWeb("http://www.smogon.com/dex/sm/pokemon/")
			self.generation = 7
		else:
			self.raiseError("Invalid Generation")
	def cloneFromWeb(self, url):
		startT = time.time()
		r = requests.get(url)
		self.debugPrint("web clone", "Extracting Text Jsons")
		textJson = re.search(r'dexSettings = (\{.*\}\n)', r.text).group(1)
		namesArrayText = requests.get("https://raw.githubusercontent.com/sindresorhus/pokemon/master/data/en.json").text
		self.debugPrint("web clone", "Parsing jsons into Dict")
		rawJson = json.loads(textJson.strip())
		pkms = rawJson['injectRpcs'][1][1]["pokemon"]
		namesArray = json.loads(namesArrayText)
		# I think if you want to make this more efficient you can
		# use lazy evaluation of this sort of list mapping in Python
		namesArray = list(map(lambda x: x.replace(u"\u2019", "'"), namesArray))
		namesArray = list(map(lambda x: x.replace(u"\u2640", "-F"), namesArray))
		namesArray = list(map(lambda x: x.replace(u"\u2642", "-M"), namesArray))
		namesArray = list(map(lambda x: x.strip(), namesArray))
		self.debugPrint("web clone", "Extracting Pokemon...")
		for p in pkms:
			# This is an excellent candidate for a function btw
			obj = Pokemon()
			obj.name = p['name']
			obj.generations = copy.copy(p["genfamily"])
			obj.types = copy.copy(p["alts"][0]["types"])
			obj.id = self.getPokeId(obj.name, namesArray)
			obj.stats = copy.copy(p["alts"][0])
			# Sorry, I don't understand why you're removing these attribs :/
			# Is this to clean certain items from the stats dict?
			obj.stats.pop('types')
			obj.stats.pop("abilities")
			obj.stats.pop("formats")
			obj.evolutions = copy.copy(p["evos"])
			self.addPokemon(obj)
		endT = time.time()
		self.debugPrint("web clone", "Finished Extracting %d pokemon in %f seconds"%(len(pkms),endT-startT))
	def save(self, file):
		# This is mostly fine but if you're writing to files
		# I'd recommend using a 'with' clause
		# so you don't have to clean up afterwards :)
		self.debugPrint("save", "Saving pokemons to file %s"%file)
		toWrite = []
		for plk in self.pokemon.keys():
			pl = self.pokemon[plk]
			for p in pl:
				toWrite.append(p.getDictRep())
		f = open(file, 'w')
		json.dump(toWrite, f)
		f.close()

		# Example with clause
		with open(file, 'w') as f:
			json.dump(toWrite, f)

		self.debugPrint("save", "Save complete")

	def load(self, file):
		self.debugPrint("load", "Loading pokemons from file %s"%file)
		f = open(file, 'r')
		x = json.load(f)
		f.close()
		for p in x:
			obj = Pokemon()
			obj.loadFromDict(p)
			self.addPokemon(obj)
		self.debugPrint("load", "Loaded %d pokemons"%len(x))
		return False

	def getPkmById(self, pkmId):
		return self.pokemon[pkmId]
	def getPkmByName(seld, name):
		pkmId = self.pokemonNames[name]
		pl = self.pokemon[pkmId]
		for p in pl:
			if p.name == name:
				return p
		return None
if __name__ == "__main__":
	pkmDb = PkmDatabase()
	# I see what you were doing here but you can use the python inbuilt logger
	# and log levels (trace, debug, info, error) to much greater effect :)
	# LOG ALL THE THINGS!
	pkmDb.debug = True
	#pkmDb.cloneGenerationFromWeb(1)
	#pkmDb.save("Gen1.pkm")
	pkmDb.load("Gen1.pkm")
	print(pkmDb.getPkmByName(""))
