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

#0.В якості датчика випадкових чисел треба використовувати один з генераторів
#практикуму No1, що показав гарні статистичні властивост
#generates gen_len bits

def random_gen_from_lab1(state, gen_len):
    frequencies = [0]*256
    #random.seed(a = state, version=2)
    bit_sequence = random.getrandbits(gen_len)
    hex_sequence = hex(bit_sequence)
    count = 0
    while bit_sequence>0:
        frequencies[bit_sequence&0xff] += 1
        bit_sequence = bit_sequence>>8
    return (hex_sequence[2:], frequencies, gen_len//8)

#1.функцію пошукувипадкового простого числа з заданого 
#інтервалуабо заданої  довжини,  використовуючи  датчик  
#випадкових  чисел  татестиперевірки  на простоту

def find_prime(bit_length, first_primes, exclude = [], bases_to_check = 10):


    random_vals_generated = [] #[debug] value

    #when first choose by random, check if random_val has desireble bit_length
    random_val = int(random_gen_from_lab1(None, bit_length)[0], 16) # = x
    if random_val.bit_length() != bit_length:
        random_val ^= (1<<(bit_length-1))

    #print("bitlength of random val {}".format(random_val.bit_length()))
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
        
        #make it odd if its not
        random_val += (~(random_val&1))&1 # = m0
        
        upper_bound = 1<<(bit_length+shift_bound-1)

        r_precomputed = gen_r_array_precomputation(first_primes[1:], random_val.bit_length())

        for test_subject in range(random_val, upper_bound, 2):
            is_prime = True
            prime_witnesses = []
            

            
            # print("first prims len = {}, r_precoputed len dim1 = {} dim2 = {}, test_subject.bitlen = {}bound.bitlen={},test_subj = {}, bound = {}".format(
            #   len(first_primes),
            #   len(r_precomputed),
            #   len(r_precomputed[0]),
            #   test_subject.bit_length(),
            #   upper_bound.bit_length(),
            #   hex(test_subject),
            #   hex(upper_bound)
            # ))

            #check with trial division by Pascal
            #check primes m = [3, 5, 7 ...], exclude 2 from list of first primes
            #r_precomputed[i-1] !!! while first_primes[i]
            for i in range(1, len(first_primes)):
                N = 0
                for k in range(0, test_subject.bit_length()):
                    #print("{} {}".format(i, k))
                    #print("i={},k={}".format(i,k))
                    N = (N + ((test_subject>>k)&1) * r_precomputed[i-1][k])%first_primes[i]
                    #print(N, end = ", ")
                #print(N, random_val)
                if N == 0:
                    #print("{} discarded on trial".format(test_subject))
                    is_prime = False #is composite 
                    break
            if is_prime == False:
                print(f"[composite]{test_subject}")
                #print("{} discarded on trial".format(test_subject))
                continue
            #print("after trial division")

            #check with miller rabin
            d = test_subject-1
            s = 0
            while True:
                if d & 1 == 1:
                    break
                d >>= 1
                s += 1
            #print("s = {}, d = {}".format(s, d))
            for i in range(bases_to_check):
                is_prime = False
                base = random.randint(2, test_subject-1)
                #print("base[{}] = {}".format(i, base))
                if gcd(base, test_subject) != 1:
                    is_prime = False
                    print(f"[composite]{test_subject}")
                    break #is composite
                tmp = pow(base, d, test_subject)
                #print("x**d = {}".format(tmp))
                if tmp == 1 or tmp == test_subject-1: #is prime
                    #print("passed 1 base")
                    prime_witnesses.append(i)
                    continue
                for r in range(1, s):
                    tmp = (tmp**2)%test_subject # optimize ?
                    #print("x**(d*2**{}) = {}".format(r, tmp))
                    if tmp == test_subject - 1:# is prime
                        #print("passed 1 base {}".format())
                        is_prime = True
                        break
                    if tmp == 1:# is composite
                        is_prime = False
                        print(f"[composite]{test_subject}")
                        break
                if is_prime == True: #append prime witnesses, go for next base
                    prime_witnesses.append(i)
                    #print("{} pseudoprime by base {}".format(test_subject, base))
                else:                #test_subject is composite, go for next subject
                    print(f"[composite]{test_subject}")
                    #print("{} not psudoprime by base {}".format(test_subject, base))
                    break
            
            #print("val = {}, prime_witnesses ={}".format(random_val,prime_witnesses))
            #if all bases are prime witnesses -> test_subject is prime
            #print("{} end loop with wintesses {}".format(test_subject, prime_witnesses))
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

#3. Написати функцію генерації ключових пар для RSA.
def GenerateKeyPair(p, q):
    phi = (p-1)*(q-1)
    e = random.randrange(2, phi-1)
    #print("[debug]q={},p={},phi={},e={}".format(q, p, phi, e))
    while gcd(e, phi) != 1:
        e = random.randrange(2, phi-1)
    #print("[debug]calculating inverse")
    d = pow(e, -1, phi)
    #print("[debug]d = {}".format(d))
    #print("[debug]should be 1 {}".format((d*e)%phi))
    return {
        "private": {
            "p" : p,
            "q" : q,
            "d" : d,
        },
        "public" : {
            "n" : p*q,
            "e" : e
        }
    }

#4.Написати  програму  шифрування,  розшифрування  і  створення  повідомлення
#з цифровим підписом для абонентів Аі B. Кожна з операцій 
#(шифрування, розшифрування, створення  цифрового  підпису,
#перевірка  цифрового  підпису)  повинна  бути  реалізована окремою  
#процедурою,  на  вхід  до  якої  повинні  подаватись  лише  ті  ключові  дані,
#які необхідні для її виконання.

def Encrypt(message, public_key):
    if(message>public_key["n"]):
        print("[error] message > n")
        return
    return pow(message, public_key["e"], public_key["n"])

def Decrypt(cypher, private_key):
    if(cypher>private_key["p"]*private_key["q"]):
        print("[error] cipher > n")
        return
    return pow(cypher, private_key["d"], private_key["p"]*private_key["q"])

def Sign(message, private_key):
    if(message>private_key["p"]*private_key["q"]):
        print("[error] cipher > n")
        return
    return {
        "message":   message,
        "signature": pow(message, private_key["d"], private_key["p"]*private_key["q"])
    }

def Verify(message_with_signature, public_key):
    if(message_with_signature["message"]>public_key["n"] or message_with_signature["signature"]>public_key["n"]):
        print("[error] message > n or signature > n")
        return
    # print("[verification info] S**e % n = {}".format(pow(
    #   message_with_signature["signature"],
    #   public_key["e"],
    #   public_key["n"]
    # )))
    return message_with_signature["message"] == pow(
        message_with_signature["signature"],
        public_key["e"],
        public_key["n"]
    )

#5.За  допомогою  раніше  написаних  на  попередніх  етапах  програм  організувати
#роботу протоколу конфіденційного розсилання ключів з підтвердженням справжності 
#по відкритому каналу за допомогою алгоритму RSA.

def SendKey(message, private_key_sender, public_key_recepient):
    if private_key_sender["p"]*private_key_sender["q"] > public_key_recepient["n"]:
        print("[error] sender public modulus should be smaller than receivers, honorable sender regenerate your key pair please")
        return
    return {
        "k1": Encrypt(message, public_key_recepient),
        "S1": Encrypt(Decrypt(message, private_key_sender), public_key_recepient)
    }

def ReceiveKey(message_with_authentication, public_key_sender, private_key_recepient):
    # if public_key_sender["n"] > private_key_recepient["p"]*private_key_recepient["q"]:
    #     print("[error] sender public modulus should be smaller than receivers, tell honorable sender to regenerate key pair")
    #     return
    k = Decrypt(message_with_authentication["k1"], private_key_recepient)
    S = Decrypt(message_with_authentication["S1"], private_key_recepient)
    authenticated = k == Encrypt(S, public_key_sender)
    return {
        "k": k,
        "authenticated": authenticated
    }

import sys
if __name__ == '__main__':

#     # #------------------------------------------------CHECKING LOCALY----------------
    random.seed(0)
    print("\t\tLOCAL CHECK")
    #2. За  допомогою  цієї функціїзгенерувати  дві  пари
    #простих  чисел qp,і 11,qpдовжини щонайменше 256 біт.
    RSA_bit_length_local_check = 256
    keys_factors = GenerateOrderedPrimes(RSA_bit_length_local_check//2, 4) #sorted
#     #print(keys_factors)

#     # #3.Після генерування функція повинна повертати та/або зберігати секретний ключ ),
#     # #,(qpdта відкритий ключ ),(en. За допомогою цієї функції побудувати схеми RSA 
#     # #для абонентів Аі B–тобто, створити та зберегти для подальшого використання відкриті
#     # # ключі ),(ne, ),(11neтасекретні dі 1d.
    Alice_keys = GenerateKeyPair(*keys_factors[2:4])
    Bob_keys = GenerateKeyPair(*keys_factors[0:2])

    print(f"Alice keys = {Alice_keys}")
    print(f"Bob keys   = {Bob_keys}")

    print("\n\t[1] checking encryption")
    #alice to bob
    messageFromAliceToBob = random.randint(0, Bob_keys["public"]["n"]-1)
    messageFromAliceToBob_encrypted = Encrypt(messageFromAliceToBob, Bob_keys["public"])
    messageFromAliceToBob_decrypted = Decrypt(messageFromAliceToBob_encrypted, Bob_keys["private"])
    print("alice sending message to bob:")
    print("message   = {}".format(messageFromAliceToBob))
    print("encrypted = {}".format(messageFromAliceToBob_encrypted))
    print("decrypted = {}".format(messageFromAliceToBob_decrypted))
#     #bob to alice
#     messageFromBobToAlice = random.randint(0, Alice_keys["public"]["n"]-1)
#     messageFromBobToAlice_encrypted = Encrypt(messageFromBobToAlice, Alice_keys["public"])
#     messageFromBobToAlice_decrypted = Decrypt(messageFromBobToAlice_encrypted, Alice_keys["private"])
#     print("bob sending message to alice:")
#     print("message   = {}".format(messageFromBobToAlice))
#     print("encrypted = {}".format(messageFromBobToAlice_encrypted))
#     print("decrypted = {}".format(messageFromBobToAlice_decrypted))

    print("\n\t[2] checking signature")
    #alice signs, bob verifies
    print("Alice signs, Bob verifies")
    messageFromAlice = random.randint(2, Alice_keys["public"]["n"]-1)
    messagePresumablyFromAliceWithSignature = Sign(messageFromAlice, Alice_keys["private"])
    verificationIfMessageIsFromAlice = Verify(messagePresumablyFromAliceWithSignature, Alice_keys["public"])
    print("message from Alice = {}\n\
signature          = {}\n\
verified           = {}".format(
            messageFromAlice,
            messagePresumablyFromAliceWithSignature["signature"],
            verificationIfMessageIsFromAlice
        )
    )

#     #bob signs, alice verifies
#     print("Bob signs, Alice verifies")
#     messageFromBob = random.randint(2, Bob_keys["public"]["n"])
#     messagePresumablyFromBobWithSignature = Sign(messageFromBob, Bob_keys["private"])
#     verificationIfMessageIsFromBob = Verify(messagePresumablyFromBobWithSignature, Bob_keys["public"])
#     print("message from Bob   = {}\n\
# signature          = {}\n\
# verified           = {}".format(
#             messageFromBob,
#             messagePresumablyFromBobWithSignature["signature"],
#             verificationIfMessageIsFromBob
#         )
#     )

    #alice sends key to bob, bob receives
    print("\n\t[3] secret key distribution protocol scheme with authentification") 

    #k should be < n
    k = random.randint(1, Alice_keys['public']['n']-1)
    alice_to_bob_sends = SendKey(k, Alice_keys['private'], Bob_keys['public'])
    
    #if sender n > receiver n -> make senders key with bit_length(receiver_key)-1:
    if alice_to_bob_sends is None:
        Alice_keys = GenerateKeyPair(*GenerateOrderedPrimes(RSA_bit_length_local_check//2-1, 2))
        k = random.randint(1, Alice_keys['public']['n']-1)
        alice_to_bob_sends = SendKey(k, Alice_keys['private'], Bob_keys['public'])
        
    print("sent from sender = {}".format(alice_to_bob_sends))
    bob_from_alice_receives = ReceiveKey(alice_to_bob_sends, Alice_keys['public'], Bob_keys['private'])
    print("computed by receiver = {}".format(bob_from_alice_receives))

#     # #------------------------------------------------CHECKING WITH http://asymcryptwebservice.appspot.com/ ----------------

#     # #IMPORTANT:
#     # # string messages should be shorter, so stringToInt(str_message)<modulus
#     # # if stringToInt(str_message)>modulus returns NONE

#     print("\n\t\tREMOTE CHECK\n")

#     #initializing session

#     check_bit_length = 512
#     session = requests.Session()
#     key_request = session.get("http://asymcryptwebservice.appspot.com/rsa/serverKey?keySize={}".format(check_bit_length))
#     public_key_from_server = key_request.json()

#     #encrypting data on server, decrypting here

#     keys = GenerateKeyPair(*GenerateOrderedPrimes(check_bit_length//2, 2))
#     #message_to_be_encrypted_on_server = stringToInt("Hello test 666 adf;,2")#string
#     message_to_be_encrypted_on_server = 0xdeadbeaf#bytes
#     encrypted_by_server = session.get(
#       "http://asymcryptwebservice.appspot.com/rsa/encrypt?modulus={}&publicExponent={}&message={}&type=BYTES"
#       .format(
#           hex(keys["public"]["n"])[2:],
#           hex(keys["public"]["e"])[2:],
#           hex(message_to_be_encrypted_on_server)[2:] #string
#           #"a0b0c0" #message - hex str        #bytes
#       )
#     ).json()['cipherText']
#     decrypted_by_us_what_was_encrypted_by_server = Decrypt(int(encrypted_by_server,16), keys["private"])
#     #print("[decrypt check] encrypted on server, decrypted here = {}".format(intToString(decrypted_by_us_what_was_encrypted_by_server)))   #string
#     print("[decrypt check] encrypted on server, decrypted here = {}".format(hex(decrypted_by_us_what_was_encrypted_by_server)))        #bytes
    
#     #encrypting data here , decrypting on server

#     encrypted_by_us = Encrypt(
#       stringToInt("Hello test 228 adfadf515115;.!`"),
#       {
#           "n": int(public_key_from_server["modulus"], 16),
#           "e": int(public_key_from_server["publicExponent"], 16)
#       }
#     )
#     decrypted_by_server_what_was_encrypted_by_us = session.get(
#       "http://asymcryptwebservice.appspot.com/rsa/decrypt?cipherText={}&expectedType=BYTES".format(
#           hex(encrypted_by_us)[2:]
#       )
#     ).json()['message']
#     print("[encrypt check] encrypted here, decrypted on server = {}".format(intToString(int(decrypted_by_server_what_was_encrypted_by_us, 16))))#string
#     # print(hex(decrypted_by_server_what_was_encrypted_by_us)[2:])                #bytes

#     #signing data here, verifying on server

#     keys = GenerateKeyPair(*GenerateOrderedPrimes(check_bit_length//2, 2))
#     signed_by_us = Sign(
#       stringToInt("Hello i'm here to test singature"),
#       keys["private"]
#     )
#     verified_by_server_what_was_signed_by_us = session.get(
#       "http://asymcryptwebservice.appspot.com/rsa/verify",
#       params = {
#           "modulus":          hex(keys["public"]["n"])[2:],
#           "publicExponent":   hex(keys["public"]["e"])[2:],
#           "message":          hex(signed_by_us["message"])[2:],
#           "signature":        hex(signed_by_us["signature"])[2:],
#           "type":             "BYTES"
#       }
#     ).json()["verified"]
#     print("[signature check] signed here, verified on server = {}".format(verified_by_server_what_was_signed_by_us))

#     #signing on server, verifying here

#     message_to_be_signed_by_server = stringToInt("testing verification now")
#     signature_by_server = session.get(
#       "http://asymcryptwebservice.appspot.com/rsa/sign",
#       params = {
#           "message":      hex(message_to_be_signed_by_server)[2:],
#           "type":         "BYTES"
#       }
#     ).json()["signature"]
#     verified_by_us_what_was_signed_on_server = Verify(
#       {
#           "message":      message_to_be_signed_by_server,
#           "signature":    int(signature_by_server,16)
#       },
#       {
#           "n": int(public_key_from_server["modulus"], 16),
#           "e": int(public_key_from_server["publicExponent"], 16)
#       }
#     )
#     print("[verify check] signed on server, verified here = {}".format(verified_by_us_what_was_signed_on_server))

#     #sending to server

#     keys = GenerateKeyPair(*GenerateOrderedPrimes(check_bit_length//2, 2))
#     sent_to_server = SendKey(
#         15293487239452,
#         keys["private"],
#         {
#           "n": int(public_key_from_server["modulus"], 16),
#           "e": int(public_key_from_server["publicExponent"], 16)
#         }
#     )
#     if sent_to_server is None:
#         keys = GenerateKeyPair(*GenerateOrderedPrimes(check_bit_length//2 - 1, 2))
#         sent_to_server = SendKey(
#             15293487239452,
#             keys["private"],
#             {
#               "n": int(public_key_from_server["modulus"], 16),
#               "e": int(public_key_from_server["publicExponent"], 16)
#             }
#         )
#     response_from_server = session.get(
#         "http://asymcryptwebservice.appspot.com/rsa/receiveKey",
#         params = {
#             "key":              hex(sent_to_server["k1"])[2:],
#             "signature":        hex(sent_to_server["S1"])[2:],
#             "modulus":          hex(keys["public"]["n"])[2:],
#             "publicExponent":   hex(keys["public"]["e"])[2:],
#         }
#     ).json()
#     print("[sendKey check] response from server after receiving our data = {}".format(response_from_server))
    
#     #receiving from server
    
#     received_from_server = session.get(
#         "http://asymcryptwebservice.appspot.com/rsa/sendKey",
#         params = {
#             "modulus":          hex(keys["public"]["n"])[2:],
#             "publicExponent":   hex(keys["public"]["e"])[2:]
#         }
#     ).json()
#     decrypted_from_server = ReceiveKey(
#         {#received from server data
#             "k1": int(received_from_server["key"], 16),
#             "S1": int(received_from_server["signature"], 16),
#         }, 
#         {#public key of server
#           "n": int(public_key_from_server["modulus"], 16),
#           "e": int(public_key_from_server["publicExponent"], 16)
#         },
#         keys["private"]
#     )
#     print("[receiveKey check] processed data sent from server = {}".format(decrypted_from_server))

#     #to do prepare(set up functions) for interactive check
#     print("\n\t\tINTERACTIVE CHECK\n")
#     encrypted_by_us = Encrypt(
#       stringToInt("qwertyFFFFasg"),
#       {
#           "n": 0x8A97AD31A7A4465E09F721929965A637646A4B40F3A769AAB8D36243C336C0D1,
#           "e": 0x10001
#       }
#     )
#     decrypted_by_server_what_was_encrypted_by_us = requests.get(
#       "http://asymcryptwebservice.appspot.com/rsa/decrypt?cipherText={}&expectedType=BYTES".format(
#           hex(encrypted_by_us)[2:]
#       ),
#       cookies = {'JSESSIONID': 'cqujC4pqpvGsa_FP_OYKLA'}
#     ).json()['message']
#     print("[interactive check] encrypted here, decrypted on server = {}".format(intToString(int(decrypted_by_server_what_was_encrypted_by_us, 16))))#string

#     