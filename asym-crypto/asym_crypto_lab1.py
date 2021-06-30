import random
from datetime import datetime, timedelta

def performanceCountWrapper(function, *args, **kwargs):
    begin_time = datetime.now().strftime("%H:%M:%S")
    res = function(*args, **kwargs)
    print('\t\tperformance = {} - {}'.format(
        begin_time,
        datetime.now().strftime("%H:%M:%S")
    ))
    return res

#gen_len in bytes
def LehmerLow(state, gen_len):
    res = hex(state&0xff)[2:]
    frequencies = [0]*256
    bigram_freq = [0]*(256*2)
    for i in range(1, gen_len):
        state = (((state*( (1<<16) + 1))) + 119)&(0xffffffff)
        x = state&0xff
        frequencies[x]+=1
        res += "0" + hex(x)[2:] if x<16 else hex(x)[2:]#" " + hex(x)[2:]#
    return (res, frequencies, gen_len)

#gen_len in bytes
def LehmerHigh(state, gen_len):
    res = hex(state&0xff)[2:]
    frequencies = [0]*256
    #print(hex(state&0xff))
    for i in range(1, gen_len):
        state = (((state*( (1<<16) + 1))) + 119)&(0xffffffff)
        x = (state>>24)&0xff
        frequencies[x]+=1
        #print(hex(x) + ", "+ hex(state))
        res += "0" + hex(x)[2:] if x<16 else hex(x)[2:]
    return (res, frequencies, gen_len)

def count_set_bits(val):
    res = 0
    for i in range(20):
        if( (val>>i)&1 ):
            res += 1
    return res&1

#gen_len in bits
def L20(state, gen_len):
    if len(state)!=20:
        return False
    frequencies = [0]*256
    res = ""
    res_byte = ""
    for i in range(0, gen_len):
        new_bit = (int(state[0])+int(state[11])+int(state[15])+int(state[17]))%2
        res_bit = state[0]
        res_byte += res_bit
        state = state[1:]+str(new_bit)
        #print(state)
        if i%8==7:
            int_byte = int(res_byte, 2)
            res += "0" + hex(int_byte)[2:] if int_byte<16 else hex(int_byte)[2:]
            frequencies[int_byte] += 1
            res_byte = ""
    #print("residue bits = {}".format(res_byte))
    if gen_len%8!=0:
        int_byte = int(res_byte, 2)
        res += "0" + hex(int_byte)[2:] if int_byte<16 else hex(int_byte)[2:]
        frequencies[int_byte] += 1
    return (res, frequencies, gen_len//8)

#gen_len in bits
def L89(state, gen_len):
    if len(state)!=89:
        return False
    frequencies = [0]*256
    res = ""
    res_byte = ""
    for i in range(0, gen_len):
        new_bit = (int(state[0])+int(state[51]))%2
        res_bit = state[0]
        res_byte += res_bit
        state = state[1:]+str(new_bit)
        #print(state)
        if i%8==7:
            int_byte = int(res_byte, 2)
            res += "0" + hex(int_byte)[2:] if int_byte<16 else hex(int_byte)[2:]
            frequencies[int_byte] += 1
            res_byte = ""
    if gen_len%8!=0:
        int_byte = int(res_byte, 2)
        res += "0" + hex(int_byte)[2:] if int_byte<16 else hex(int_byte)[2:]
        frequencies[int_byte] += 1
    return (res, frequencies, gen_len//8)

#gen_len in bits  
def Geffe(state, gen_len):
    if len(state[0])!=11 or len(state[1])!=9 or len(state[2])!=10:
        return False
    frequencies = [0]*256
    res = ""
    res_byte = ""
    state_check = state.copy()
    for i in range(0, gen_len):
        new_bit = [0]*3
        res_bit = [0]*3
        for j in range(0, 3):
            if j == 0:
                new_bit[j] = int(state[j][0])^int(state[j][2])                       #L11
            elif j == 1:
                new_bit[j] = int(state[j][0])^int(state[j][1])^int(state[j][3])^int(state[j][4]) #L9   
            elif j == 2:
                new_bit[j] = int(state[j][0])^int(state[j][3])                             #L10
            res_bit[j] = state[j][0]
            #res_byteL11 += res_bit
            state[j] = state[j][1:]+str(new_bit[j])
            state_check[j] += str(new_bit[j])
            #print(state)
        z_bit = 0
        if int(res_bit[2]) == 1: #s == 1
            z_bit = res_bit[0] #x
        else:                    #s == 0
            z_bit = res_bit[1] #y
        # 1111111111100001
        #print("{} {} {} {} {}".format(i, res_bit[0], res_bit[1], res_bit[2], z_bit))
        res_byte += z_bit
        if i%8==7:
            int_byte = int(res_byte, 2)
            res += "0" + hex(int_byte)[2:] if int_byte<16 else hex(int_byte)[2:]
            frequencies[int_byte] += 1
            res_byte = ""
    if gen_len%8!=0:
        int_byte = int(res_byte, 2)
        res += "0" + hex(int_byte)[2:] if int_byte<16 else hex(int_byte)[2:]
        frequencies[int_byte] += 1
    #print("0b{}\n0b{}\n0b{}".format(state_check[0], state_check[1], state_check[2]))
    return (res, frequencies, gen_len//8)

#gen_len in bits
def Wolfram(state, gen_len):
    if state>=2**32:
        return False
    frequencies = [0]*256
    res = ""
    res_byte = ""
    state = int(state)
    for i in range(0, gen_len):
        res_bit = str(state&1)
        res_byte += res_bit
        state = (((state<<1)|(state>>31)) ^ (state | ((state>>1)|(state<<31))))&(2**32-1)
        #print(i)
        #print(state)
        if i%8==7:
            int_byte = int(res_byte, 2)
            res += "0" + hex(int_byte)[2:] if int_byte<16 else hex(int_byte)[2:]
            frequencies[int_byte] += 1
            res_byte = ""
    if gen_len%8!=0:
        int_byte = int(res_byte, 2)
        res += "0" + hex(int_byte)[2:] if int_byte<16 else hex(int_byte)[2:]
        frequencies[int_byte] += 1
    return (res, frequencies, gen_len//8)

#gen_len in bytes
def Librarian(file_path):
    frequencies = [0]*256
    with open(file_path, "rb") as f:
        byte = f.read(1)
        #print(byte)
        res = hex(int.from_bytes(byte, byteorder='big'))[2:]
        count = 1
        while byte:
            #print(byte)
            #print(int.from_bytes(byte, byteorder='big'))
            int_byte = int.from_bytes(byte, byteorder='big')
            frequencies[int_byte] += 1
            byte = f.read(1)
            res += "0" + hex(int_byte)[2:] if int_byte<16 else hex(int_byte)[2:]
            count += 1
        frequencies[int_byte] += 1
    return (res,frequencies, count)

# def big_power_by_mod(a, exp, p):
#   if exp == 0:
#       return 1
#   res = a
#   # for i in range(2, exp+1):
#   #     res = (res*a)%p
#   while(exp!=0)
#   return res

def big_power_by_mod(base, exp, mod):
    if exp == 0: return 1
    if (int(exp) & 1) == 0:
        r = big_power_by_mod(base, exp / 2, mod)
        return (r * r) % mod
    else: return (base % mod * big_power_by_mod(base, exp - 1, mod)) % mod

#bit
def BM_bit(state, gen_len):
    p = int("CEA42B987C44FA642D80AD9F51F10457690DEF10C83D0BC1BCEE12FC3B6093E3", 16)
    a = int("5B88C41246790891C095E2878880342E88C79974303BD0400B090FE38A688356", 16)
    q = int("675215CC3E227D3216C056CFA8F8822BB486F788641E85E0DE77097E1DB049F1", 16)

    frequencies = [0]*256
    res = ""
    res_byte = ""
    state = int(state)
    for i in range(0, gen_len):
        res_bit = "1" if state < q else "0" 
        res_byte += res_bit
        state = big_power_by_mod(a, state, p);
        #print(i)
        #print(state)
        if i%8==7:
            int_byte = int(res_byte, 2)
            res += "0" + hex(int_byte)[2:] if int_byte<16 else hex(int_byte)[2:]
            frequencies[int_byte] += 1
            res_byte = ""
    if gen_len%8!=0:
        int_byte = int(res_byte, 2)
        res += "0" + hex(int_byte)[2:] if int_byte<16 else hex(int_byte)[2:]
        frequencies[int_byte] += 1
    return (res, frequencies, gen_len//8)

#byte
def BM_byte(state, gen_len):
    p = int("CEA42B987C44FA642D80AD9F51F10457690DEF10C83D0BC1BCEE12FC3B6093E3", 16)
    a = int("5B88C41246790891C095E2878880342E88C79974303BD0400B090FE38A688356", 16)
    q = int("675215CC3E227D3216C056CFA8F8822BB486F788641E85E0DE77097E1DB049F1", 16)

    frequencies = [0]*256
    #ranges = [((i*(p-1))//256, ((i+1)*(p-1))//256) for i in range(0, 255)]
    res = ""
    res_byte = ""
    state = int(state)
    for i in range(0, gen_len):
        state = big_power_by_mod(a, state, p);
        int_byte = ((state*128)//q) - 1
        if int_byte < 0:
            int_byte += 1
        #print(state)
        res += "0" + hex(int_byte)[2:] if int_byte<16 else hex(int_byte)[2:]
        frequencies[int_byte] += 1
    return (res, frequencies, gen_len)

#generates gen_len-1 bit
def BBS_bit(state, gen_len):
    p = int("D5BBB96D30086EC484EBA3D7F9CAEB07", 16)
    q = int("425D2B9BFDB25B9CF6C416CC6E37B59C1F", 16)
    n = p*q

    frequencies = [0]*256
    res = ""
    res_byte = ""
    state = state**2 % n #skip x0
    for i in range(0, gen_len):
        res_bit = str(state&1)
        res_byte += res_bit
        state = state**2 % n
        #print(i)
        #print(state)
        if i%8==7:
            int_byte = int(res_byte, 2)
            res += "0" + hex(int_byte)[2:] if int_byte<16 else hex(int_byte)[2:]
            frequencies[int_byte] += 1
            res_byte = ""
    if gen_len%8!=0:
        int_byte = int(res_byte, 2)
        res += "0" + hex(int_byte)[2:] if int_byte<16 else hex(int_byte)[2:]
        frequencies[int_byte] += 1
    return (res, frequencies, gen_len//8)

#generates gen_len-1 byte
def BBS_byte(state, gen_len):
    p = int("D5BBB96D30086EC484EBA3D7F9CAEB07", 16)
    q = int("425D2B9BFDB25B9CF6C416CC6E37B59C1F", 16)
    n = p*q

    frequencies = [0]*256
    res = ""
    res_byte = ""
    state = state**2 % n #skip x0
    for i in range(0, gen_len):
        int_byte = state&0xff
        frequencies[int_byte] += 1
        res += "0" + hex(int_byte)[2:] if int_byte<16 else hex(int_byte)[2:]
        state = state**2 % n
    return (res, frequencies, gen_len-1)

#generates gen_len bits
def built_in(state, gen_len):
    frequencies = [0]*256
    random.seed(a = state, version=2)
    bit_sequence = random.getrandbits(gen_len)
    hex_sequence = hex(bit_sequence)
    count = 0
    while bit_sequence>0:
        frequencies[bit_sequence&0xff] += 1
        bit_sequence = bit_sequence>>8
    #print(hex(random.getrandbits(gen_len)))
    return (hex_sequence[2:], frequencies, gen_len//8)

rules = {
    0.05: 1.645, 
    0.1: 1.282, 
    0.15: 1.036
}

def uniformity_check(results, alpha):
    result = 0
    ksi_quad = 0
    nj = results[2]/256
    for i in range(256):
        ksi_quad += (results[1][i] - nj)**2
    ksi_quad /= nj
    ksi_quad_t = ((510)**(1/2))*rules[alpha]+255
    if ksi_quad<=ksi_quad_t:
        result = True
    else:
        result = False
    print("\t\travnomernost: pract = {}, teor = {}, result = {}".format(ksi_quad, ksi_quad_t, result))
    return result

#bigram frequencies + occurence on first and second place frequencies
def count_bigram_frequencies(text):
    place_occurrence_freq = [[0,0] for i in range(0,256)] # [0,0] or [0.01, 0.01]
    bigram_freq = [0]*(256**2)
    for i in range(0, len(text), 4):
        #print("{}, {}".format(text[i:i+4], hex(int(text[i:i+4], 16))))
        #print("{} {}".format(i, text[i:i+4]))
        bigram_freq[int(text[i:i+4], 16)] += 1
        #print("{} {} {} {}".format(text[i:i+2], text[i+2:i+4],int(text[i:i+2],16),int(text[i+2:i+4], 16)))
        place_occurrence_freq[int(text[i:i+2], 16)][0] += 1
        if text[i+2:i+4] != "":
            place_occurrence_freq[int(text[i+2:i+4], 16)][1] += 1
    return (bigram_freq, place_occurrence_freq)

def independence_check(results, alpha):
    bigram_data = count_bigram_frequencies(results[0])
    result = 0
    ksi_quad = 0
    for i in range(256):
        for j in range(256):
            if bigram_data[1][i][0] != 0 and bigram_data[1][j][1] != 0 and  bigram_data[0][i*256+j] != 0:
                ksi_quad += (bigram_data[0][i*256+j]**2)/(bigram_data[1][i][0]*bigram_data[1][j][1])
            #ksi_quad += bigram_data[0][i*256+j]/(bigram_data[1][i][0]*bigram_data[1][j][1])
    #print("\t\ttmp = {}".format(ksi_quad))
    ksi_quad -= 1
    ksi_quad *= results[2]//2
    ksi_quad_t = (255*(2)**(1/2))*rules[alpha]+255**2
    if ksi_quad<=ksi_quad_t:
        result = True
    else:
        result = False
    print("\t\tindependence: pract = {}, teor = {}, valid = {}".format(ksi_quad, ksi_quad_t, result))
    return result

def count_segment_freq(text, r, segment_len):
    segment_detailed = [[0]*256 for i in range(0, r)] # r massivov po 256 znachenii
    segment_general = [0]*256 # occurrence of byte 0-255 in all segments
    for i in range(0, r*segment_len):
        if text[i:i+2] != "":
            segment_detailed[i//segment_len][int(text[i:i+2], 16)] += 1
            segment_general[int(text[i:i+2], 16)] += 1
    return (segment_detailed, segment_general)

def odnorodnost_check(results, alpha, r):
    result = 0
    ksi_quad = 0
    segment_len = results[2]//r
    n = segment_len * r
    segment_data = count_segment_freq(results[0][:n], r, segment_len)#passing not only m'*r bytes
    for i in range(256):
        for j in range(r):
            if segment_data[1][i] != 0:
                ksi_quad += (segment_data[0][j][i]**2)/(segment_data[1][i]*segment_len)
    ksi_quad -= 1
    ksi_quad *= n
    l = (r-1)*255
    ksi_quad_t = ((2*l)**(1/2))*rules[alpha]+l
    if ksi_quad<=ksi_quad_t:
        result = True
    else:
        result = False
    print("\t\todnorodnost: pract = {}, teor = {}, valid = {}".format(ksi_quad, ksi_quad_t, result))
    return result

def random_bit_str(length):
    tmp = bin(random.getrandbits(length))[2:]
    if len(tmp) < length:
        tmp = "0"*(length-len(tmp)) + tmp
    return tmp

#TODO:   1)launch every gen on 3 different init states
#        2)pass different books for librarian
#        3)dodelat tablitsy
if __name__ == '__main__':
    random.seed(datetime.now())
    print(random.getrandbits(32))
    funcs_and_args = [
        (built_in, [
            [datetime.today() + timedelta(days=20), 10**6],
            [datetime.today() + timedelta(days=1), 10**6],
            [datetime.today() + timedelta(days=4), 10**6]
        ]),
        (LehmerLow, [
            [random.getrandbits(32)+1, 10**6],
            [random.getrandbits(32)+1, 10**6],
            [random.getrandbits(32)+1, 10**6]
        ]),
        (LehmerHigh, [
            [random.getrandbits(32)+1, 10**6],
            [random.getrandbits(32)+1, 10**6],
            [random.getrandbits(32)+1, 10**6]
        ]),
        (L20, [
            [random_bit_str(20), 10**6],
            [random_bit_str(20), 10**6],
            [random_bit_str(20), 10**6]
        ]),
        (L89, [
            [random_bit_str(89), 10**6],
            [random_bit_str(89), 10**6],
            [random_bit_str(89), 10**6]
            ]),
        (Geffe, [
            [[random_bit_str(11),random_bit_str(9),random_bit_str(10)], 10**6],
            [[random_bit_str(11),random_bit_str(9),random_bit_str(10)], 10**6],
            [[random_bit_str(11),random_bit_str(9),random_bit_str(10)], 10**6]
        ]),
        (Librarian, [
            ["../input/librarian-l1/-  .pdf"],
            ["../input/librarian-l1/Programming in Lua.pdf"],
            ["../input/librarian-l1/watershipdown.pdf"]
        ]),
        (Wolfram, [
            [random.getrandbits(32)+1, (10**6)],
            [random.getrandbits(32)+1, (10**6)],
            [random.getrandbits(32)+1, (10**6)]
        ]),
        (BM_bit, [
            [random.randint(0, int("CEA42B987C44FA642D80AD9F51F10457690DEF10C83D0BC1BCEE12FC3B6093E3", 16)-1), (10**6)],
            [random.randint(0, int("CEA42B987C44FA642D80AD9F51F10457690DEF10C83D0BC1BCEE12FC3B6093E3", 16)-1), (10**6)],
            [random.randint(0, int("CEA42B987C44FA642D80AD9F51F10457690DEF10C83D0BC1BCEE12FC3B6093E3", 16)-1), (10**6)]
        ]),
        (BM_byte, [
            [random.randint(0, int("CEA42B987C44FA642D80AD9F51F10457690DEF10C83D0BC1BCEE12FC3B6093E3", 16)-1), (10**6)//8],
            [random.randint(0, int("CEA42B987C44FA642D80AD9F51F10457690DEF10C83D0BC1BCEE12FC3B6093E3", 16)-1), (10**6)//8],
            [random.randint(0, int("CEA42B987C44FA642D80AD9F51F10457690DEF10C83D0BC1BCEE12FC3B6093E3", 16)-1), (10**6)//8]
        ]),
        (BBS_bit, [
            [random.getrandbits(32)+2, (10**6)],
            [random.getrandbits(32)+2, (10**6)],
            [random.getrandbits(32)+2, (10**6)]
        ]),
        (BBS_byte, [
            [random.getrandbits(32)+2, (10**6)],
            [random.getrandbits(32)+2, (10**6)],
            [random.getrandbits(32)+2, (10**6)]
        ]),
    ] 
    alpha = list(rules.keys())
    r = 20
    for generator in funcs_and_args:
        print(str(generator[0]))
        for i in range(len(generator[1])):
            print("\talpha = {}".format(alpha[i]))
            res = performanceCountWrapper(generator[0], *generator[1][i])
            uniformity_check(res, alpha[i])
            independence_check(res, alpha[i])
            odnorodnost_check(res, alpha[i], r)
        print()

 # funcs_and_args = [
 #        (built_in, [
 #            [datetime.today() + timedelta(days=20), 10**6],
 #            [datetime.today() + timedelta(days=1), 10**6],
 #            [datetime.today() + timedelta(days=4), 10**6]
 #        ]),
 #        (LehmerLow, [
 #            [5235, 10**6],
 #            [113, 10**6],
 #            [196782, 10**6]
 #        ]),
 #        (LehmerHigh, [
 #            [511, 10**6],
 #            [12, 10**6],
 #            [6, 10**6]
 #        ]),
 #        (L20, [
 #            ["0000100001"*2, 10**6],
 #            ["1110101011"*2, 10**6],
 #            ["0010101101"*2, 10**6]
 #        ]),
 #        (L89, [
 #            ["00000000001"*8+"1", 10**6],
 #            ["10010110101"*8+"0", 10**6],
 #            ["11110000111"*8+"1", 10**6]
 #            ]),
 #        (Geffe, [
 #            [["11111111111","111110001","0000011111"], 10**6],
 #            [["11000000011","110010101","0111011111"], 10**6],
 #            [["10000111111","111111111","1001011111"], 10**6]
 #        ]),
 #        (Librarian, [
 #            ["watershipdown.pdf"],
 #            ["watershipdown.pdf"],
 #            ["watershipdown.pdf"]
 #        ]),
 #        (Wolfram, [
 #            [4, (10**6)],
 #            [512, (10**6)],
 #            [44535, (10**6)]
 #        ]),
 #        (BM_bit, [
 #            [1342134234, (10**6)],
 #            [4623, (10**6)],
 #            [6, (10**6)]
 #        ]),
 #        (BM_byte, [
 #            [77378, (10**6)//8],
 #            [333, (10**6)//8],
 #            [4, (10**6)//8]
 #        ]),
 #        (BBS_bit, [
 #            [12, (10**6)],
 #            [55, (10**6)],
 #            [777887, (10**6)]
 #        ]),
 #        (BBS_byte, [
 #            [363734, (10**6)],
 #            [7784, (10**6)],
 #            [888, (10**6)]
 #        ]),
 #    ] 