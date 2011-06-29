# A collection of encryption and signature padding schemes
import charm.cryptobase
import hashlib, math, struct
from bitstring import *
from SecureRandom import *
from weakrandom import WeakRandom

# OAEPEncryptionPadding
#
# Implements the OAEP padding scheme.  Appropriate for RSA-OAEP encryption.
# Implemented according to PKCS#1 v2.1 Section 7 ftp://ftp.rsasecurity.com/pub/pkcs/pkcs-1/pkcs-1v2-1.pdf

class OAEPEncryptionPadding:
    def __init__(self, _hash_type ='sha1'):
        self.hashFn = hashFunc(_hash_type)
        self.hashFnOutputBytes = len(hashlib.new(_hash_type).digest())
        global debug
        debug = False
        
    # outputBytes - the length in octets of the RSA modulus used
    #             - the intended length of the encoded message 
    # label = 'X'    
    def encode(self, message, emLen, label="", seed=None):
        # Skipped: label input length checking. (L must be less than 2^61 octets for SHA1)
        # First, make sure the message isn't too long.    
        hLen = self.hashFnOutputBytes
        if (len(message) > (emLen - (2 * hLen) - 2)):
            assert False, "message too long"
        
        lHash = self.hashFn(Bytes(label, 'utf-8'))  
              
        # Let PS be a string of length (emLen - mLen - 2hLen - 2) containing only zero octets.
        # Compute DB = lHash || PS || 0x01 || M.
        PS = Bytes.fill(b'\x00', emLen - len(message) - (2 * hLen) - 2)
        DB = lHash + PS + b'\x01' + bytes(message)
        
        # Generate a random octet string seed of length hLen and compute 
        # maskedDB = MGF1(seed, emLen - self.hashFnOutputBytes - 1)
        if (seed is None):
            rand = SecureRandomFactory.getInstance()
            seed = rand.getRandomBits(hLen)
            
        dbMask = MGF1(seed, len(DB), self.hashFn, hLen)
        maskedDB = DB ^ dbMask
        
        # Let seedMask = MGF(maskedDB, self.hashFnOutputBytes) and
        # maskedSeed = seedMask XOR seed
        seedMask = MGF1(maskedDB, len(seed), self.hashFn, hLen)        
        maskedSeed = seedMask ^ seed
        if(debug):
            print("Encoding")
            print("label    =>", label)
            print("lhash    =>", lHash)
            print("seed     =>", seed)
            print("db       =>", DB)
            print("db len   =>", len(DB))
            print("db mask  =>", dbMask)
            print("maskedDB =>", maskedDB)
            print("seedMask =>", seedMask)
            print("maskedSed=>", maskedSeed)
      
        return Bytes(b'\x00') + maskedSeed + maskedDB
    
    def decode(self, encMessage, label=""):
        hLen = self.hashFnOutputBytes
        # Make sure the encoded string is at least L bytes long
        if len(encMessage) < (2 * hLen + 2):
            assert False, "encoded string not long enough."
        lHash = self.hashFn(Bytes(label, 'utf-8'))
        
        # Parse the encoded string as (0x00 || maskedSeed || maskedDB)
        #Y = encMessage[0]
        maskedSeed = Bytes(encMessage[1:(1+hLen)])
        maskedDB = Bytes(encMessage[(1+hLen):])

        # Set seedMask = MGF1(maskedDB, hashFnOutputSize)
        seedMask = MGF1(maskedDB, len(maskedSeed), self.hashFn, hLen)
        seed = maskedSeed ^ seedMask           
        
        # Set dbMask = MGF(seed, k - hLen - 1) and
        #     DB = maskedDB \xor dbMask.
        dbMask = MGF1(seed, len(maskedDB), self.hashFn, hLen)
        DB = dbMask ^ maskedDB
        if(debug):
            print("decoding:")
            print("MaskedSeed => ", maskedSeed)
            print("maskedDB   => ", maskedDB)
            print("r seed =>", seed)
            print("r DB   =>", DB)
                
        # Parse DB as:
        #   DB = lHash' || PS || 0x01 || M.
        # Check that lHash' == lHash, Y == 0x00 and there is an 0x01 after PS
        lHashPrime = DB[0 : hLen]        
        M = DB[DB.find(b'\x01')+1 : ]
        return M

# MGF1 Mask Generation Function
#
# Implemented according to PKCS #1 specification, see appendix B.2.1:
# hLen is the output length of the hash functionA\x87\x0bZ\xb0)\xe6W\xd9WP\xb5L(<\x08r]\xbe\xa9
# maskBytes - the number of mask bytes to return
def MGF1(seed:Bytes, maskBytes:int, hashFn, hLen:int):
    debug = False
    # Skipped output size checking.  Must be less than 2^32 * hLen
    #result = b''.join([hashFn(struct.pack(">sI", seed, i)) for i in range(math.ceil(maskBytes / hashOutputBytes) - 1)])
    ran = range(math.ceil(maskBytes / hLen))
    if debug:
        print("calc =>", math.ceil(maskBytes / hLen))
        print("Range =>", ran)
    test = [hashFn(struct.pack(">%dsI" % (len(seed)), seed, i)) for i in ran]
    if debug: 
        print("test =>", test)
    result = b''.join(test)
    return Bytes(result[0:maskBytes])
    #diff = maskBytes - len(result)
    #result2 = result + Bytes.fill(b'\x00', diff)  #NOT CORRECT
    #return Bytes(result2)

class hashFunc:
    def __init__(self, _hash_type=None):
        if _hash_type == None:
            self.hashObj = hashlib.new('sha1')
        else:
            self.hashObj = hashlib.new(_hash_type)
        
    #message must be a binary string
    def __call__(self, message):
        h = self.hashObj.copy()
        h.update(bytes(message))
        return Bytes(h.digest())  
    
# PSSSignaturePadding
#
# Implements the PSS signature padding scheme.  Appropriate for RSA-PSS signing
# Implemented according to section 8 of PKCS1v2-1.pdf.
#
class PSSPadding:
    def __init__(self, _hash_type ='sha1'):
        self.hashFn = hashFunc(_hash_type)
        self.hLen = len(hashlib.new(_hash_type).digest())
        self.sLen = self.hLen # The length of the salt
        global debug
        debug = False
    
    def encode(self, M, emLen=None, salt=None):
        '''Encodes a message with PSS padding
        emLen will be set to the minimum allowed length if not explicitly set
        '''
        #Max length of output message
        if emLen is None:
            emBits =  8*self.hLen + 8 * self.sLen + 9
            emLen = math.ceil(emBits / 8)
        #Make sure the the message is long enough to be valid
        assert emLen >= self.hLen + self.sLen + 2, " Error"
        
        # assert len(M) < (2^61 -1), Message too long
        
        mHash = self.hashFn(M)
        
        if salt is None:
            if self.sLen > 0: 
                salt = SecureRandomFactory.getInstance().getRandomBits(self.sLen)
            else:
                salt = b''
        
        eightzerobytes = Bytes.fill(b'\x00', 8)
        Mprime = eightzerobytes + mHash + salt
        H = self.hashFn(Mprime)
        
        pslen = emLen - self.sLen - self.hLen - 2
        ps = Bytes.fill(b'\x00', pslen)        
        DB = ps + Bytes(b'\x01') + salt

        masklen = emLen - self.hLen - 1
        dbMask = MGF1(H, masklen, self.hashFn, self.hLen)  
        maskedDB = DB ^ dbMask
        
        # Set 8emLen - emBits bits of the left most octet in maskedDB to zero
        # This is not needed because we only pad byte aligned messages?
        
        EM = maskedDB + H + Bytes(b'\xbc')
        
        if debug:
            print("PSS Encoding:")
            print("M     =>", M) 
            print("mHash =>", mHash)
            print("salt  =>", salt)
            print("M'    =>", Mprime)
            print("H     =>", H)
            print("DB    =>", DB)
            print("dbmask=>", dbMask)
            print("masked=>", maskedDB)
            print("EM    =>", EM)
        return EM
    
    def verify(self, M, EM):
        '''
        Verifies that EM is a correct encoding for M
        M - the message to verify
        EM - the encoded message
        return true or false
        '''
        if debug: print("PSS Decoding:")
            
        emLen = len(EM) 
        # assert len(M) < (2^61 -1), Message too long
        mHash = self.hashFn(M)
        if emLen < self.hLen + self.sLen + 2:
            if debug: print("emLen too short") 
            return False
        
        if EM[len(EM)-1:] != b'\xbc':
            if debug: print("0xbc not found") 
            return False
        
        maskeDBlen = emLen - self.hLen - 1
        maskedDB = Bytes(EM[:maskeDBlen])
        H = EM[maskeDBlen:maskeDBlen+self.hLen]
        
        #if the leftmost 8emLen - emBits of the leftmost octet in maskedDB are not equal to zero return false
        
        masklen = emLen - self.hLen - 1
        dbMask = MGF1(H, masklen, self.hashFn, self.hLen)
        DB = maskedDB ^ dbMask
        #Set the leftmost 8emLen - emBits of the leftmost octet in DB to zero
        
        zerolen = emLen - self.hLen - self.sLen - 2
        if DB[:zerolen] != Bytes.fill(b'\x00', zerolen):
            if debug: print("DB did not start with % zero octets" % zerolen) 
            return False
        
        if DB[zerolen] != 0x01:
            if debug: print("DB did not have 0x01") 
            return False
        
        salt = DB[len(DB)-self.sLen:]
        mPrime = Bytes.fill(b'\x00', 8) + mHash + salt
        HPrime = self.hashFn(mPrime)
        
        if debug:
            print("M     =>", M) 
            print("mHash =>", mHash)
            print("salt  =>", salt)
            print("M'    =>", mPrime)
            print("H     =>", H)
            print("DB    =>", DB)
            print("dbmask=>", dbMask)
            print("masked=>", maskedDB)
            print("EM    =>", EM)
        
        return H == HPrime
