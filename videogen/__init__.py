import os
import tempfile
from subprocess import call

from pdf2image import convert_from_path
from gtts import gTTS

__author__ = ['slideit']

## Sometimes ffmpeg is avconv
FFMPEG_NAME = 'ffmpeg'
# FFMPEG_NAME = 'avconv'
pdf_path = "slidev/slides-export.pdf"
output_path = "output.mp4"

def generate_video(content):
    with tempfile.TemporaryDirectory() as temp_path:
        images_from_path = convert_from_path(pdf_path)
        for i, image in enumerate(images_from_path):
            image_path = os.path.join(temp_path, 'frame_{}.jpg'.format(i))
            audio_path = os.path.join(temp_path, 'frame_{}.mp3'.format(i))
            image.save(image_path)
            if (i==0):
                #The empty spaces for pause
                speaker_notes = content["title"] + '      ' + content["subtitle"]
            else:
                speaker_notes = ' '.join(content["slides"][i-1])

            generate_audio_from_text(speaker_notes, audio_path)
            generate_video_from_image(image_path, audio_path, temp_path, i)

        video_list = [os.path.join(temp_path, 'frame_{}.ts'.format(i)) \
                        for i in range(len(images_from_path))]
        video_list_str = 'concat:' + '|'.join(video_list)
        ffmpeg_concat(video_list_str, output_path)

def ffmpeg_concat(video_list_str, out_path):
    call([FFMPEG_NAME, '-y', '-f', 'mpegts', '-i', '{}'.format(video_list_str),
          '-c', 'copy', '-bsf:a', 'aac_adtstoasc', out_path])

def generate_audio_from_text(text, output_path):
    tts = gTTS(text=text, lang='en')
    tts.save(output_path)

def generate_video_from_image(image_path, audio_path, temp_path, i):
    out_path_mp4 = os.path.join(temp_path, 'frame_{}.mp4'.format(i))
    out_path_ts = os.path.join(temp_path, 'frame_{}.ts'.format(i))
    call([FFMPEG_NAME, '-loop', '1', '-y', '-i', image_path, '-i', audio_path,
          '-c:v', 'libx264', '-tune', 'stillimage', '-c:a', 'aac',
          '-b:a', '192k', '-pix_fmt', 'yuv420p', '-shortest', out_path_mp4])
    call([FFMPEG_NAME, '-y', '-i', out_path_mp4, '-c', 'copy',
          '-bsf:v', 'h264_mp4toannexb', '-f', 'mpegts', out_path_ts])
    