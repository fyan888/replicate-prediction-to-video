import argparse
import subprocess

import ffmpeg
import replicate
import requests
from dotenv import load_dotenv

# load API key from .env file
load_dotenv()

# get args from the command line
parser = argparse.ArgumentParser()
parser.add_argument('--model', type=str, required=True)
parser.add_argument('--prompt', type=str, required=True)
args = parser.parse_args()
print(args.__dict__)

# make a temporary directory to store the files
import tempfile
temp_dir = tempfile.mkdtemp()
print("temp_dir: ", temp_dir)

# start the prediction
prediction_generator = replicate.models.get(args.model).predict(prompt=args.prompt, steps=100)
print("prediction_generator: ", prediction_generator)
print("waiting for output from the model. This can take a bit if the model is cold...")

# iterate over prediction responses
for index, url in enumerate(prediction_generator):

    # construct filename
    prefix = str(index).zfill(4) # 0001, 0002, etc.
    print(url)
    fileIndex = 0
    str = ''
    listFileName = f"{temp_dir}/mylist.txt"
    for u in url:
        uuid = u.split('/')[-2]
        extension = u.split('.')[-1] # jpg, png, etc
        fileIndex = fileIndex + 1
        filename = f"{temp_dir}/{fileIndex}.{extension}"
        str += f'file {filename}\n'
    
        # download and save the file
        data = requests.get(u)
        with open(filename, 'wb') as file:
            file.write(data.content)
    with open(listFileName, 'wb') as file:
        file.write(bytes(str.replace('\\', '\\\\'), 'utf-8'))

# create video from series of images and append a reversed copy of the video
# so it will play ping-pong style: start-to-finish-to-start
print(temp_dir)
print(extension)
input_pattern = f"{temp_dir}\\mylist.txt"
print('input patter = ' + input_pattern)
video_path = f"{temp_dir}\\output.mp4"
print('video_path = ' + video_path)
ffmpeg.input(input_pattern, r=1, f='concat', safe='0').output(video_path, pix_fmt='yuv420p').run() #.overwrite_output().run()


in1 = ffmpeg.input(f"{temp_dir}\\1.png", framerate=1)
v1 = in1.video
v2 = in1.video.filter('reverse')
in2 = ffmpeg.input(f"{temp_dir}\\2.png", framerate=1)
v12 = in2.video
v22 = in2.video.filter('reverse')
joined = ffmpeg.concat(v1, v2, v12, v22, v=1).node
# create video
video_path = f"{temp_dir}/output2.mp4"
print('video_path = ' + video_path)
ffmpeg.output(joined[0], video_path).overwrite_output().run()  #.run()

# create gif
# gif_path = f"{temp_dir}/output.gif"
# ffmpeg.output(joined[0], gif_path).run()

# print(video_path)
# subprocess.run(['open', video_path], check=True)

# print(gif_path)
# subprocess.run(['open', gif_path], check=True)

# subprocess.run(['open', temp_dir], check=True)

print("done!")
