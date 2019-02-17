# ///////////////////////////////////////////////////////////////// //
#                                                                   //
# python script to read the pressure with a                         //
# Pfeiffer Vacuum Dual Gauge TPG 362 Controller, PTG 28290          //
#                                                                   //
# Last modifications: 17.02.2019 by R.Berner                        //
#                                                                   //
# ///////////////////////////////////////////////////////////////// //

from   class_def import *
import subprocess
import time

# Define offset
offset_p1 = 0
offset_p2 = 0

# Setting up connection
gauge = TPG362(port='/dev/ttyUSB0')

# Print some information about the device
gauge._send_command('AYT')
answer = gauge._get_data()
print "----------------------------------------"
print "Device Type:", answer.split(',')[0]
print "Model No.:  ", answer.split(',')[1]
print "Serial No.: ", answer.split(',')[2]
print "----------------------------------------"
print "Firmware version:", answer.split(',')[3]
print "Hardware version:", answer.split(',')[4]
print "----------------------------------------"
gauge._send_command('RHR')
print "Operating hours:  ", gauge._get_data()
gauge._send_command('TMP')
print "Inner temperature:", gauge._get_data(), "degrees"
print "----------------------------------------"
gauge._send_command('ETH')
answer = gauge._get_data()
if int(answer.split(',')[0]) == 0: print "IP address:     ", answer.split(',')[1], "(statically)"
if int(answer.split(',')[0]) == 1: print "IP address:     ", answer.split(',')[1], "(dynamically)"
print "Subnet address: ", answer.split(',')[2]
print "Gateway address:", answer.split(',')[3]
print "----------------------------------------"
gauge._send_command('TID')
answer = gauge._get_data()
print "Gauge 1:", answer.split(',')[0]
print "Gauge 2:", answer.split(',')[1]
print "----------------------------------------"

# Setting the backlight to 0%
gauge._send_command('BAL,0')

# Setting unit to mbar/bar
gauge._send_command('UNI,0')

# Save number format (0: floating point; 1: exponential)
gauge._send_command('FMT,0')

# Setting the gas to nitrogen/air (1: Ar; 2: H; 3: He; 4: Ne; 5: Kr; 6: Xe; 7: Other gases)
gauge._send_command('GAS,0,0')

# Setting the range of linear gauges to 1000 hPa (Logarithmic gauges are recognized automatically)
gauge._send_command('FSR,5,5')

# Setting the measurement value filter (0: Off; 1: Fast; 2: Normal; 3: Slow)
gauge._send_command('FIL,2,2')

# Save user parameters
gauge._send_command('SAV,1')

# Acquiring data
while 1:
    try:
        gauge._send_command('PRX')
        answer = gauge._get_data()
    except (IOError):
        pass

    try:
        # The answer is of the form: statusCode1,pressure1,statusCode2,pressure2
        statusCode_p1 = int(answer.split(',')[0])
        p1 = float(answer.split(',')[1]) + offset_p1
        statusCode_p2 = int(answer.split(',')[2])
        p2 = float(answer.split(',')[3]) + offset_p2
        #print "p1: ", p1
        #print "statusCode_p1: ", statusCode_p1
        #print "p2: ", p2
        #print "statusCode_p2: ", statusCode_p2

        # Send data to database (only if data is of good quality, e.g. statusCode==0)
        if statusCode_p1==0 and p1>=0.:
            print "p1 =", p1, gauge.pressure_unit()
            #post1_bar = "pressure_bar,sensor=1,pos=cryostat value=" + str(p1)
            #subprocess.call(["curl", "-i", "-XPOST", "lhepdaq2.unibe.ch:8086/write?db=module_zero_run_jan2019", "--data-binary", post1_bar])
        if statusCode_p1==1: print "Sensor 1: Underrange"
        if statusCode_p1==2: print "Sensor 1: Overrange"
        if statusCode_p1==3: print "Sensor 1: Sensor error"
        if statusCode_p1==4: print "Sensor 1: Sensor off"
        if statusCode_p1==5: print "Sensor 1: No sensor (output: 5,20000E-2 [mbar])"
        if statusCode_p1==6: print "Sensor 1: Identification error"

        if statusCode_p2==0 and p2>=0.:
            print "p2 =", p2, gauge.pressure_unit()
            #post2_bar = "pressure_bar,sensor=2,pos=cryostat value=" + str(p2)
            #subprocess.call(["curl", "-i", "-XPOST", "lhepdaq2.unibe.ch:8086/write?db=module_zero_run_jan2019", "--data-binary", post2_bar])
        if statusCode_p2==1: print "Sensor 2: Underrange"
        if statusCode_p2==2: print "Sensor 2: Overrange"
        if statusCode_p2==3: print "Sensor 2: Sensor error"
        if statusCode_p2==4: print "Sensor 2: Sensor off"
        if statusCode_p2==5: print "Sensor 2: No sensor (output: 5,20000E-2 [mbar]"
        if statusCode_p2==6: print "Sensor 2: Identification error"

        time.sleep(0.95)

    except (ValueError,IndexError,IOError):
        pass
