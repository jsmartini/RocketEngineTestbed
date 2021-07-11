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






Load Cell Data Packet:







System Reporting Data Packet





RemoteCLI DataPacket
