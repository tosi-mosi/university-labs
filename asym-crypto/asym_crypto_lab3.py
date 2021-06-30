import re
import random
from datetime import datetime
import requests

def stringToInt(string):
    return int("".join(
        "0"+hex(ord(char))[2:]
        if len(hex(ord(char))[2:]) == 1 
        else hex(ord(char))[2:] 
        for char in string
    ), 16)

def intToString(integer):
    return "".join(
        chr((integer>>i)&0xff) for i in range(0, integer.bit_length(), 8)
    )[::-1]

def performanceCountWrapper(function, *args, **kwargs):
    begin_time = datetime.now().strftime("%H:%M:%S")
    res = function(*args, **kwargs)
    print('\t\tperformance = {} - {}'.format(
        begin_time,
        datetime.now().strftime("%H:%M:%S")
    ))
    return res

def gen_first_primes(N):
    result = []
    for i in range(0, N+1):
        if re.match(r'^1?$|^(11+?)\1+$', '1' * i) == None:
            result.append(i)
    return result #[2,3,5,....]

def gen_r_array_precomputation(small_primes, t):
    result = []
    for m in small_primes:
        r_m = [1]
        for i in range(1, t):
            tmp = (r_m[-1]<<1)%m
            if tmp == r_m[-1]: #is periodic -> should compare with r_m[i][0]=1
                r_m += r_m[:i-1]*(t//i)+r_m[:t%i]
                break
            r_m.append(tmp)
        result.append(r_m)
    return result

def gcd(a,b): 
    if a<b:
        c = a
        a = b
        b = c
    if b == 0:
        return a
    else:
        return gcd(b, a%b)

def jacobi(a, p):
  if p == 2:
      return 1
  res = 1
  while abs(a)>1:
      a = a%p
      power_of_2 = 0
      while a&1!=1:
          a = a>>1
          power_of_2 += 1
      if power_of_2&1 == 1:
          if ((p**2-1)>>3)&1:
              res = -res
      if a!=1:
          if ((p-1)>>1)&1 == 1 and ((a-1)>>1)&1 == 1:
              res = -res
          tmp = a
          a = p%a
          p = tmp
  return 0 if res == -1 else res

def random_gen_from_lab1(state, gen_len):
    frequencies = [0]*256
    #random.seed(a = state) #delete this for reproducibility
    bit_sequence = random.getrandbits(gen_len)
    hex_sequence = hex(bit_sequence)
    count = 0
    while bit_sequence>0:
        frequencies[bit_sequence&0xff] += 1
        bit_sequence = bit_sequence>>8
    return (hex_sequence[2:], frequencies, gen_len//8)

def find_prime(bit_length, first_primes, exclude = [], bases_to_check = 10):

    random_vals_generated = [] #[debug] value

    #when first choose by random, check if random_val has desireble bit_length
    random_val = int(random_gen_from_lab1(None, bit_length)[0], 16) # = x
    if random_val.bit_length() != bit_length:
        random_val ^= (1<<(bit_length-1))

    #regenerate if random_val is on the upper bound
    while random_val+3>=(1<<(bit_length)):
        print("[extremely improbable situation] random_val={}, bound={}".format(hex(random_val+3), hex(1<<(bit_length-1))))
        random_val = int(random_gen_from_lab1(None, bit_length)[0], 16)
        if random_val.bit_length() != bit_length:
            random_val ^= (1<<(bit_length-1))

    shift_bound = 1
    upper_bound = 0

    print(f"start from {random_val}")

    while True:
        is_prime = True

        #changing starting point for prime search when bound was crossed
        if(shift_bound != 1):
            print("no primes found between {} and {}\n\
                expanding upper bound to {} bits".format(
                    random_val, 
                    upper_bound,
                    bit_length+shift_bound,
                )
            )
            random_val = upper_bound #starting where we finished
        
        #make it 4k+3
        random_val += 3-(random_val%4) # m0 = 4k+3
        
        upper_bound = 1<<(bit_length+shift_bound-1)

        r_precomputed = gen_r_array_precomputation(first_primes[1:], random_val.bit_length())

        for test_subject in range(random_val, upper_bound, 4):
            is_prime = True
            prime_witnesses = []

            #check with trial division by Pascal
            #check primes m = [3, 5, 7 ...], exclude 2 from list of first primes
            #r_precomputed[i-1] !!! while first_primes[i]
            for i in range(1, len(first_primes)):
                N = 0
                for k in range(0, test_subject.bit_length()):
                    N = (N + ((test_subject>>k)&1) * r_precomputed[i-1][k])%first_primes[i]
                if N == 0:
                    is_prime = False #is composite
                    break
            if is_prime == False:
                print(f"[composite]{test_subject}")
                continue

            #check with miller rabin
            d = test_subject-1
            s = 0
            while True:
                if d & 1 == 1:
                    break
                d >>= 1
                s += 1
            for i in range(bases_to_check):
                is_prime = False
                base = random.randint(2, test_subject-1)
                if gcd(base, test_subject) != 1:
                    print(f"[composite]{test_subject}")
                    is_prime = False
                    break #is composite
                tmp = pow(base, d, test_subject)
                if tmp == 1 or tmp == test_subject-1: #is prime
                    prime_witnesses.append(i)
                    continue
                for r in range(1, s):
                    tmp = (tmp**2)%test_subject # optimize ?
                    if tmp == test_subject - 1:# is prime
                        is_prime = True
                        break
                    if tmp == 1:# is composite
                        print(f"[composite]{test_subject}")
                        is_prime = False
                        break
                if is_prime == True: #append prime witnesses, go for next base
                    prime_witnesses.append(i)
                else:                #test_subject is composite, go for next subject
                    break
            if len(prime_witnesses) == bases_to_check:
                if test_subject not in exclude:
                    print(f'[prime]{test_subject}')
                    return test_subject
                else:
                    print("{} is in exclude list {}, proceeding with search".format(test_subject, exclude))
                    return find_prime(bit_length, first_primes, exclude, bases_to_check)
            
        #doshli do kontsa i ne nashli chto iskali sdvigaem granitsy
        shift_bound+=1
    
def GenerateOrderedPrimes(bit_length, quantity):
    primes = []
    precomputed_first_primes = gen_first_primes(300)
    for i in range(quantity):
        primes.append(find_prime(bit_length, precomputed_first_primes, exclude = primes))
    #primes.sort()
    return sorted(primes)

def GenerateKeyPair(p, q):
    b = random.randint(0, p*q - 1)
    return {
        "private": {
            "p" : p,
            "q" : q,
            "b" : b
        },
        "public" : {
            "n" : p*q,
            "b" : b
        }
    }

def Format(message, n):
    modulus_byte_length = n.bit_length()//8 + (1 if n.bit_length()%8!=0 else 0)
    message_byte_length = message.bit_length()//8 + (1 if message.bit_length()%8!=0 else 0)
    if (message_byte_length>modulus_byte_length-10):
        print("[error] cant format. Message byte length > public modulus byte length-10")
        return None
    return random.randint(0, (1<<64) - 1) ^ (0xff<<(8*(modulus_byte_length-2))) ^ (message<<64)

def Unformat(formated_message, n):
    if(formated_message >> (formated_message.bit_length()-8) != 0xff):
        print("[unformat] invalid message encountered")
        return
    # formated_message >> 64 (eliminated postfix)
    # -64 -> we have eliminated postfix -> -64 bits
    # -8  -> we don't take prepending 0xff
    # -1  -> want 1*n bitmask, shift n-1        
    return (formated_message>>64)&((1<<(formated_message.bit_length()-64-8))-1)

def egcd(a, b):
    u1,u2,v1,v2 = 1,0,0,1
    if a<b:
        a, b = b, a
    while b!=0:
        q = a // b
        r = a % b
        a = b
        b = r
        v1, v2 = v2 - v1*q, v1
        u1, u2 = u2 - u1*q, u1
    return (a, u2, v2)

def square_roots(y, p, q):
    n = p*q
    s1 = pow(y, (p+1)//4, p)
    s2 = pow(y, (q+1)//4, q)
    #q > p from gen ordered primes
    u, v = egcd(q, p)[1:]
    return [
        (s2*u*p + s1*v*q)%n,
        (s2*u*p - s1*v*q)%n,
        (-s2*u*p + s1*v*q)%n,
        (-s2*u*p - s1*v*q)%n,
    ]

def Encrypt(message, public_key):
    message = Format(message, public_key['n'])
    y = (message*(message+public_key['b']))%public_key['n']
    c1 = ((message + public_key['b']*pow(2, -1, public_key['n']))%public_key['n'])&1
    c2 = jacobi(message + public_key['b']*pow(2, -1, public_key['n']), public_key['n'])
    return {
        "cipherText" : y,
        "parity": c1,
        "jacobiSymbol": c2
    }

def Decrypt(cypher, private_key):
    n = private_key["p"]*private_key["q"]
    if(cypher['cipherText']>n):
        print("[error] cipher > n")
        return
    tmp = ((cypher['cipherText'] + pow(private_key['b'], 2, n)*pow(4, -1, n))) #b**2 mod n
    tmp_sqrts = square_roots(tmp, private_key['p'], private_key['q'])
    match_by_parity =   [i for i in tmp_sqrts if i&1 == cypher['parity']]
    full_match = [i for i in match_by_parity if jacobi(i, n) == cypher['jacobiSymbol']][0]
    x = (-(private_key['b'] * pow(2, -1, n)) + full_match)%(n)
    return Unformat(x, n)

def Sign(message, private_key):
    n = private_key['p']*private_key['q']
    formated_message = Format(message, n)
    while(jacobi(formated_message, private_key['p']) != 1 or jacobi(formated_message, private_key['q']) != 1):
        formated_message = Format(message, n)
    return {
        "message":   message,
        "signature": square_roots(formated_message, private_key['p'], private_key['q'])[0]
    }

def Verify(message_with_signature, public_key):
    if(message_with_signature["message"]>public_key["n"] or message_with_signature["signature"]>public_key["n"]):
        print("[error] message > n or signature > n")
        return
    # print("[verification info] s**2%n = {}".format(hex(pow(
    #   message_with_signature["signature"],
    #   2,
    #   public_key["n"]
    # ))))
    return message_with_signature["message"] == Unformat(
        pow(
            message_with_signature["signature"],
            2,
            public_key["n"]
        ),
        public_key['n'])

if __name__ == '__main__':

    random.seed(a=10)

    key_length = 256
    # key_pair = GenerateKeyPair(*GenerateOrderedPrimes(key_length//2, 2))

    #testing encryption
    # message = 0x156234
    # encrypted = Encrypt(message, key_pair['public'])
    # decrypted = Decrypt(encrypted, key_pair['private'])

    # print(key_pair['public']['n'])
    # print("public modulus bit length = ", key_pair['public']['n'].bit_length())
    # print("p bit_length = {}, q bit_length = {}".format(
    #     key_pair['private']['p'].bit_length(),
    #     key_pair['private']['q'].bit_length()
    #     ))


    keys_factors = GenerateOrderedPrimes(key_length//2, 2) #sorted
#     #print(keys_factors)

#     # #3.Після генерування функція повинна повертати та/або зберігати секретний ключ ),
#     # #,(qpdта відкритий ключ ),(en. За допомогою цієї функції побудувати схеми RSA 
#     # #для абонентів Аі B–тобто, створити та зберегти для подальшого використання відкриті
#     # # ключі ),(ne, ),(11neтасекретні dі 1d.
    #Alice_keys = GenerateKeyPair(*keys_factors[2:4])
    Bob_keys = GenerateKeyPair(*keys_factors[0:2])

    print(f"keys   = {Bob_keys}")

    print("\n\t[1] checking encryption")
    messageFromAliceToBob = 0xdeadbeaf
    messageFromAliceToBob_encrypted = Encrypt(messageFromAliceToBob, Bob_keys["public"])
    messageFromAliceToBob_decrypted = Decrypt(messageFromAliceToBob_encrypted, Bob_keys["private"])
    print("alice sending message to bob:")
    print("message   = {}".format(messageFromAliceToBob))
    print("encrypted = {}".format(messageFromAliceToBob_encrypted))
    print("decrypted = {}".format(messageFromAliceToBob_decrypted))


    print("\n\t[2] checking signature")
    messageFromAlice = 0xdeadbeaf
    messagePresumablyFromAliceWithSignature = Sign(messageFromAlice, Bob_keys["private"])
    verificationIfMessageIsFromAlice = Verify(messagePresumablyFromAliceWithSignature, Bob_keys["public"])
    print("message   = {}\n\
signature = {}\n\
verified  = {}".format(
            messageFromAlice,
            messagePresumablyFromAliceWithSignature["signature"],
            verificationIfMessageIsFromAlice
        )
    )

    #print(int(334348411781048548478284142133132095699).bit_length())

    session = requests.Session()

    # # testing encryption
    # # local
    # print("Commencing local encryption/decryption testing")
    # terminate = False
    # for i in range(0, 20):
    #     if (terminate == True):
    #         break
    #     random.seed(a=i)
    #     key_length = 256
    #     key_pair = GenerateKeyPair(*GenerateOrderedPrimes(key_length//2, 2))
    #     #print("[encryption check]keys = ", key_pair)

    #     for j in range(0, 30):
    #         message = random.randint( 0, (1<<(key_length - 64 - 16))-1 )
    #         encrypted = Encrypt(message, key_pair['public'])
    #         decrypted = Decrypt(encrypted, key_pair['private'])

    #         if(message != decrypted):
    #             print("seed = {}, j = {}".format(i, j))
    #             terminate = True
    #             break

    # print("encryption/decryption testing testing with server")
    # #with server
    # #check our decryption
    # keys = GenerateKeyPair(*GenerateOrderedPrimes(key_length//2, 2))
    # message_to_be_encrypted_on_server = 52341234#bytes
    # encrypted_by_server = session.get(
    #   "http://asymcryptwebservice.appspot.com/rabin/encrypt?modulus={}&b={}&message={}&type=BYTES"
    #   .format(
    #       hex(keys["public"]["n"])[2:],
    #       hex(keys["public"]["b"])[2:],
    #       hex(message_to_be_encrypted_on_server)[2:] #string
    #       #"a0b0c0" #message - hex str        #bytes
    #   )
    # ).json()
    # encrypted_by_server['cipherText'] = int(encrypted_by_server['cipherText'], 16)
    # decrypted_by_us_what_was_encrypted_by_server = Decrypt(encrypted_by_server, keys["private"])
    # print("[encryption/decryption with server testing]\nmessage = {}\ndata encrypted on server = {}\ndecrypted = {}".format(
    #     message_to_be_encrypted_on_server,
    #     encrypted_by_server,
    #     decrypted_by_us_what_was_encrypted_by_server
    #     ))
   
    # # testing signature
    # # local
    # print("Commencing local signature/verification testing")
    # terminate = False
    # for i in range(0, 20):
    #     if (terminate == True):
    #         break
    #     random.seed(a=i)
    #     key_length = 256
    #     key_pair = GenerateKeyPair(*GenerateOrderedPrimes(key_length//2, 2))
    #     #print("[encryption check]keys = ", key_pair)

    #     for j in range(0, 30):
    #         message = random.randint( 0, (1<<(key_length - 64 - 16))-1 )
    #         signed = Sign(message, key_pair['private'])
    #         verification = Verify(signed, key_pair['public'])

    #         if(verification != True):
    #             print("seed = {}, j = {}".format(i, j))
    #             terminate = True
    #             break
    # print("End of local signature/verification testing ")

    # #with server
    # key_request = session.get("http://asymcryptwebservice.appspot.com/rabin/serverKey?keySize={}".format(key_length)).json()
    # message_to_be_signed_by_server = 5234643521#bytes
    # signed_by_server = session.get(
    #   "http://asymcryptwebservice.appspot.com/rabin/sign?message={}&type=BYTES"
    #   .format(
    #       hex(message_to_be_signed_by_server)[2:] #string
    #   )
    # ).json()
    # # print(key_request)
    # # print(signed_by_server)

    # verified_by_us = Verify(
    #     {
    #         'message'   : message_to_be_signed_by_server,
    #         'signature' : int(signed_by_server['signature'], 16)
    #     }, 
    #     {
    #         'n' : int(key_request['modulus'], 16),
    #         'b' : int(key_request['b'], 16)
    #     }
    # )
    # print("[signature/verification with server testing]\nmessage = {}\ndata signed on server = {}\n verified = {}".format(
    #     message_to_be_signed_by_server,
    #     signed_by_server,
    #     verified_by_us
    #     ))
   
    #overthrow
    n = int(session.get("http://asymcryptwebservice.appspot.com/znp/serverKey").json()['modulus'], 16)
    print(f"n = {n}")
    counter = 0
    while(True):
        counter += 1
        t = random.randint(2, n-1)
        t_square = pow(t, 2, n)
        z = int(session.get("http://asymcryptwebservice.appspot.com/znp/challenge?y={}".format(hex(t_square)[2:])).json()['root'], 16)
        print(f"\titeration #{counter}\nt   = {t}\nt^2 = {t_square}\nz   = {z}")
        if(t != z and t!=n-z):
            factor1 = egcd(n, (t+z)%n)[0]
            print(factor1)
            break
    print("iteration = {}\nn = {}\np = {}".format(counter, n, factor1))
    print("factor2 = ", n/factor1)
    print(n%factor1)

