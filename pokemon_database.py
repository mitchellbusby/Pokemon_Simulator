from bs4 import BeautifulSoup
import re
import requests
import time
import json
import copy 

def match(regex, text):
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
	def raiseError(self, s):
		raise Exception(s)
	def addPokemon(self, pkm):
		if not isinstance(pkm, Pokemon):
			self.raiseError("Object supplied of invalid type: "+type(pkm))
		try:
			self.pokemon[pkm.id].append(pkm)
		except:
			self.pokemon[pkm.id]=[pkm]
		self.pokemonNames[pkm.name] = pkm.id
	def removePokemon(self, **kwargs):
		if 'id' in kwargs:
			pkmId = kwargs['id']
			pkm = self.pokemon[pkmId]
			for p in pkm:
				self.pokemonNames.pop(p.name)
			self.pokemon.pop(pkmId)
		elif 'name' in kwargs:
			pkmName = kwargs['name']
			pkmId = self.pokemonNames[pkmName]
			self.pokemonNames.pop(pkmName)
			toRemove = None
			for p in self.pokemon[pkmId]:
				if p.name == pkmName:
					toRemove = p
					break
			self.pokemon[pkmId].remove(p)
	def clear(self):
		self.pokemon = {}
		self.pokemonNames = {}
	def getPokeId(self, pkm, array):
		try:
			return array.index(pkm)+1
		except:
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
		namesArray = list(map(lambda x: x.replace(u"\u2019", "'"), namesArray))
		namesArray = list(map(lambda x: x.replace(u"\u2640", "-F"), namesArray))
		namesArray = list(map(lambda x: x.replace(u"\u2642", "-M"), namesArray))
		namesArray = list(map(lambda x: x.strip(), namesArray))
		self.debugPrint("web clone", "Extracting Pokemon...")
		for p in pkms:
			obj = Pokemon()
			obj.name = p['name']
			obj.generations = copy.copy(p["genfamily"])
			obj.types = copy.copy(p["alts"][0]["types"])
			obj.id = self.getPokeId(obj.name, namesArray)
			obj.stats = copy.copy(p["alts"][0])
			obj.stats.pop('types')
			obj.stats.pop("abilities")
			obj.stats.pop("formats")
			obj.evolutions = copy.copy(p["evos"])
			self.addPokemon(obj)
		endT = time.time()
		self.debugPrint("web clone", "Finished Extracting %d pokemon in %f seconds"%(len(pkms),endT-startT))
	def save(self, file):
		self.debugPrint("save", "Saving pokemons to file %s"%file)
		toWrite = []
		for plk in self.pokemon.keys():
			pl = self.pokemon[plk]
			for p in pl:
				toWrite.append(p.getDictRep())
		f = open(file, 'w')
		json.dump(toWrite, f)
		f.close()
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
	pkmDb.debug = True
	#pkmDb.cloneGenerationFromWeb(1)
	#pkmDb.save("Gen1.pkm")
	pkmDb.load("Gen1.pkm")
	print(pkmDb.getPkmByName(""))




