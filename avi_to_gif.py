'''
Convert the avi video file to gif
'''
import moviepy.editor as mp

if __name__ == "__main__":
    clip = mp.VideoFileClip("test.avi")
    clip.write_gif("test.gif")
