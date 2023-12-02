#!/bin/bash
sudo apt-get install sox

xrandr --output DP-7 --same-as DP-1
xrandr --output DP-5 --same-as DP-1

rec -r 16000 ./recordings/sound%6n.wav silence 1 0.1 2%  1 3.0 2% : newfile : restart
