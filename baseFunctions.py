import string
import random
import json
charecters = string.ascii_letters + string.digits + "~!@#$%^&*()_+`-=[]|:;<>?,./"
def generateKey(n,l=None):
	key = ''.join(random.SystemRandom().choice(charecters) for _ in range(n))
	if(l is not None):
		handle = open(l,'w')
		handle.write(key)
		handle.close()
	print(key)

def diffieHellmanMapping():
	vals = set()
	while(len(set(vals))<len(charecters)):
		vals.add(random.randint(11,99))
	vals = list(vals)
	random.shuffle(vals)
	random.shuffle(vals)
	mapping = {}
	for x in range(len(charecters)):
		print(f"{vals[x]:02d}")
		mapping[charecters[x]] = f"{vals[x]:02d}"
		mapping[f"{vals[x]:02d}"] = charecters[x]
	handle = open("mapping",'w')
	handle.write(json.dumps(mapping))
	handle.close()
	print(mapping)

diffieHellmanMapping()
# generateKey(59,"modulus")
# generateKey(128,"privateKeys/KeyForA")
# generateKey(128,"privateKeys/KeyForB")