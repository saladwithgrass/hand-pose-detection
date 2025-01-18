# IMPORTANT
If you use wayland, be wary of opencv being somewhat fucky. In my case it was fixed with 
`$ export QT_QPA_PLATFORM=xcb`

# Part 1: Pose Detection Module

For now this module is just for detection, but when i figure it out, i'm going to add conversion to gripper later.

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

## ~~Task 6: Triangulation~~
For start i will try to track the position of charuco board and see where it gets me.
1) Do it with one camera and see how well it tracks it.

    It is VERY slow, but i was able to track an aruco marker

2) Triangulate Charuco board with two cameras

    This step needs reworking:
        
        1) Simultaneously calibrate two cameras to determine their relative orientation. 
        2) Draw them and verify that everything is okay.
        3) Triangulate a marker and draw it in relation to cameras

    Okay, a lot of details occured to me.
    I researched the DLT algorithm that is used to triangulate in 3D and wrote.
    It seems to run, but it does not work properly. Main suspicion is on the incorrect usage of rvecs and tvecs for determining world position.
    Steps were updated:

        1) Calibrate two cameras and extract rvecs and tvecs in their correct form
        2) Try to triangulate the world origin. This is done by getting its pixel representation when calibration orientation. 
    All i need to do for triangulation is solve a system for two projection matrices. Just easy math.

        
АХАХАХАХАХАХАХ Я НАШЕЛ ЕБАНУЮ ОШИБКУ, ЩА КАК СДЕЛАЮ ТРИАНГУЛЯЦИЮ И ОНА ЗАРАБОТАЕТ АХАХАХАХАХА

3) Triangulate hand

## Conclustion to Part 1
Okay, so i managed to write a set of scripts that is capable of triangulating a point in 3D space based on its position on the screen.
### Findings
1) Triangulation does not use DLT, DLT is used to determine camera intrinsics and extrinsics during the calibration step. Triangulation is simply solving some linear equations for projections.
2) Rotation vector and translation vector that i get from estimating charuco pose ARE the vectors i need to create the projection matrix.
3) Hand is very twitchy.
### Todo
1) Streamline the experience, for example, unite calibration data into one file after extrinsics calibration. Also, maybe add a single script to run everyting.
2) Profile it. See what takes up the most time.
3) Optimize where possible. I have a suspicion, that triangulation itself can be improved since it's basically just solving overdefined linear equations.
4) Recalibrate cameras. Add more frames and leave it to run for a night. Will be done when i come home. Also, make it possible to save calibration data without running the calibration itself.
5) Look into how i can use distortion coefficients to improve results.
6) Maybe, add some kind of filtering to make hand less twitchy.
7) Maybe look into other models for landmarks.

# Part 2: Gripper conversion

Now, i need to determine what the person actually does. And calculate how much should i open the gripper.
## Brainstorming ideas
### The stupid way
I could go the stupid way and just look at the index finger and the thumb, and run from there. I think, i will use this in the beginning just for its simplicity.
### The kinda smart way
I could record multiple ways of grabbing stuff and then write an heuristic that will evaluate how close the current pose to each of them and select the closest.
Immidiately, what comes to my attention is that in the perfect world, i should normalize the hand by some characteristic. But the details will come later.
### The expensive way
I could train some neural network to evaluate the probability of each pose. However, there are sooo many problems with this:
1) I need a big dataset that will accomodate networks needs for data.
2) I need a big GPU to train the network on.

## Task 1: Do it the stupid way.
So, what is to be done:
1) Look only at the last two joints of index finger and thumb
2) Select the point where they are the closest. 
3) Draw parallel lines that lie as close to the original joints as possible.
4) This is the gripper. Make it a plane
5) Determine the orientation and position of this plane.
