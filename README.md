nowforever_vfd
==============

Based on the "Sumitomo HF-430 | Hitachi SJ300 | Hitachi L300P" python example from http://wiki.linuxcnc.org/cgi-bin/wiki.pl?VFD_Modbus

It handles communication with Nowforever E100 VFD using RS-485 / Modbus RTU mode.
There are a couple of intermediate values to convert RPM to freq and vice versa.

You can drive spindle:
 - start/stop (`vfd.spdvfd.run`)
 - direction (`vfd.spdvfd.forward`)
 - setpoint speed (`vfd.spdvfd.rpmset`)

It also reads from the VFD:
 - freq setpoint  (`vfd.spdvfd.commfrequency`)
 - current freq (`vfd.spdvfd.outfrequency`) + virtual current rpm (`vfd.spdvfd.outrpm`)
 - current current (A) (`vfd.spdvfd.outcurrent`)
 - current voltage (V) (`vfd.spdvfd.outvoltage`)
 - current power (VA) (`vfd.spdvfd.power`)
 - if spindle is at speed (`vfd.spdvfd.atfreq`)

TODO:
 - use argparse to make the script parametric
 - <del>optimize to not send order every time (only when they differs like start stop, direction, freq)</del>
