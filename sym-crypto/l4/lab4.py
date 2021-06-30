import bitstring as bit
from bitstring import ConstBitStream as BS

THREADS_OPTIMAL = 4

#recalculate
n1 = 222
c1 = 70

n2 = 229
c2 = 72


#		    0123456789...
#deprecated
stateL1 = 0b0000000000000000000000011
stateL2 = 0b00000000000000000000000111
stateL3 = 0b000000000000000000000001111
stateL4 = 0b0111

def CountBits(n):
	n = (n & 0x5555555555555555) + ((n & 0xAAAAAAAAAAAAAAAA) >> 1)
	n = (n & 0x3333333333333333) + ((n & 0xCCCCCCCCCCCCCCCC) >> 2)
	n = (n & 0x0F0F0F0F0F0F0F0F) + ((n & 0xF0F0F0F0F0F0F0F0) >> 4)
	n = (n & 0x00FF00FF00FF00FF) + ((n & 0xFF00FF00FF00FF00) >> 8)
	n = (n & 0x0000FFFF0000FFFF) + ((n & 0xFFFF0000FFFF0000) >> 16)
	n = (n & 0x00000000FFFFFFFF) + ((n & 0xFFFFFFFF00000000) >> 32) # This last & isn't strictly necessary.
	return n

def gh():
	global stateL4

	poly = 0b1001 # x4 = x0 + x2 + x3

	new_bit = CountBits(poly & stateL4)%2
	stateL4 = ((stateL4 << 1) ^ new_bit)
	ret = 			0b10000 & stateL4 # get 26th bit
	stateL4 &=      0b01111 & stateL4 # nullify 26th bit
	print("nbit = {} state = {}".format(new_bit, bin(stateL4)))

	if ret!=0:
		return 1
	else:
		return 0

#should use ulls instead of array of bits -> no difference in performance? only in mem storage
#but results will be used to calculate R -> performance increase? 
# or should i convert result array of bits to longs to speed up R calculation
#could convert with int("0b...", 2)
#parallelize?
def genL1(length, init_state = 0, init_state_range = (0,0)):
	
	print("started thread L1 {}".format(init_state_range))
	quarter = (init_state_range[1]-init_state_range[0])/4 + init_state_range[0]

	# x25 = x0 + x3
	poly = 0b1001000000000000000000000

	result = []
	result_append = result.append

	#if range passed
	if init_state_range[0] != 0 and init_state_range[1] != 0:
		print("inside range initi proc")
		#iterate through init states
		# init_state_range[0] -> 1
		# init_state_range[1]+1 -> 2**25-1
		for k in range(init_state_range[0], init_state_range[1]+1):

			if k % 10000 == 0:
				print(k)

			if k == quarter:
				print("reached quarter")

			result_for_init = []
			result_for_init_append = result_for_init.append
			init_state_tmp = k

			#iterate through length of requested sequence
			for i in range(length):

				# using array of bits 
				new_bit = CountBits(poly & init_state_tmp)%2
				init_state_tmp = ((init_state_tmp << 1) ^ new_bit)
				ret = 			0b10000000000000000000000000 & init_state_tmp # get 26th bit
				init_state_tmp &=      0b01111111111111111111111111 # nullify 26th bit
				if ret != 0:
					result_for_init_append(1)
				else:
					result_for_init_append(0)

				## using ulls -
				#print(bin(stateL1))
			result_append(result_for_init)
	#if single init state passed
	else:
		result_for_init = []
		for i in range(length):
			new_bit = CountBits(poly & init_state)%2
			init_state = ((init_state << 1) ^ new_bit)
			ret = 			0b10000000000000000000000000 & init_state # get 26th bit
			init_state &=      0b01111111111111111111111111 # nullify 26th bit
			if ret != 0:
				result_for_init.append(1)
			else:
				result_for_init.append(0)
		result.append(result_for_init)

	return result

def genL2(length, init_state = 0, init_state_range = (0,0)):

	poly = 0b11100010000000000000000000

	result = []

	#if range passed
	if init_state_range[0] != 0 and init_state_range[1] != 0:

		#iterate through init states
		# init_state_range[0] -> 1
		# init_state_range[1]+1 -> 2**25-1
		for k in range(init_state_range[0], init_state_range[1]+1):
			result_for_init = []
			init_state_tmp = k

			#iterate through length of requested sequence
			for i in range(length):

				# using array of bits 
				new_bit = CountBits(poly & init_state_tmp)%2
				init_state_tmp = ((init_state_tmp << 1) ^ new_bit)
				ret = 			0b100000000000000000000000000 & init_state_tmp # get 27th bit
				init_state_tmp &=      0b011111111111111111111111111 # nullify 27th bit
				if ret != 0:
					result_for_init.append(1)
				else:
					result_for_init.append(0)

				## using ulls -
				#print(bin(stateL1))
			result.append(result_for_init)
	#if single init state passed
	else:
		result_for_init = []
		for i in range(length):
			new_bit = CountBits(poly & init_state)%2
			init_state = ((init_state << 1) ^ new_bit)
			ret = 			0b100000000000000000000000000 & init_state # get 26th bit
			init_state &=      0b011111111111111111111111111 # nullify 26th bit
			if ret != 0:
				result_for_init.append(1)
			else:
				result_for_init.append(0)
		result.append(result_for_init)

	return result

def genL3(length, init_state = 0, init_state_range = (0,0)):

	poly = 0b111001000000000000000000000

	result = []

	#if range passed
	if init_state_range[0] != 0 and init_state_range[1] != 0:

		#iterate through init states
		# init_state_range[0] -> 1
		# init_state_range[1]+1 -> 2**25-1
		for k in range(init_state_range[0], init_state_range[1]+1):
			result_for_init = []
			init_state_tmp = k

			#iterate through length of requested sequence
			for i in range(length):

				# using array of bits 
				new_bit = CountBits(poly & init_state_tmp)%2
				init_state_tmp = ((init_state_tmp << 1) ^ new_bit)
				ret = 			0b1000000000000000000000000000 & init_state_tmp # get 27th bit
				init_state_tmp &=      0b0111111111111111111111111111 # nullify 28th bit
				if ret != 0:
					result_for_init.append(1)
				else:
					result_for_init.append(0)

			result.append(result_for_init)
	#if single init state passed
	else:
		result_for_init = []
		for i in range(length):
			new_bit = CountBits(poly & init_state)%2
			init_state = ((init_state << 1) ^ new_bit)
			ret = 			0b1000000000000000000000000000 & init_state # get 26th bit
			init_state &=      0b0111111111111111111111111111 # nullify 26th bit
			if ret != 0:
				result_for_init.append(1)
			else:
				result_for_init.append(0)
		result.append(result_for_init)

	return result


def Geffe(length, initL1, initL2, initL3):

	result = []

	#get list of results from L3
	who_to_invoke_l = genL3(length, init_state=initL3)
	print("gen L3 complete")

	timesL1 = who_to_invoke_l.count(1)

	resultL1 = genL1(timesL1, init_state=initL1)
	print("gen L1 complete")
	resultL2 = genL2(length - timesL1, init_state=initL2)
	print("gen l2 complete")

	#could do it in 2 threads
	r1 = 0
	r2 = 0
	for i in range(len(who_to_invoke_l)):
		if who_to_invoke_l[i] == 1:
			#print("invoking 1")
			result.append(resultL1[r1])
			r1 += 1
		else:
			#print("invoking 2")
			result.append(resultL2[r2])
			r2 += 1

	print("l1 = {}\n\n l2 = {}\n\n l3 = {}\n\n rsult = {}".format(
			resultL1,
			resultL2,
			who_to_invoke_l,
			result
		)
	)

def toFindNandCL1(z):

	tmp = 1
	for i in range(2**25 - 1):

		#statistical hypothethis test h0 = { p(xj+zj=1) = 1/4 }


		tmp += 1

	return

import queue
from threading import Thread

# raspotochit na 4 potoka:
# 	divide 2**25-1 na 4
# 	(2**25-1)/4 init states for any thread
# T(n) = 2**25 * n1
def findL1(encoded):

	R = 0

	suitable_inits = []
	
	step = int((2**25)/THREADS_OPTIMAL)

	threads_results = []

	#prepare for m threading
	threads_list = []

	que = queue.Queue()

	for k in range(THREADS_OPTIMAL):
		print((k*step, (k+1)*step))
		t = Thread(target = lambda q, arg1, arg2: q.put((arg1, genL1(arg1, init_state_range=arg2))), args = (que, n1, (k*step, (k+1)*step)))
		t.start()
		threads_list.append(t)

	#wait for results in queue
	for t in threads_list:
		t.join()

	#check return values
	while not que.empty():
		threads_results.append(que.get())

	print(threads_results)


	# #iterate through all init states of L1
	# for i in range(1, 2**25-1):

	# 	#generate n1 results from L1
	# 	stateL1 = i # set init state to tmp
	# 	resL1 = genL1(n1)

	# 	#count R
	# 	for j in range(0, n1):
	# 		if resL1[j] == int(encoded[j]):
	# 			R += 1

	# 	if R<c1:
	# 		suitable_inits.append(i)
	# 	print("nexto")

	# return suitable_inits


if __name__ == '__main__':


	encoded4dummies = "11111010010100001110001111101110010001111110101000011011000010001001000001100111111110001110100111110100011101111010011110100000001000001110000000011000000000011100011111101110100100110111101100101100011111110000001101010110110000110001111111110011011010011010000110111011101111011001101000111000111001100100010100110111001110001100011100100011011101100110011010001110001010101110000001011111000110101011010101000001001010101110011010101101000110011100110111001010101001010111000110101001000011001110111011110000001011011110111000110010100110110101010000011011011101001011100010001101000101001011110001011010111001101010111001001010110101010100001010111000110101110101111111111101001111011101100100101100000010010010000011010001011101100101110011111100100000111110100110000101010011111001100101010011000101001000101010100101110110101011001100011000010101110011000011111100100111011111111010101011011100101010100101000100111101001010001010110001001010000000110101101110001101110110001001110010010100101110000001110000011100001111110110001111011110011101101001100100101101111011010101001011100000010100111011000000011100011101110000101010100000011011111110011111110010000010010100100000111100001001111000111011001101101101011001100011000111101100010101011100110111000110011101100001101110010011111100000011101000000001110000100010101100100111011110011110101001110101011110000111101000110100010100000101010110001010111011010111111110101000100100111111111101000110010011101101001110110000010100110000101001010101010100110111111011011101001101010101001010011000100100110111001101101001001101010011001100110001010011001100111001110000100010001011110011101111011100110101001110001110000011101100100101100100010100010101011001011100000101001111001010100000001101011111101101000110000011110101101000011010110010100100111000101000001101111101001010011101111111101101100111001111110110110110111010100011011111101000110110010100011110000111010011011111000000111010001001001100000111010011100110011110101110000111110101010010100101100001010001000110010000110110"
	encoded4realman = "10101101111000010011100110001011100011101001110101001001111011110001010100000100100111010110000110101001101011010110110011000001101001111010100000000111001001011100000110000011000100001000101100111010010000001010100110100111110101110001110101000111100101000110011110111100100111100100000111100001001110011101001110000101110000100010110101001100010001110101101111000000111111111000001100101001100011000101110110100010000000011101010000110010011010110110111001001100010101110010000110011010100011011100010110001010000011001110011001010011011000011100001111110010100110101011011111110110111010001111101000111100111111111101010011000101101000101000111111101000101110001001101011110010000001101010101110110010100011100001101000011000010111100100100000000110010111000011100000000010010001001000110101000000110000100111011011000100011000000011000111101000110011111100010000000111110111010101011010100011011001111110011011001100010101100110110100111010011011000011110011011011010011001001000101111001000110100111110100110011101100000010001000011011011010111110011000110101110001010001010111100010001101110101101000010101100011100011000010101000111101000110001101001110011110101110101111000011011110101011000110101111101000000111010010000000010111011000000011111111000011000010100010011011011001100001011001000111100011100101000110110100001101000100111111101111100111001000001011010001010110110010001100011100101011010001111001011011000010011101011001100100100101000111111000111110010010000100001101111011010010001010000011000111001001111110111001000000011110000001110001101001000000100101011111000001101000010101100011001001111111011011001100101101100011111010110100010101011001111011111100100101010001111111010010011111001000111011110001100001011110101000100010110110100111001001000010101000011100011110110010010011110100011111110100001001010000000011000000111101000000101001101111010110110010010010110111001000100101001010010110101011100110101000001000001000001000101010000101100110100000111001011100100100000001010100010000110011100111000110111111001001"

	# egor
	encoded4dummies = "01111010110000011110000000000101001100011100010000110000010000011011110100010101010000011101011101000100101000000010111011101000000000100011110100110000001110000011011100001010011010010001011010000001010101011110010011100101001111000010000011111000101000001001100001001110110010110100010010111111001011001010001110001111100100110010111000010011110110000100011101011111101101111110001101011010100101000110101011011111100011010101110101111001101010111110101100101110110011111101010001001111000000010001100110111000011001010010000101001111011110010001010110001011000100101001001011010100000101010100100100110011011011100001011100000100000011111111010101001011001110011011011101110001011011101010000111000101110000011100010110111101100001111111011101101010000111111011100011010110001010101001111001111010010101010111001101111110101011010011010111010011000000110000010000111011010110010101101101101000111011111111010000110001110110010111101111010111111110010111111100111001000010101110100101011010111110011111110001001100101001011111101100110111010100000110100010011101011010010000110001011011001100110101100001001010110000101011000100100101010011000111010001011100110000010101000010011111011011000001110110110001000001011101110101000100000101100000111001101101100101010010100100001101110001011111010000110000101001000000100001011011110010111010111100000011110100100100111000000011011000000100101010000010000011110011101101010010100111111110101000100001000000110010010110001110111110010000110010101110111011101011011110110000110000111001101111000001000000101110110010100100010001110000111100101001010100100111111110010001100101001101101010001011011101110011111011110011001000111011010011111110010010000011100010100110011011011100000001110111001101111000011011100101010111011111110101110101101101010100111000110101000111100100100101100110110111011101110110111001101010010001000000100100100101100000101111000001011100011100000001000110110010000111100101111000111100001111010101001011001110101011111111000101011000011011001011111111101010100101110011111101"

	resl1 = genL2(2048, init_state=3)
	print(resl1)

	# print(bin(stateL2))
	# for i in range(0, 2**26-1):
	# 	genL2()
	# print(bin(stateL2))

	# print(bin(stateL3))
	# for i in range(0, 2**27-1):
	# 	genL3()
	# print(bin(stateL3))

	# print("initial state = {}".format(bin(stateL4)))
	# for i in range(0, (2**4)-1):
	# 	print(i+1)
	# 	gh()
	# print("final state = {}".format(bin(stateL4)))

	#Geffe(2048)

	# b = 1/2**25
	# print("b={}".format(b))
	# print("1-b={}".format(1-b))

	print(genL1(n1, init_state_range=(1, 8388608)))

	#findL1(encoded4dummies)

	print()