import random
import numpy

character_probability = {
	'а':0.07872987184577382,
	'б':0.01714433167407771,
	'в':0.046780726653282895,
	'г':0.017309222198547157,
	'д':0.03172215304194634,
	'е':0.08667459711563966,
	'ё':0.0010375254429291492,
	'ж':0.011297142361553457,
	'з':0.015431183367901313,
	'и':0.06638556758212379,
	'й':0.010433073184624496,
	'к':0.03296953915238484,
	'л':0.04530956054534942,
	'м':0.03137952338071001,
	'н':0.06520777812163155,
	'о':0.11426699202189877,
	'п':0.027455343041875004,
	'р':0.04258351330313789,
	'с':0.0536076226534167,
	'т':0.06402142291960845,
	'у':0.02923487584491541,
	'ф':0.0013212656311399076,
	'х':0.008698510524618402,
	'ц':0.0029776658996759197,
	'ч':0.017652922577473733,
	'ш':0.007960786035270132,
	'щ':0.0032539110640471486,
	'ъ':2.3877004517358034E-4,
	'ы':0.016541517613842,
	'ь':0.022005389992852342,
	'э':0.0034262966123563264,
	'ю':0.005800077734103678,
	'я':0.02114132081592478,
}

def coincidence_index(encoded_block, presumable_key_length):
	
	if len(encoded_block) < 2 :
		return -1

	#count character occurances in passed block
	char_occurances = {}
	for char in encoded_block[::presumable_key_length]:
		if char in char_occurances:
			char_occurances[char] += 1
		else:
			char_occurances[char] = 1
		#for key in char_occurances
	
	#cound index
	coincidence_index = 0
	for _ in char_occurances:
		#print(char_occurances[_])
		coincidence_index += char_occurances[_] * (char_occurances[_] - 1)
	#print(coincidence_index)
	coincidence_index /= len(encoded_block[::presumable_key_length]) * (len(encoded_block[::presumable_key_length]))
	#print(coincidence_index)
	return coincidence_index


def guess_key_length(encoded, max_len, verbose=False):

	#blok fragmentation of text
	occurance_index_average = {}
	for r in range (2, max_len+1):
		occurance_indexes = []
		for _ in range (0, len(encoded), r):

			#for every block count coincidence index
			tmp_index = coincidence_index(encoded, r)
			if tmp_index != -1:
				occurance_indexes.append(tmp_index)
			
		#count average index
		occurance_index_average[r] = 0
		for _ in range (0, len(occurance_indexes)):
			occurance_index_average[r] += occurance_indexes[_]
		occurance_index_average[r] /= len(occurance_indexes)

		#print("r = {}, index = {}".format(r, occurance_index_average[-1]))

	if verbose == True:
		for _ in occurance_index_average:
			print("r = {} coincidence index = {}".format(_, occurance_index_average[_]))
	
	#find by max(all wrong key lengths should -> 1/32 < 0.0553)
	max_occurance_freq = max(occurance_index_average.values())
	for _ in occurance_index_average:
		if occurance_index_average[_] == max_occurance_freq:
			return _
	return -1

def get_key(encoded_block, presumable_key_length):

	if presumable_key_length == -1:
		print("Unknown error encountered, key length unrecognized")
		return -1

	#traverse blocks
	most_frequent_keys = []
	for i in range(0, presumable_key_length):

		#find the most frequently used character in block
		char_occurances = {}
		for char in encoded_block[i::presumable_key_length]:
			if char in char_occurances:
				char_occurances[char] += 1
			else:
				char_occurances[char] = 1

		most_frequent_value = max(char_occurances.values())
		most_frequent_keys.append('M')
		for _ in char_occurances:
			if char_occurances[_] == most_frequent_value:
				most_frequent_keys[-1] = _

	key = []
	#print(most_frequent_keys)
	#print()
	for i in range(0, len(most_frequent_keys)):
		key.append((ord(most_frequent_keys[i])-ord('о')) % 32)
	return key

def get_key_Mg(encoded_block, guessed_key_length):

	key_Mg = []
	for _k in range(0, guessed_key_length):
		#iterate through key candidats
		Mig_max = 0
		key_candidate = 0
		for _i in range(0, 31):
			
			#iterate through letters
			Mig = 0
			for _j in range(0, 31):
				Mig += character_probability[chr(1072+_j)] * countOccurances(encoded_block[_k::guessed_key_length], chr(1072+(_i+_j)%32))

			if Mig>Mig_max:
				Mig_max = Mig
				key_candidate = _i

		key_Mg.append(key_candidate)

	return key_Mg

def decypher(encoded, key):
	result = ""
	for i in range(0, len(encoded)):
		result += (chr(( (ord(encoded[i])-1072) - key[i%len(key)] ) % 32 + 1072))
	#print(result)
	return result

def encrypt(text, key):
	result = ""
	for i in range(0, len(text)):
		result += chr( (key[i%len(key)] + ord(text[i]) - 1072)%32 + 1072 )
	return result

def keygen(len):
	return [random.randint(0, 31) for _ in range(len)]

def countOccurances(block, character):

	counter = 0

	for i in range(len(block)):
		if block[i] == character:
			counter += 1
	
	return counter

def task1(message):

	print("TASK 1:")

	encrypted= []
	decrypted = []

	#count coincidence index of plain text
	coincidence_index_plain = coincidence_index(message[::1], 1)

	#encrypt with r = [2-20]
	for i in range(2, 21):
		if i>5 and i<10:
			continue
		key = keygen(i)
		encoded = encrypt(message, key)
		coincidence_index_encrypted = coincidence_index(encoded, i)
		encrypted.append({
			"key_length": i,
			"key": key,
			"coincidence_index_encrypted": coincidence_index_encrypted,
			"encoded": encoded[:20]+"..."
			})

	print("coincidence index of plain text = {}".format(coincidence_index_plain))
	for i in encrypted:
		print(i)

def task2(encoded):

	print("TASK 2:")

	k_len = guess_key_length(encoded, 30, verbose=True)
	key_by_coincidence = get_key(encoded, k_len)
	key_by_M = get_key_Mg(encoded, k_len)

	key_by_coincidence[14] = 15 
	key_by_coincidence[15] = 5
	res = (decypher(encoded, key_by_coincidence))

	print("key length = {}\nkey by coincidence index = {}\nkey by M function        = {}".format(k_len, key_by_coincidence,key_by_M))
	print("\tRESULT:")
	print(res)

	return

if __name__ == '__main__':


	task1(open("v13decoded.txt", "r").read())

	task2(open("encrypted.txt", "r").read())

# 14 скаяспрезреньетъм
# 13 скаяспрезреньпхсм
#ытьможноновконьок
# онцовправдавыйнет
# онцовправдавыйно
# онцовправдавыйчо

#н-ю = 15
#[2, 5, 13, 5, 22, 8, 0, 13, 17, 10, 8, 9, 10, 19, 15, 5, 22] - should be 
#[2, 5, 13, 5, 22, 8, 0, 13, 17, 10, 8, 9, 10, 19, 6, 5, 22] - is