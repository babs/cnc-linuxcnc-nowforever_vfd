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
# P056 => 2 (dft)
#baudrate = 9600
# P056 => 4
baudrate = 38400
bytesize = 8
parity = comms.serial.PARITY_NONE
stopbits = 1
timeout = 0.2
port = '/dev/ttyUSB0'

#spindle vfd has subordinate id 1
serialvfd1 = comms.Instrument(port, 1)
#serialvfd1.debug = True
serialvfd1.serial.baudrate = baudrate
serialvfd1.serial.bytesize = bytesize
serialvfd1.serial.parity   = parity
serialvfd1.serial.stopbits = stopbits
serialvfd1.serial.timeout  = timeout
serialvfd1.mode = comms.MODE_RTU

#initialize variables to safe settings
vfd['spdvfd.run'] = 0
vfd['spdvfd.forward'] = 1
vfd['spdvfd.rpmset'] = 500
vfd['spdvfd.commfrequency'] = 0


def main():
    laststate = 0
    while 1:
        try:
            resp = serialvfd1._performCommand(0x03, struct.pack('>HH', 0x500,0x05))

            laststate = ord(resp[2])
            vfd['spdvfd.commfrequency'] = ord(resp[3])*256 + ord(resp[4])
            vfd['spdvfd.outfrequency'] = ord(resp[5])*256 + ord(resp[6])

            # convert freq to rpm (outfreq unit is 0.01Hz) 400Hz = 40000 as commfreq
            vfd['spdvfd.outrpm'] = vfd['spdvfd.outfrequency'] * 24000.0/40000
            vfd['spdvfd.atfreq'] = vfd['spdvfd.commfrequency'] == vfd['spdvfd.outfrequency']

            vfd['spdvfd.outcurrent'] = (ord(resp[7])*256 + ord(resp[8])) / 10.0
            vfd['spdvfd.outvoltage'] = (ord(resp[9])*256 + ord(resp[10])) / 10.0
            vfd['spdvfd.power'] = vfd['spdvfd.outcurrent'] * vfd['spdvfd.outvoltage']

        except KeyboardInterrupt:
            raise SystemExit
        except Exception, e:
            pass

        fct = None
        payload = ""

        #start/stop/cw/ccw
        if vfd['spdvfd.run'] and vfd['spdvfd.forward'] and (laststate & 3) != 1: #run CW
            fct = 0x10
            payload = struct.pack('>HHBH', 0x900,0x01,0x02,1)
        elif vfd['spdvfd.run'] and not vfd['spdvfd.forward'] and (laststate & 3) != 3: #run CCW
            fct = 0x10
            payload = struct.pack('>HHBH', 0x900,0x01,0x02,3)
        if not vfd['spdvfd.run'] and (laststate & 1) != 0: #stop
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

        #set the frequency (commfreq unit is 0.01Hz) 400Hz = 40000 as commfreq
        # cap rpm at 24000 => 400Hz
        if vfd['spdvfd.rpmset'] > 24000:
            vfd['spdvfd.rpmset'] = 24000
        freqset = int(vfd['spdvfd.rpmset'])*40000.0/24000
        if int(vfd['spdvfd.commfrequency']) != int(freqset):
            _vfd_do(0x10, struct.pack('>HHBH', 0x901, 0x01, 0x02, freqset))

def _vfd_do(fct,payload):
    while True:
        try:
            return serialvfd1._performCommand(fct,payload)
        except KeyboardInterrupt:
            raise SystemExit
        except:
            with open("/tmp/vfd_hal",'a') as f:
                f.write(str(datetime.datetime.now()))
                f.write(
                    " Error while writing: fct: %.2x\t payload:%s (%s)\n%s\n"%(
                        fct,payload,
                        " ".join("%.2x"%ord(n) for n in payload),
                        traceback.format_exc()
                    )
                )
                f.flush()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit
    except Exception, e:
        with open("/tmp/vfd_hal",'a') as f:
            f.write(str(datetime.datetime.now()))
            f.write(traceback.format_exc())
            f.flush()
