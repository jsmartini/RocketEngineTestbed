RPi Program


Features
-data aquisition
-solenoid control
-data publishing (0MQ)
-PID control of tank pressure


TO-DO
-implement closed loop control model for PID in pressure subscriber
-implement scaling for reading pressure data
-implement gpio activiation of solenoids from older revisions
    -implement hardware functions into remoteCLI compatible functions via wrappers
-test on hardware

Endpoints and Data Packets
- tcp://127.0.0.1:port (check config.toml for information on publisher services)

Pressure Data Packet:

data sub-dict
{
            "LOX_PSI": 0,
            "KERO_PSI": 0
            "KERO_ERROR: 0,
            "LOX_ERROR": 0
}


scaleNSmooth function outputs the data sub-dict above which contains the pressure data
{
                        "DATA": scaleNSmooth(ADS.read_sequence(ADC_channels)),
                        "TIME": TS()
}



Load Cell Data Packet:

{
                        "NODE_NAME"    : node_name,
                        "SENSOR_NAME"  : cell_name,
                        "VOLTAGE_RATIO": vr,
                        "TIME": TS()
}


System Reporting Data Packet

{
                        "SYSTEM": SYS,
                        "TIME": TS()
}



RemoteCLI DataPacket
