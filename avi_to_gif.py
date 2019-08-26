import moviepy.editor as mp
clip = mp.VideoFileClip("test.avi")
clip.write_gif("test.gif")
