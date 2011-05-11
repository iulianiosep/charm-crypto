from toolbox.ecgroup import *
from toolbox.PKSig import *

class ECDSA():
    def __init__(self, groupObj):
        global group
        group = groupObj
        
    def keygen(self, bits):
        group.paramgen(bits)
        x, g = group.random(), group.random(G)
        y = (g ** x)
        return ({'g':g, 'y':y}, x)
    
    def sign(self, pk, x, M):
        while True:
            k = group.random()
            r = group.zr(pk['g'] ** k)
            e = group.hash(M)
            s = (~k) * (e + x * r)
            if (r == 0 or s == 0):
                print ("unlikely error r = %s, s = %s" % (r,s))
                continue
            else:
                break
        return { 'r':r, 's':s }
        
    def verify(self, pk, sig, M):
        w = ~sig['s']
        u1 = group.hash(M) * w
        u2 = sig['r'] * w
        v = (pk['g'] ** u1) * (pk['y'] ** u2)
    
        if group.zr(v) == sig['r']:
            return True
        else:
            return False

if __name__ == "__main__":
    groupObj = ECGroup(409)
    ecdsa = ECDSA(groupObj)
    
    (pk, sk) = ecdsa.keygen(0)
    m = "hello world! this is a test message."

    sig = ecdsa.sign(pk, sk, m)
    if ecdsa.verify(pk, sig, m):
        print("Signature Verified!!!")
    else:
        print("Signature FAILED!!!")

