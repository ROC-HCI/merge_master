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
import logging

logging.basicConfig(level=logging.DEBUG)
'''
If you want to set the logging level from a command-line option such as:
  --log=INFO
'''

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
        logging.info('converting ' + fname + ' to mp4')
        #cmd = "ffmpeg -i " + fname + \
        #      ' -vcodec libx264 -pix_fmt yuv420p -profile:v baseline ' + \
        #      ' -preset slow -crf 22 -movflags +faststart ' + fname_mp4
        cmd = "ffmpeg -i " + fname + \
              ' -vcodec libx264 -pix_fmt yuv420p -profile:v baseline ' + \
              ' -preset slow -r 15 -crf 22 -movflags +faststart ' + fname_mp4
       
        os.system(cmd)

        #proc = subprocess.Popen(["cat", "/etc/services"], stdout=subprocess.PIPE, shell=True)
        #(out, err) = proc.communicate()
        #print("program output:", out)        
        
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
            logging.warning(fname_wav + ' exists, skipping.\n')
            continue
        logging.info('  extracting wav from ' + fname + '\n')
        cmd = "ffmpeg -async 1 -i " + fname + ' ' + fname_wav
        
        os.system(cmd)
        # TODO save log



#------------------------------------------------------------------------
def merge_wavs(wav_file1, wav_file2, wav_file_out):
    """ merges two wav files while preserving length """

    logging.info('  MERGING WAV FILES: ' + wav_file1 + ' and ' + wav_file2)
    logging.info(' --> ' + wav_file_out + '\n')

    if(not os.path.exists(wav_file1)):
        raise ValueError(wav_file1 + " file does not exist.")
    if(not os.path.exists(wav_file2)):
        raise ValueError(wav_file2 + " file does not exist.")
    if(os.path.exists(wav_file_out)):
        logging.warning(wav_file_out + ' exists, skipping.\n')
        return

    cmd = 'ffmpeg  -i ' +  wav_file1 + ' -i ' + wav_file2 +' -filter_complex ' + \
          'amerge -ac 2 ' + wav_file_out
    os.system(cmd)
    # TODO save log

#------------------------------------------------------------------------
def merge_mp4s(infile1, infile2, outfile):
    """ merges two mp4 file into a new side by side mp4 file """
    
    if(os.path.exists(outfile)):
        logging.warning(outfile + ' exists, skipping.\n')
        return

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

    if(os.path.exists(outfile)):
        logging.warning(outfile + ' exists, skipping.\n')
        return
    
    if( not os.path.exists(infile)):
        raise ValueError(infile + " file does not exist.")

    cmd = 'ffmpeg -i ' + infile + ' -c copy -an ' + outfile
    os.system(cmd)
    # TODO save log

#------------------------------------------------------------------------
def merge_av(wav_file, mp4_file, outfile):
    """ creates a new mp4 file with audio from wav and vid from mp4  """

    if(os.path.exists(outfile)):
        logging.warning(outfile + ' exists, skipping.\n')
        return

    if(not os.path.exists(wav_file)):
        raise ValueError(wav_file + " file does not exist.")

    if(not os.path.exists(mp4_file)):
        raise ValueError(wav_file + " file does not exist.")

    cmd = 'ffmpeg -i ' + wav_file + ' -i ' + mp4_file + \
          ' -c:v libx264 -c:a libmp3lame -shortest ' + outfile
    os.system(cmd)
    # TODO save log

#------------------------------------------------------------------------
def pair_steps():
    """ Before: a directory of mp4 files and wav files """
   
    roots = set()
    mp4_files = glob.glob('*.mp4')
    for mp4_file in mp4_files:
        mp4_file = mp4_file.replace('.','-')
        fname_split = mp4_file.split('-')
        root = '-'.join(fname_split[0:6])
        roots.add(root)    

    for root in roots:

        # merge wav
        wav_files = glob.glob(root + '*.wav')
        assert(len(wav_files) >= 2), 'root=' + root
        merge_wavs(wav_files[0], wav_files[1], root + '.wav')

        # merge mp4
        mp4_files = glob.glob(root + '*.mp4')
        assert(len(mp4_files) >= 2), mp4_files
        merge_mp4_fname = root + '-merged.mp4'
        merge_mp4s(mp4_files[0], mp4_files[1], merge_mp4_fname)

        # remove audio from mp4
        merge_mp4_noa_fname = root + '-merged.noa.mp4'
        remove_audio(merge_mp4_fname, merge_mp4_noa_fname)

        # merge merged audio and video
        merge_av(root + '.wav', root + '-merged.noa.mp4', root + '.mp4')


#------------------------------------------------------------------------
def do_all():
    convert2mp4()
    extract_wav()
    pair_steps()

#------------------------------------------------------------------------
do_all()
