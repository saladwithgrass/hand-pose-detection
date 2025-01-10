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

## ~~Task 4: Calibrate Cameras~~
I have to calibrate cameras with a chessboard, i think i will use ChArUco.
From calibration i will get `rvecs` and `tvec` which are elements of homogenous transforms.
From there it should be relatively smooth sailing. 

Cameras have been calibrated. I marked them L and R. Left has a small error of about 0.24, while the right one has around 0.47. 
Maybe i'll recalibrate them, since my tech for calibration is anything but precise.

Now, i should try getting rvec and tvec and then determining the of an object.

Also, above i made a mistake of saying that i will get `rvecs` and `tvecs` from calibration. No. From calibration i only get camera data.
It can be used then to determine `rvec` and `tvec` more precisely. 

## ~~Task 5: 3d graphics~~
Now, i want to triangulate the position of an object with cameras.
I don't have anything precise in 3d space on my hands right now.
What i will do is display and point in 3d and look at its movement and try verifying if at least its quality is correct.
Any other precision will come from better calibration and better calibration comes from better equipment. 
As of now, i have to figure out how to draw a point on a 3d plot.
I have a class that updates it's plot with point coordinates

## Task 6: Triangulation
For start i will try to track the position of charuco board and see where it gets me.
1) Do it with one camera and see how well it tracks it.

    It is VERY slow, but i was able to track an aruco marker

2) Triangulate Charuco board with two cameras

    This step needs reworking:
        
        1) Simultaneously calibrate two cameras to determine their relative orientation. 
        2) Draw them and verify that everything is okay.
        3) Triangulate a marker and draw it in relation to cameras
3) Triangulate hand
