<br/>
<p align="center">
  <a href="https://github.com/clates/home-security-pi">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">Home Security System built on some Raspberry Pi0ws</h3>

  <p align="center">
    Simple python CV project to get comfortable with Python and the OpenCV library.
    <br/>
    <br/>
    <a href="https://github.com/clates/home-security-pi"><strong>Explore the docs »</strong></a>
    <br/>
    <br/>
    <a href="https://github.com/clates/home-security-pi">View Demo</a>
    .
    <a href="https://github.com/clates/home-security-pi/issues">Report Bug</a>
    .
    <a href="https://github.com/clates/home-security-pi/issues">Request Feature</a>
  </p>
</p>

![Downloads](https://img.shields.io/github/downloads/clates/home-security-pi/total) ![Contributors](https://img.shields.io/github/contributors/clates/home-security-pi?color=dark-green) ![Issues](https://img.shields.io/github/issues/clates/home-security-pi) ![License](https://img.shields.io/github/license/clates/home-security-pi) 

## Table Of Contents

* [About the Project](#about-the-project)
* [Built With](#built-with)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage](#usage)
* [Contributing](#contributing)
* [Authors](#authors)
* [Acknowledgements](#acknowledgements)

## About The Project

I needed to get reacquainted with Python and learn a little bit of OpenCV for work. Also needed to get a security system for the house. Two birds, one stone.

## Built With

Raspberry Pi Zero W
NoIR Camera V2
Redis - For realtime image sharing.
Python
OpenCV - For Image processing
PyGame - For audio alerting

## Getting Started

This is an example of how you may give instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps.

### Prerequisites

You'll need at the very least 1 Pi to act as the HostImager, and 1 other machine to act as the DisplayServer. Make sure to `sudo apt-get update` and that you have a working `pip`/`pip3` and `python`/`python3` on all machines.


### Installation

#### Setting up the Pi (alerter and/or imager):

Starting from a fresh install of a Raspberry Pi run the following to get the openCV libraries prepped before pip. 

```
sudo apt-get install libhdf5-dev libhdf5-serial-dev libhdf5-100
sudo apt-get install libqtgui4 libqtwebkit4 libqt4-test
sudo apt-get install libatlas-base-dev
sudo apt-get install libjasper-dev
```

then finally you'll need to pip all your python dependencies in

```
pip3 install opencv-contrib-python
pip3 install redis
```

#### Setting up the DisplayServer 

I guess this could be any machine, I used my desktop but might port to a different pi at some point in the future

Install and run the redis server 
- https://redis.io/topics/quickstart
- After it's up and running you'll need to allow connections from your Pi to your DisplayServer `./src/redis-cli` then at the CLI prompt `CONFIG SET protected-mode no`. You're looking for a response `"OKAY"`

Pip all your same dependencies, but you'll also need ffmpeg
`pip install ffmpeg-python`
and the binary `sudo apt-get install ffmpeg`


## Usage

TODO: Add pictures / videos. 

