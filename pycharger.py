#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import os, sys
import time
import serial
from datetime import datetime

 
# discharge end voltage (empty)
 
dchg_end = 3.2
 
 
# iCharger modes of operation
mop=[None]*13
 
mop[1]  = "Charging"
mop[2]  = "Discharging"
mop[3]  = "Monitor"
mop[4]  = "Waiting"
mop[5]  = "Motor burn-in"
mop[6]  = "Finished"
mop[7]  = "Error"
mop[8]  = "LIxx trickle"
mop[9]  = "NIxx trickle"
mop[10] = "Foam cut"
mop[11] = "Info"
mop[12] = "External-discharging"
 
# configure the serial connections 
# change according to the ttyUSB assigned to the iCharger (dmesg)
 
ser = serial.Serial(
    port='/dev/ttyUSB0',
)
ser.close()
ser.open()
ser.isOpen()

# create 2 csv files for results storing, wipe already existing files

chgfile = open("charge.csv", "w")
dchgfile = open("discharge.csv", "w")

chgfile.write("time, V_in, V_bat, V_C1, V_C2, V_C3, V_C4, V_C5, V_C6, I_cgh, I_sum, T_int \n")
dchgfile.write("time, V_in, V_bat, V_C1, V_C2, V_C3, V_C4, V_C5, V_C6, I_cgh, I_sum, T_int \n")

 
### MAIN #############################################################
 
while 1 :
 
    # read current measurments from the charger, split the values into an array of strings
    line    = ser.readline  ()
    raw     = str(line).split    (';')
 
    # extract values from the array, convert to float/int
    v_bat   = float(raw[4])/1000
    v_c1    = float(raw[6])/1000
    v_c2    = float(raw[7])/1000
    v_c3    = float(raw[8])/1000
    v_c4    = float(raw[9])/1000
    v_c5    = float(raw[10])/1000
    v_c6    = float(raw[11])/1000
    v_in    = float(raw[3])/1000
    i_chg   = int(raw[5])/100
    i_sum   = float(raw[14])/1000
    t_int   = float(raw[12])/10
    t_ext   = float(raw[13])/10
 
    # calculate rudimentary charge percentages
    s_vc1   = max((v_c1 - dchg_end)*100, 0)
    s_vc2   = max((v_c2 - dchg_end)*100, 0)
    s_vc3   = max((v_c3 - dchg_end)*100, 0)
    s_vc4   = max((v_c4 - dchg_end)*100, 0)
    s_vc5   = max((v_c5 - dchg_end)*100, 0)
    s_vc6   = max((v_c6 - dchg_end)*100, 0)
 
    # print values to the CLI for on-the-go monitoring
    print("Mode:           " + mop[int(raw[1])])
    print("Batt:           " + "%.2f" % v_bat + " V")
    print("Cell 1:         " + "%.2f" % v_c1  + " V (" + "%.2f" % s_vc1 + "%)")
    print("Cell 2:         " + "%.2f" % v_c2  + " V (" + "%.2f" % s_vc2 + "%)")
    print("Cell 3:         " + "%.2f" % v_c3  + " V (" + "%.2f" % s_vc3 + "%)")
    print("Cell 4:         " + "%.2f" % v_c4  + " V (" + "%.2f" % s_vc4 + "%)")
    print("Cell 5:         " + "%.2f" % v_c5  + " V (" + "%.2f" % s_vc5 + "%)")
    print("Cell 6:         " + "%.2f" % v_c6  + " V (" + "%.2f" % s_vc6 + "%)")
    print("Supply:         " + "%.2f" % v_in + " V")
    print("Charge Current: " + "%.2f" % i_chg + " A")
    print("Charge Amount:  " + "%.2f" % i_sum + " Ah")
    print("Temp INT:       " + "%.1f" % t_int + " °C")
    print("Temp EXT:       " + "%.1f" % t_ext + " °C")
    print("\n")

    # get current time for logs
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    # append values to csv files created earlier (only when charging/discharging)
    if raw[1] == '1':
        with open("charge.csv", "a") as chgfile:
            chgfile.write(current_time + ", " + str(v_in) + ", " + str(v_bat) + ", " + str(v_c1) + ", " + str(v_c2) + ", " + str(v_c3) + ", " + str(v_c4) + ", " + str(v_c5) + ", " + str(v_c6)+ ", " + str(i_chg) + ", " + str(i_sum) + ", " + str(t_int) + "\n")

    if raw[1] == '2':
        with open("discharge.csv", "a") as dchgfile:
            dchgfile.write(current_time + ", " + str(v_in) + ", " + str(v_bat) + ", " + str(v_c1) + ", " + str(v_c2) + ", " + str(v_c3) + ", " + str(v_c4) + ", " + str(v_c5) + ", " + str(v_c6)+ ", " + str(i_chg) + ", " + str(i_sum) + ", " + str(t_int) + "\n")