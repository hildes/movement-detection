Basic movement detection algorithm based on static background subtraction.


### Running

Three alternative sets of parameters are defined in the `config.ini` file: default, fast, slow. 

The mode can be modified in the `movement_detection.py` script: `mode = 'fast' # default, slow, fast`
### Parameters

input_file: path to video to be used (people_walking.mp4)
consecutive_frame: number of consecutive frames to be used at each step for 
wait_milliseconds: number of milliseconds to wait between each frame

### Algorithm

```text
Get the background image by taking the mean of 50 random frames

Convert the frame to grayscale

For each consecutive 4-frame set:

    For each frame in the 4-set:
    
        Compute abs. difference between background and current frame
        
        Convert that difference to black/white for pixels above/below 50 threshold
        
        Dialte (twice) using default 3x3 kernel
        
    Sum up the 4 resulting frames
    
    Compute contours in resulting frame
    
    For each contour with area >=500:
    
        Compute bounding box
        
        Draw bounding box on original frame
```

### Results

![image1](https://user-images.githubusercontent.com/24638777/225451817-7e558608-caf2-4bbb-9b5e-80f6174fa7f7.png)
![image2](https://user-images.githubusercontent.com/24638777/225451836-0f377343-9e52-4fed-b529-690ff216c929.png)
