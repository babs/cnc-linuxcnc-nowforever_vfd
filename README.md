nowforever_vfd
==============

Based on the "Sumitomo HF-430 | Hitachi SJ300 | Hitachi L300P" python example from http://wiki.linuxcnc.org/cgi-bin/wiki.pl?VFD_Modbus

It handles communication with Nowforever VFD using RS-485 / Modbus RTU mode.
There are a couple of intermediate values to convert RPM to freq and vice versa.


You can drive spindle:
 - start
 - stop
 - direction
 - setpoint speed

It also reads from the VFD:
 - freq setpoint (+ virtual rpm setpoint)
 - current freq
 - current current
 - current voltage

TODO:
 - optimize to not send order every time (only when they differs like start stop, direction, freq)
