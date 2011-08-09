''' 
Hohenberger-Waters Chameleon Hash (RSA-based)
based on the scheme of Ateneise and de Medeiros
 
 | From: "S. Hohenberger, B. Waters. Realizing Hash-and-Sign Signatures under Standard Assumptions", Appendix A.
 | Published in: Eurocrypt 2009
 | Available from: http://eprint.iacr.org/2009/028.pdf
 | Notes: 

 * type:       hash function (chameleon)
 * setting:      RSA
 * assumption:   RSA

:Author:    Matthew Green
:Date:      1/2011
'''

from toolbox.Hash import *
from toolbox.integergroup import *

class RSA_HW09(ChamHash):
    def __init__(self):
        global group
        group = IntegerGroupQ(0)
    
    def paramgen(self, secparam, p = 0, q = 0):
        # If we're given p, q, compute N = p*q.  Otherwise select random p, q
        if p != 0 and q != 0:
            N = p * q
        else:
            group.paramgen(secparam)
            p, q = group.p, group.q
            N = p * q
        
        phi_N = (p-1)*(q-1)
        J = group.random(N)
        e = group.random(phi_N)
        while (not gcd(e, phi_N) == 1):
            e = group.random(phi_N)
        pk = { 'secparam': secparam, 'N': N, 'J': J, 'e': e }
        sk = { 'p': p, 'q': q }
        return (pk, sk)
          
    def hash(self, pk, message, r = 0):
        N, J, e = pk['N'], pk['J'], pk['e']
        if r == 0:
           r = group.random(N)
       
        print("Message =>", message)    
        msg_int = 0
        # iterate over bits?
        for b in message:
            msg_int = msg_int << 8
            msg_int += ord(b)
            h = (J ** msg_int) * (r ** e)
        return (h, r)

if __name__ == "__main__":    
    chamHash = RSA_HW09()
    
    (pk, sk) = chamHash.paramgen(1024)
    
    msg = 12345678
    c = chamHash.hash(pk, msg)
    
    print("sig =>", c)