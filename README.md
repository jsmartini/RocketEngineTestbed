# RocketEngineTestbed
The final iteration (0MQ)


This is the final iteration of the Alabama Rocketry Association Rocket Engine Test Bed Software

temp - Example ZeroMQ(0MQ) pub/sub req/rep DDS models for data aquisitioning and remote function calling

Hardware - Teststand specific application files

Controller - Ground Stations specific application files (GUI/DataFeed Monitoring and logging)

TO-DO:
- reimplment GPIO solenoid function togglers
- test the hardware software for bugs and configuration errors
- write software (.sh) to automatically configure a new install of raspberry pi for static address networking configuration to do control via 150ft Catv6 cable
- write testbed test software to pull datafeeds off of the rpi
- develop closed loop pid control to discretely depressurize the LOX/KERO tanks if propellant boiloff causes pressure spikes.

- write the GUI with commandline/data plotting/system state display features


Done:
- PUB/SUB endpoints 
- basic data reading features
- data and state reporting
