'''
dream to dream video
'''

import cv2
import os
import numpy as np
import PIL.Image
from deepdreamer import model, load_image, recursive_optimize

def create_dream_frames(file_name = "test.png", target_dream_layer = 3, total_frames=5, zoom_in=False):
    """
    Args:
        file_name: orginal image file
        target_dream_layer: targeted dream layer style
        total_frames: total number of frames of dream images to generate
    Returns:
        dream_layer_dir_path: directory path storing the frames
        file_name: name of original image file
    Creates the total number of frames, inside dream_frames/img_name
    """
    curr_path = os.getcwd()
    dream_frames_path = os.path.join(curr_path, 'dream_frames')
    # zoom-in effect directory
    if zoom_in:
        dream_frames_path = dream_frames_path + '_zoom_in'

    # check and create '/dream_frames' directory
    if not os.path.exists(dream_frames_path):
        os.mkdir(dream_frames_path)

    # /file_name dir
    dream_dir_path = os.path.join(dream_frames_path, '{}'.format(format(file_name[:-4])))
    if not os.path.exists(dream_dir_path):
        os.mkdir(dream_dir_path)
    
    # /layer_num
    dream_layer_dir_path = os.path.join(dream_dir_path, 'layer_{}'.format(target_dream_layer))
    if not os.path.exists(dream_layer_dir_path):
        os.mkdir(dream_layer_dir_path)

    dream_layer_tensor = model.layer_tensors[target_dream_layer]

    # saves original image as starter image
    img_path = os.path.join(dream_layer_dir_path, 'img_0.png')
    result = PIL.Image.open(file_name)
    (x_size, y_size) = result.size
    result.save(img_path)

    # generates the frames
    for i in range(total_frames-1):
        img_result = load_image(filename='{}{}.png'.format(img_path[:-5], i))
        if zoom_in:
            x_trim = 10
            y_trim = 10
            img_result = img_result[0+x_trim:y_size-y_trim, 0+y_trim:x_size-x_trim]
            img_result = cv2.resize(img_result, (x_size, y_size))
            img_result[:, :, 0] += 3  # reds
            img_result[:, :, 1] += 3  # greens
            img_result[:, :, 2] += 3  # blues
            img_result = np.clip(img_result, 0.0, 255.0)
            img_result = img_result.astype(np.uint8)
        img_result = recursive_optimize(layer_tensor=dream_layer_tensor,
                                        image=img_result,
                                        num_iterations=15,
                                        step_size=1.0,
                                        rescale_factor=0.7,
                                        num_repeats=1,
                                        blend=0.2)

        img_result = np.clip(img_result, 0.0, 255.0)
        img_result = img_result.astype(np.uint8)
        result = PIL.Image.fromarray(img_result, mode='RGB')
        result.save('{}{}.png'.format(img_path[:-5], i+1))
        print('{}/{} DONE'.format(i+1,total_frames))
    return dream_layer_dir_path, file_name
    

def create_dream_video(file_name = "test.png", 
                        img_dir = None, 
                        total_frames=5,
                        fps=5, 
                        video_length=0):
    """
    Args:
        file_name: image to create dream video on
        img_dir: directory with all the frames
        total_frames: the total number of frames in directory
        fps: frames per second of the generated video
        video_length: the duration of the generated video

    Use the frames created and convert them into a video file
    """
    # get size of image/video
    result = PIL.Image.open(file_name)
    (img_width, img_height) = result.size
    # initiate video writer
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('{}.avi'.format(file_name[:-4]),fourcc, fps, (img_width,img_height))
    # if video_length is specified, calculate new total_frames
    if not video_length == 0:
        total_frames = int(video_length * fps)
    # write frames to video file
    for i in range(total_frames):
        if img_dir is not None:
            img_name = os.path.join(img_dir, 'img_{}.png'.format(i))
            frame = cv2.imread(img_name)
            out.write(frame)
        print('{}/{} frame'.format(i+1,total_frames))
    out.release()


if __name__ == "__main__":
    img_dir, file_name = create_dream_frames(target_dream_layer=3,total_frames=10,zoom_in=True)
    create_dream_video(img_dir=img_dir,total_frames=10)
