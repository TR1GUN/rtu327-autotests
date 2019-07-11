import struct

class Crc16:
    xorPolynom = 0xA001
    
    def __init__(self, *args):
        return super().__init__(*args)

    def CalcCrc16Poly(self, buf, length, crc):
        for b in buf:
            crc = self.UpdCrc16Poly (crc, b)
        return crc

    def UpdCrc16Poly(self, crc, b):
        crc ^= b
        for x in range(0, 8):            
            if (crc & 1):
                crc = ( crc >> 1) ^ self.xorPolynom
            else: 
                crc = ( crc >> 1)
        return crc

    def swap(self, crc):
        return crc.to_bytes(2,'little')

    def makeCRC16(self, buf, initPolynom = 0x40BF): #0x40BF for UM-RTU, 0xFFFF for anything else        
        if type(buf) is str:
            buf = buf.encode("utf-8")
        Crc = self.CalcCrc16Poly(buf,len(buf), initPolynom) 
        return self.swap(Crc)    
        
    

    