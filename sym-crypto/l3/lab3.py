import math
remember = []

def EEA(a, mod):

	#? handle module = 0
	if mod == 0:
		return {
			"gcd":0,
			"inverse":0
		}

	m = mod
	x = 0
	y = 0

	nod = 1
	x1 = 0
	x2 = 1
	y1 = 1
	y2 = 0

	while mod>0:
		q = a//mod
		r = a - q*mod
		x = (x2 - q*x1)%m
		y = (y2 - q*y1)%m
		a = mod
		mod = r
		x2 = x1
		x1 = x
		y2 = y1
		y1 = y
		
	nod = a
	x = x2
	y = y2

	if nod == 1:
		return {
			"gcd":nod,
			"inverse":x
		}
	else:
		return {
			"gcd":nod,
			"inverse":0
		}

def solveCongruationSystem(a, b, mod):

	#handle b=0, a=0?

	res = EEA(a,mod)
	d = res["gcd"]
	inverseAN = res["inverse"]
	#print("gcd = {}, inverse = {}".format(nodAN, inverseAN))

	x = []

	#one root
	if d == 1:
		x.append((inverseAN*b)%mod)
	elif d > 1:
		#zero roots
		if b%d != 0:
			print("no solution!!!")
		else:
			#>1 roots
			x0 = ( (b/d)*EEA(a/d, mod/d)["inverse"] ) % (mod/d)
			for i in range(0, d):
				x.append(x0+i*(mod/d))

	#print(x)
	return x

#should be used later on
#return top 5 bigrams of encoded message
def find5MostFrequent(encoded):

	#count frequency
	encodedFrequencies = {}
	for _ in range(0, len(encoded), 2):
		if encoded[_:_+2] in encodedFrequencies:
			encodedFrequencies[encoded[_:_+2]] += 1
		else:
			encodedFrequencies[encoded[_:_+2]] = 1

	#sort by value in dictionary returns list of tuples
	encodedFrequencies = sorted(encodedFrequencies.items(), key=lambda x:x[1], reverse = True)

	#print(encodedFrequencies[:10])
	return [encodedFrequencies[i][0] for i in range(0, 5)]
	

def bigramToInt(bigram, pos = -1):
	hint = ord(bigram[0])-1072
	lint = ord(bigram[1])-1072

	# print(hint)
	# print(lint)
	# print('endtoint')

	#check for Ъ 27 = 
	#works this way
	if pos == -1:
		if hint>27:
			hint-=1
		if lint>27:
			lint-=1
	else:
		if hint>27:
			remember.append(pos)
			hint-=1
		if lint>27:
			remember.append(pos+1)
			lint-=1
	
	# print(hint)
	# print(lint)
	# print("sfds")

	return (hint)*31 + lint

def intToBigram(intBi):
	hchar = (intBi)//31
	lchar = (intBi)%31

	# print(hchar)
	# print(chr(hchar+1072))
	# print(lchar)
	# print(chr(lchar+1072))

	#doesnt work this way 27!!!
	#check for Ъ 
	# if hchar>28:
	# 	hchar+=1
	# if lchar>28:
	# 	lchar+=1

	return "".join([chr(hchar + 1072),chr(lchar + 1072)])

#return 5*5 tupples
def decrypt(encoded, mostFrequentRus, mostFrequentCyphered):

	#composition = (cypheredBi, plainBi)

	count_iter = 0

	for i in range(len(mostFrequentCyphered)):
		for j in range(len(mostFrequentRus)):
			composition1 = (mostFrequentCyphered[i], mostFrequentRus[j])
			composition1Mod32 = (bigramToInt(mostFrequentCyphered[i]), bigramToInt(mostFrequentRus[j]))
			for i_ in range(i, len(mostFrequentCyphered)):

				for j_ in range(j, len(mostFrequentRus)):
					if i*len(mostFrequentCyphered)+j>i_*len(mostFrequentCyphered)+j_:
						continue

					count_iter += 1
					#print("indexes = {} {} {} {}".format(i, j, i_, j_))

					composition2 = (mostFrequentCyphered[i_], mostFrequentRus[j_])
					composition2Mod32 = (bigramToInt(mostFrequentCyphered[i_]), bigramToInt(mostFrequentRus[j_]))

					#process sets of 2 bigram compositions
					a = solveCongruationSystem((composition1Mod32[1] - composition2Mod32[1])%(31**2), (composition1Mod32[0] - composition2Mod32[0])%(31**2), 31**2)
					#find b
					for _ in range(len(a)):
						b = (composition2Mod32[0]-a[_]*composition2Mod32[1])%(31**2)
						attempt = recognition(decypher(encoded, {"a":int(a[_]), "b":int(b)}))
						if attempt != False:
							return {
								"key":{"a":int(a[_]), "b":int(b)},
								"decoded":attempt#"".join(attempt_list)
							}
	return False

	print("len cyph = {} len rus = {} count iter = {}".format(len(mostFrequentCyphered), len(mostFrequentRus), count_iter))
	print()

def recognition(decoded):

	# print("DECODED IN ROCOGNITION")
	# print(decoded)
	#check least and most frequent characters
	#print(decoded)
	least_frequent = {
		"ф":[0,0.0013212656311399076],
		"щ":[0,0.0032539110640471486],
		#"ь":(0,0.022005389992852342),#0.02 - kinda frequent
	}
	most_frequent = {
		"о":[0,0.11426699202189877],
		"а":[0,0.07872987184577382],
		"е":[0,0.08667459711563966],
	}
	for _ in decoded:
		if _ in least_frequent:
			least_frequent.get(_)[0] = least_frequent.get(_)[0]+ 1
			#print()
		elif _ in most_frequent:
			most_frequent.get(_)[0] += 1
			#print()

	#print("freq output")
	for _ in least_frequent:
		least_frequent.get(_)[0] = least_frequent.get(_)[0]/len(decoded)
		#print(least_frequent.get(_)[0])
		#print(least_frequent.get(_)[1]*2)
		if least_frequent.get(_)[0]>least_frequent.get(_)[1]*2:
			return False
	#print()
	for _ in most_frequent:
		most_frequent.get(_)[0] = most_frequent.get(_)[0]/len(decoded)
		#print(most_frequent.get(_)[0])
		#print(abs(most_frequent.get(_)[0]-most_frequent.get(_)[1]))
		#print(most_frequent.get(_)[1]/3)
		if abs(most_frequent.get(_)[0]-most_frequent.get(_)[1])>most_frequent.get(_)[1]/3:
			return False

	#print(least_frequent)
	#print(most_frequent)
	#print(decoded)
	#print("SUCCESS")
	return decoded


def decypher(encoded, key):
	result = ""
	for i in range(0,len(encoded)-1,2):
		intBi =  (EEA(key["a"], 31**2)["inverse"]*(bigramToInt(encoded[i:i+2], i)-key["b"]))%(31**2)
		trueBigram = intToBigram( intBi )
		result += trueBigram
	return result

if __name__ == '__main__':

	top5RusBigrams = ["то", "ен", "ст", "на", "но"]#["но","то","по","ер","ра"]#

	encoded = open("variants\\13.txt", "r").read().replace('\n', '').replace('\r', '')

	top5Encoded = (find5MostFrequent(encoded))
	
	print("top 5 frequent bigrams in encoded message = {}".format(top5Encoded))
	
	result = decrypt(encoded, top5RusBigrams,top5Encoded)
	if result == False:
		print("Key not found")
	else:
		#print(result)
		result_l = list(result["decoded"])
		for _ in range(len(result_l)):
			if ord(result_l[_])>(1072+26):
				result_l[_] = chr(ord(result_l[_])+1)
		print("Decoded message with key = {}:".format(result["key"]))
		print("".join(result_l))

		#debug output
		# for i in range(0, len(encoded), 2):
		# 	print("{} -> {}, {} -> {}".format(
		# 			encoded[i:i+2], result["decoded"][i:i+2],
		# 			bigramToInt(encoded[i:i+2]), bigramToInt(result["decoded"][i:i+2])
		# 		))

# 0,0->(аф, но), 1,1->(яф то), a=99.0,b=700.0
# b must be 60

#4x=2mod22
#ын = 26*31 + 13
#ы -> 27ая, но так как пропоускаем Ъ она -> 26
