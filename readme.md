Basic movement detection algorithm based on static background subtraction.


### Running

Three alternative sets of parameters are defined in the `config.ini` file: default, fast, slow. 

The mode can be modified in the `movement_detection.py` script: `mode = 'fast' # default, slow, fast`
### Parameters

input_file: path to video to be used (people_walking.mp4)
consecutive_frame: number of consecutive frames to be used at each step for 
wait_milliseconds: number of milliseconds to wait between each frame

### algorithm

```text
Get the background image by taking the mean of 50 random frames
Convert the frame to grayscale

For each consecutive 4-frame set:

    For each frame in the 4-set:
        1. Compute abs. difference between background and current frame
        2. Convert that difference to black/white for pixels above/below 50 threshold
        3. Dialte (twice) using default 3x3 kernel
    - Sum up the 4 resulting frames
    - Compute contours in resulting frame
    For each contour with area >=500:
        1. Compute bounding box
        2. Draw bounding box on original frame
```