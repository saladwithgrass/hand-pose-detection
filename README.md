# IMPORTANT
If you use wayland, be wary of opencv being somewhat fucky. In my case it was fixed with 
`$ export QT_QPA_PLATFORM=xcb`

# Pose Detection Module

For now this module is just for detection, but when i figure it out, i'm going to add conversion to gripper here.

## ~~Task 1: Basic Detection~~
~~Setup basic detection~~

## ~~Task 2: Mediapipe `LIVE_STREAM`~~
Figure out how to use `LIVE_STREAM` option in mediapipe.
I figured it out and it is not so different from `VIDEO`, so I'll just use it.
As of now I have set up the detection with video and there's no need for `LIVE STREAM`


## Task 3: Parallel Computing (LATER)
Setup parallel computing for this stuff.
### Step 1
I think i should separate detection, so that there are not two of everything for each image. I Think, what i will do is have a listener process that is used for drawing, and two threads that run detection.
#### Schematic
By running a program, I will spawn two detection processes.
The main thread will be just a `while True:` loop that waits for completion on both those processes. Once both results are not None, draw them.

## Task 4: Calibrate Cameras 
I have to calibrate cameras with a chessboard, i think i will use ChArUco.
From calibration i will get `rvecs` and `tvec` which are elements of homogenous transforms.
From there it should be relatively smooth sailing. 