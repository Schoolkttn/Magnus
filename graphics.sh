#!/bin/bash

# Start the lockscreen with animation
qmlscene lockscreen.qml &

# Lock the screen after animation starts
qdbus org.freedesktop.ScreenSaver /ScreenSaver Lock
