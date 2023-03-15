import cv2 
import argparse 
import numpy as np
import configparser
 
def get_background(file_path): 
    cap = cv2.VideoCapture(file_path) 
    # we will randomly select 50 frames for the calculating the median 
    frame_indices = np.random.randint(0, cap.get(cv2.CAP_PROP_FRAME_COUNT), 50)
    # frame_indices = cap.get(cv2.CAP_PROP_FRAME_COUNT) * np.random.uniform(size=50) 

    # sample the frames corresponding to the frame indices, and store them in the array
    frames = [] 
    for idx in frame_indices:
        # set the frame id to read that particular frame 
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx) 
        ret, frame = cap.read() 
        frames.append(frame) 

    # calculate the median 
    median_frame = np.median(frames, axis=0).astype(np.uint8)
    return median_frame


config = configparser.ConfigParser()
config.read('config.ini')

mode = 'fast' # default, slow, fast

# Set default values for command line arguments based on the configuration file
default_input_file = config.get('default', 'input_file', fallback=None)
default_consecutive_frame = config.getint('default', 'consecutive_frame', fallback=1)
default_wait_milliseconds = config.getint('default', 'wait_milliseconds', fallback=50)

parser = argparse.ArgumentParser()
parser.add_argument('--input_file', default=default_input_file, help='Path to the input file')
parser.add_argument('--config', help='Path to the configuration file')
parser.add_argument('--consecutive_frame', type=int, default=default_consecutive_frame, help='Number of consecutive frames to process at once')
parser.add_argument('--wait_milliseconds', type=int, default=default_wait_milliseconds, help='Number of milliseconds to wait between frames')

args = parser.parse_args()

# Update default values based on the configuration file
if config:
    # config.read(args.config)
    input_file = config.get(mode, 'input_file', fallback=None)
    consecutive_frame = config.getint(mode, 'consecutive_frame', fallback=None)
    wait_milliseconds = config.getint(mode, 'wait_milliseconds', fallback=None)
    if input_file is not None:
        args.input = default_input_file
    if consecutive_frame is not None:
        args.consecutive_frame = consecutive_frame
    if wait_milliseconds is not None:
        args.wait_milliseconds = wait_milliseconds


input_file = getattr(args, 'input_file', None)
consecutive_frame = getattr(args, 'consecutive_frame', None)
wait_milliseconds = getattr(args, 'wait_milliseconds', None)

if input_file is None:
    print('Error: input file not specified')
if consecutive_frame is None:
    print('Error: consecutive_frame not specified')
if wait_milliseconds is None:
    print('Error: wait_milliseconds not specified')



cap = cv2.VideoCapture(input_file)
# get the video frame height and width 
frame_width = int(cap.get(3)) 
frame_height = int(cap.get(4)) 
save_name = f"outputs/{input_file.split('/')[-1]}" 
# define codec and create VideoWriter object 
out = cv2.VideoWriter( 
    save_name, 
    cv2.VideoWriter_fourcc(*'mp4v'), 10,  
    (frame_width, frame_height) 
) 
# get the background model 
background = get_background(input_file)
# convert the background model to grayscale format 
background = cv2.cvtColor(background, cv2.COLOR_BGR2GRAY) 
# create a black image of the same size as the background
black_image = np.zeros(background.shape, dtype=np.uint8)
frame_count = 0 
while (cap.isOpened()): 
    ret, frame = cap.read() 
    # wait for 50 millisecond
    #if 
    #cv2.waitKey(wait_milliseconds)
    if ret == True: 
        frame_count += 1 
        orig_frame = frame.copy()
        # IMPORTANT STEP: convert the frame to grayscale first 
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
        # if the frame count is 1st or a multiple of consecutive_frame
        if frame_count % consecutive_frame == 0 or frame_count == 1: 
            frame_diff_list = [] 
        # find the difference between current frame and base frame 
        frame_diff = cv2.absdiff(gray, background) 

        # thresholding to convert the frame to binary 
        ret, thres = cv2.threshold(frame_diff, 50, 255, cv2.THRESH_BINARY) 

        # dilate the frame a bit to get some more white area... 
        # ... makes the detection of contours a bit easier 
        dilate_frame = cv2.dilate(thres, None, iterations=2) 

        # append the final result into the frame_diff_list 
        frame_diff_list.append(dilate_frame) 
        # if we have reached consecutive_frame number of frames 
        if len(frame_diff_list) == consecutive_frame: 
            # add all the frames in the frame_diff_list 
            sum_frames = sum(frame_diff_list) 
            # find the contours around the white segmented areas 
            contours, hierarchy = cv2.findContours(sum_frames, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 

            # display gray, background, frame_diff, thres, dilate_frame, sum_frames side by side horizontally
            cv2.imshow('Gray, Background, Frame Diff, thres, dilate_frame, sum_frames', np.hstack([np.vstack([gray, background]), np.vstack([frame_diff, thres]), np.vstack([dilate_frame, sum_frames])]))
            # draw the contours, not strictly necessary 
            for i, cnt in enumerate(contours): 
                cv2.drawContours(frame, contours, i, (0, 0, 255), 3) 
            for contour in contours: 
                # continue through the loop if contour area is less than 500... 
                # ... helps in removing noise detection 
                if cv2.contourArea(contour) < 500: 
                    continue 
                # get the xmin, ymin, width, and height coordinates from the contours 
                (x, y, w, h) = cv2.boundingRect(contour) 
                # draw the bounding boxes 
                cv2.rectangle(orig_frame, (x, y), (x+w, y+h), (0, 255, 0), 2) 
         
            cv2.imshow('Detected Objects', orig_frame) 
            out.write(orig_frame)
            if cv2.waitKey(wait_milliseconds) & 0xFF == ord('q'): 
                break 
    else: # could not read the frame
        break 
cap.release() 
cv2.destroyAllWindows()


