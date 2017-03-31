#!/usr/bin/python
import linuxcnc, hal, time, comms
import struct, traceback, datetime
from pprint import pprint

vfd = hal.component("vfd")
vfd.newpin("spdvfd.drivestatus", hal.HAL_U32, hal.HAL_OUT)
vfd.newpin("spdvfd.commfrequency", hal.HAL_FLOAT, hal.HAL_OUT)
vfd.newpin("spdvfd.outfrequency", hal.HAL_FLOAT, hal.HAL_OUT)
vfd.newpin("spdvfd.outrpm", hal.HAL_FLOAT, hal.HAL_OUT)
vfd.newpin("spdvfd.outcurrent", hal.HAL_FLOAT, hal.HAL_OUT)
vfd.newpin("spdvfd.outvoltage", hal.HAL_FLOAT, hal.HAL_OUT)
vfd.newpin("spdvfd.power", hal.HAL_FLOAT, hal.HAL_OUT)
vfd.newpin("spdvfd.runtime", hal.HAL_FLOAT, hal.HAL_OUT)
vfd.newpin("spdvfd.powerontime", hal.HAL_FLOAT, hal.HAL_OUT)

vfd.newpin("spdvfd.atfreq", hal.HAL_BIT, hal.HAL_OUT)

vfd.newpin("spdvfd.run", hal.HAL_BIT, hal.HAL_IN)
vfd.newpin("spdvfd.forward", hal.HAL_BIT, hal.HAL_IN)
vfd.newpin("spdvfd.rpmset", hal.HAL_FLOAT, hal.HAL_IN)

vfd.ready()

#baudate 9600bps, byte size 8, parity none, stop bits 2, timeout 0.2s
baudrate = 9600
bytesize = 8
parity = comms.serial.PARITY_NONE
stopbits = 1
timeout = 0.2
port = '/dev/ttyUSB0'

#spindle vfd has slave id 1
serialvfd1 = comms.Instrument(port, 1)
#serialvfd1.debug = True
serialvfd1.serial.baudrate = baudrate
serialvfd1.serial.bytesize = bytesize
serialvfd1.serial.parity   = parity
serialvfd1.serial.stopbits = stopbits
serialvfd1.serial.timeout  = timeout
#serialvfd1.mode = comms.MODE_ASCII
serialvfd1.mode = comms.MODE_RTU

#initialize variables to safe settings
vfd['spdvfd.run'] = 0
vfd['spdvfd.forward'] = 1
vfd['spdvfd.rpmset'] = 500

#with open("/tmp/vfd_hal",'a') as f:
#    f.write("hey !"+"\n")
#    f.write(str(vfd['spdvfd.run'])+"\n")
#    f.flush()

def main():
    while 1:
        #with open("/tmp/vfd_hal",'a') as f:
        #    f.write(str(datetime.datetime.now()))
        #    for item in ["spdvfd.run", "spdvfd.forward", "spdvfd.rpmset", "spdvfd.atfreq"]:
        #        f.write("\t"+item+": "+ str(vfd[item]))
        #    f.write("\n")
        #    f.flush()
        
        #time.sleep(0.01)
        #-----------------SPINDLE VFD--------------------
        readparamA = []
        #responseA=serialvfd1._performCommand(3, "none")
        ### Test
        #responseA=serialvfd1._performCommand(3, struct.pack('>BBBB', 0x01,0x02,0x03,0x04))
        
        ### stop 
        #responseA=serialvfd1._performCommand(0x10, struct.pack('>HHBHH', 0x900,0x02,0x04,0,40000))

        ### start 400
        #responseA=serialvfd1._performCommand(0x10, struct.pack('>HHBHH', 0x900,0x02,0x04,1,40000))

        ### start
        #responseA=serialvfd1._performCommand(0x10, struct.pack('>HHBH', 0x900,0x01,0x02,0))

        ### Set freq to 4Hz
        #responseA=serialvfd1._performCommand(0x10, struct.pack('>HHBH', 0x901,0x01,0x02,400))

        ### Read
        responseA = ""
        resp = ""
        try:
            resp = serialvfd1._performCommand(0x03, struct.pack('>HH', 0x500,0x06))
            
            vfd['spdvfd.commfrequency'] = ord(resp[3])*256 + ord(resp[4]) 
            vfd['spdvfd.outfrequency'] = ord(resp[5])*256 + ord(resp[6])
            vfd['spdvfd.outcurrent'] = (ord(resp[7])*256 + ord(resp[8])) / 10.0
            vfd['spdvfd.outvoltage'] = (ord(resp[9])*256 + ord(resp[10])) / 10.0
            
            vfd['spdvfd.outrpm'] = vfd['spdvfd.outfrequency'] * 240.0/400
            vfd['spdvfd.atfreq'] = vfd['spdvfd.commfrequency'] == vfd['spdvfd.outfrequency']

           
            print " ".join("%.2x"%ord(n) for n in resp)
            #with open("/tmp/vfd_hal.read",'a') as f:
            #    f.write(str(datetime.datetime.now())+" ")
            #    f.write(" ".join("%.2x"%ord(n) for n in message))
            #    f.write("\n")
            #    f.flush()
        except KeyboardInterrupt:
            raise SystemExit
        except:
            pass

        for i in xrange(0,len(responseA)/8):
            readparamA.append(responseA[i*8+2:8*i+8+2])
        #print readparamA
        #vfd['spdvfd.outfrequency'] = float(readparamA[0])/10000
        #vfd['spdvfd.outcurrent'] = float(readparamA[1])/1000
        #vfd['spdvfd.drivestatus'] = int(readparamA[2])
        #vfd['spdvfd.outtorque'] = int(readparamA[7])/100
        #vfd['spdvfd.outvoltage'] = float(readparamA[8])/1000
        #vfd['spdvfd.power'] = float(readparamA[9])/1000
        #vfd['spdvfd.runtime'] = int(readparamA[11])
        #vfd['spdvfd.powerontime'] = int(readparamA[12])
        #vfd['spdvfd.commfrequency'] = float(serialvfd1._performCommand(6, "F001"))/100


        fct = None
        payload = ""
        
        #start/stop/cw/ccw
        if vfd['spdvfd.run'] and vfd['spdvfd.forward']: #run CW
            fct = 0x10
            payload = struct.pack('>HHBH', 0x900,0x01,0x02,1)
        elif vfd['spdvfd.run'] and not vfd['spdvfd.forward']: #run CCW
            fct = 0x10
            payload = struct.pack('>HHBH', 0x900,0x01,0x02,3)
        else: #do not run. keep resending this for safety.
            fct = 0x10
            payload = struct.pack('>HHBH', 0x900,0x01,0x02,0)

        if fct != None:
            try:
                _vfd_do(fct, payload)
            except KeyboardInterrupt:
                raise SystemExit
            except Exception, e:
                with open("/tmp/vfd_hal",'a') as f:
                    f.write(str(datetime.datetime.now()))
                    f.write(" Error while writing: fct: %.2x\t payload:%s\n%s\n"%(fct,payload,traceback.format_exc()))
                    f.flush()

        #set the frequency
        if vfd['spdvfd.rpmset'] > 24000:
            vfd['spdvfd.rpmset'] = 24000
        freqset = int(vfd['spdvfd.rpmset'])*400.0/24000
        if ('%.2f'%vfd['spdvfd.commfrequency']) != ('%.2f'%freqset):
            _vfd_do(0x10, struct.pack('>HHBH', 0x901,0x01,0x02,min((freqset*100),400*100)))

def _vfd_do(fct,payload):
    while True:
        try:
            return serialvfd1._performCommand(fct,payload)
        except KeyboardInterrupt:
            raise SystemExit
        except:
            with open("/tmp/vfd_hal",'a') as f:
                f.write(str(datetime.datetime.now()))
                f.write(" Error while writing: fct: %.2x\t payload:%s\n%s\n"%(fct,payload,traceback.format_exc()))
                f.flush()
        
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit
else:
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit
