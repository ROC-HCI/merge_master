#!/usr/bin/env python
"""
------------------------------------------------------------------------
  converts all webm files in current directory to mp4

  There are many issues with videos. Below is the technique that appears to 
  produce the best result.  Doing all these steps at once in a single 
  FFMPEG command do not work (for various known and unknown reasons).

------------------------------------------------------------------------
"""
import glob
import os
from sets import Set


#------------------------------------------------------------------------
def convert2mp4():
    """ convert to mp4 """

    files =  glob.glob('*.webm')
    for fname in files:
        root = fname.split('.')[0]
        fname_mp4 = root + '.mp4'
        # if mp4 file already exists skip
        if(os.path.exists(fname_mp4)):
          continue
        print('converting ' + fname + ' to mp4')
        cmd = "ffmpeg -i " + fname + \
              ' -vcodec libx264 -pix_fmt yuv420p -profile:v baseline ' + \
              ' -preset slow -crf 22 -movflags +faststart ' + fname_mp4
        
        os.system(cmd)
        # TODO capture log

#------------------------------------------------------------------------
def extract_wav():
    """ extracts a .wav file from a .mp4 file """

    files =  glob.glob('*.mp4')
    for fname in files:
        root = fname.split('.')[0]
        fname_wav = root + '.wav'
        # skip if wav file already exists
        if(os.path.exists(fname_wav)):
          print('WARNING: ' + fname_wav + ' exists, skipping.\n')
          continue
        print('  extracting wav from ' + fname + '\n')
        cmd = "ffmpeg -async 1 -i " + fname + ' ' + fname_wav
        
        os.system(cmd)
        # TODO save log



#------------------------------------------------------------------------
def merge_wavs(wav_file1, wav_file2, wav_file_out):
    """ merges two wav files while preserving length """

    print('  MERGING WAV FILES: ' + wav_file1 + ' and ' + wav_file2)
    print(' --> ' + wave_file_out + '\n')

    if(!os.path.exists(wav_file1)):
      raise ValueError(wav_file1 + " file does not exist.")
    if(!os.path.exists(wav_file2)):
      raise ValueError(wav_file2 + " file does not exist.")
    if(!os.path.exists(wav_file_out)):
      raise ValueError(wav_file_out + " file does not exist.")

    cmd = 'ffmpeg  -i ' +  wave_file1 + ' -i $2 -filter_complex ' + \
          'amerge -ac 2 ' + wave_file_out
    os.system(cmd)
    # TODO save log

#------------------------------------------------------------------------
def merge_mp4s(infile1, infile2, outfile):
    """ merges two mp4 file into a new side by side mp4 file """

    cmd = 'ffmpeg  -i ' + infile1 + ' -i ' + infile2 + \
          ' -filter_complex "[0:v]setpts=PTS-STARTPTS, pad=iw*2:ih[bg]; [1:v]setpts=PTS-STARTPTS[fg]; [bg][fg]overlay=w;  amerge, pan=stereo:c0<c0+c2:c1<c1+c3" ' + outfile

    # TODO: break into multiple lines

    # NOTE: we could probably remove the audio processing steps in the 
    # above command.  However, removing may cause
    # timing/synchronization/length or other issues.

    os.system(cmd)
    # TODO save log
    
#------------------------------------------------------------------------
def remove_audio(infile, outfile):
    """ creates a new mp4 file without audio  """

    if(!os.path.exists(infile)):
      raise ValueError(infile + " file does not exist.")

    cmd = 'ffmpeg -i ' + infile + ' -c copy -an ' + outfile
    os.system(cmd)
    # TODO save log


#------------------------------------------------------------------------
def pair_steps():
    """ Before: a directory of mp4 files and wav files """
   
    roots = set()
    mp4_list = glob.glob('*.mp4')
    for mp4_file in mp4_files:
        fname_split = mp4_file.split('-')
        root = '-'.join(fsplit[0:6])
        roots.add(root)    

    for root in roots:

        # merge wav
        wav_files = glob.glob(root + '*')
        assert(len(wav_files == 2)
        merge_wavs(wav_files[0], wav_files[1], root + '.wav')

        # merge mp4
        merge_mp4s()

        # remove audio from mp4
        remove_audio()

        # merge merged audio and video
        merge_av()


#------------------------------------------------------------------------
def do_all():
    convert2mp4()
    extract_wav()
    


#------------------------------------------------------------------------
do_all()
