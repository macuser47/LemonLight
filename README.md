# LemonLight

LemonLight is a FLOSS machine vision solution designed for use by teams in the FIRST Robotics Competition. The system, modeled after the [limelight camera](https://limelightvision.io/), is designed to run on embedded linux systems like the Raspberry Pi, and provides an easy to use vision pipeline for object detection on robotic systems.

[![LemonLight Demo](/img/demo.gif)](https://www.youtube.com/watch?v=FIk3sqZEktc)

## About

LemonLight provides a web configurator that enables users easily calibrate vision parameters to detect objects in a scene. Contour data from the image is communicated to other embedded systems via the [FRC NetworkTables API](https://github.com/robotpy/pynetworktables).

LemonLight is designed as a low-cost alternative to the limelight camera system, with specific goals of being able to work well on an inexpensive, diverse set of common hardware owned by most FRC teams. This, coupled with the easy to use web configurator, enables the vast majority of teams to quickly deploy vision systems without the overhead of developing team-specific OpenCV applications.

## Implementation

LemonLight uses the python mappings of the OpenCV for vision processing along with flask for managing web sessions.

## Running the Demo

Note that the current build of LemonLight does not work on Windows systems. It is confirmed working on Linux, and the state on MacOS is unknown.

LemonLight uses python 2.7.

LemonLight requires `OpenCV`, `flask`, and `pynetworktables`.

You can see how to install OpenCV for linux systems [here.](https://github.com/milq/milq/blob/master/scripts/bash/install-opencv.sh)

Install other dependencies:

```
pip install flask
pip install pynetworktables
```
Clone the project and run the demo:

```
git clone https://github.com/macuser47/LemonLight
cd LemonLight/webserver
sudo python LemonLight.py
```

The application should run and be accessible at http://127.0.0.1:125/


