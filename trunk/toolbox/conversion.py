'''
:Date: Jul 5, 2011
:Authors: Gary Belvin

This class facilitates conversion between domain spaces
'''
from charm.integer import *
import charm.integer
from toolbox.bitstring import Bytes
import math

# define dict of conversion possibilities
conversion_types = {'byte2str':Conversion.byte2str, 'byte2intE':Conversion.bytes2integer, 'byte2pairE':None, 'byte2eccE':3 
          ,'str2byte':Conversion.str2bytes,'str2intE':4, 'str2pairE':None, 'str2eccE':None }

class Conversion(object):
    '''
    The goal is to convert arbitrarily between any of the following types
    
    Input types:
    
    * bytes
    * Bytes
    * int
    * Integer Element
    * Modular Integer Element
    
    Output types:
    
    * int
    * Group element
    * Integer element
    * Integer element mod N
    '''
    
    @classmethod
    def convert(self, source, target):
        return source
    
    @classmethod
    def bytes2element(self, bytestr):
        '''Converts a byte string to a group element'''
        pass
   
    @classmethod
    def bytes2integer(self, bytestr):
        '''Converts a bytes string to an int of a particular bit-length?'''
        return integer(bytestr)
   
    @classmethod
    def str2bytes(self, strobj):
        return Bytes(strobj, 'utf-8')
    
    @classmethod
    def byte2str(self, byteobj):
        return Bytes.decode(byteobj, 'utf-8')
     
    @classmethod    
    def OS2IP(self, bytestr, element = False):
        '''
        :Return: A python ``int`` if element is False. An ``integer.Element`` if element is True
        
        Converts a byte string to an integer
        '''
        
        val = 0 
        for i in range(len(bytestr)):
            val += bytestr[len(bytestr)-1-i] << (8 *i)
        #These lines convert val into a binary string of 1's and 0's 
        #bstr = bin(val)[2:]   #cut out the 0b header
        #val = int(bstr, 2)
        
        #return val
        if element:
            return integer(val)
        else:
            return val
    
    @classmethod    
    def IP2OS(self, number, xLen=None):
        '''
        :Parameters:
          - ``number``: is a normal integer, not modular
          - ``xLen``: is the intended length of the resulting octet string
        
        Converts an integer into a byte string'''
        
        ba = bytearray()
        
        if xLen == None:
            xLen = math.ceil(math.log(number, 2) / 8)
        

        if type(number) == integer:
            x = int(number)
        elif type(number) == int:
            x = number
        
        for i in range(xLen):
            ba.append(x % 256)
            x = x >> 8
        ba.reverse()
        return Bytes(ba)