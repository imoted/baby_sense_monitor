#!/bin/bash

ffmpeg -i /dev/video2 -vcodec libx264 -g 0 -s 640x480 -f flv rtmp://localhost:1935/live/test2
