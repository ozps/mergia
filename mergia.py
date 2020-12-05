#!/usr/local/bin/python3.6

import os
import sys
import shutil
import click
import pyheif
import numpy as np
import cv2
from PIL import Image
from tqdm import tqdm

@click.command()
@click.option('--src', required = True, help = 'Source path')
@click.option('--des', required = True, help = 'Destination path')
@click.option('--prefix', required = True, help = 'Media prefix')
@click.option('--start_num', default = 0, help = 'First media file number')
@click.option('--sort_media', default = 'True', help = 'Sort by last modified')
@click.option('--show_same', default = 'False', help = 'Show same media files')
@click.option('--show_unsupport', default = 'False', help = 'Show unsupport media format')

def merge_media(src, des, prefix, start_num, sort_media, show_same, show_unsupport):
    try:
        sort_media = eval(sort_media)
        show_same = eval(show_same)
        show_unsupport = eval(show_unsupport)
    except:
        print('Error: invalid show_same or show_unsupport')
        sys.exit(1)
    src_path, des_path = get_real_path(src, des)
    src_backup_path = src_path + '_backup'
    shutil.copytree(src_path, src_backup_path)
    all_media_extensions = set()
    all_media_files = list(filter(lambda x: not x.startswith('.'), os.listdir(src_path)))
    num_of_media_files = 0
    num_of_move_media_files = 0
    image_extensions = ['JPG', 'PNG']
    video_extensions = ['MOV', 'MP4']
    live_extensions = ['HEIC']
    support_extensions = image_extensions + video_extensions + live_extensions
    duplicate_indexes = set()
    if src_path == '':
        print('Error: source path does not exist')
        sys.exit(1)
    print('---------- Get all extensions ----------')
    for media_filename in tqdm(all_media_files):
        media_extension = os.path.splitext(media_filename)[1][1:].upper()
        if len(media_extension) > 0:
            all_media_extensions.add(media_extension)
        num_of_media_files += 1
    print('All extensions:', all_media_extensions)
    print('Number of all media files:', num_of_media_files)
    extension_counter = {ext: 0 for ext in all_media_extensions}
    print('---------- Move media processing ----------')
    for i in tqdm(range(num_of_media_files)):
        if i in duplicate_indexes:
            continue
        media_1_path = os.path.join(src_path, all_media_files[i])
        media_1_extension = os.path.splitext(media_1_path)[1][1:].upper()
        for j in range(i + 1, num_of_media_files):
            if j in duplicate_indexes:
                continue
            media_2_path = os.path.join(src_path, all_media_files[j])
            media_2_extension = os.path.splitext(media_2_path)[1][1:].upper()
            if media_1_extension == media_2_extension: # Same extensions
                if media_1_extension in image_extensions: # Image
                    image_1 = Image.open(media_1_path)
                    image_2 = Image.open(media_2_path)
                    if list(image_1.getdata()) == list(image_2.getdata()):
                        duplicate_indexes.add(j) # Save duplicate image index
                        if show_same: print('SAME IMAGE:', media_1_path, '--', media_2_path)
                elif media_1_extension in video_extensions: # Video
                    video_1 = cv2.VideoCapture(media_1_path)
                    property_id = int(cv2.CAP_PROP_FRAME_COUNT)
                    length_video_1 = int(cv2.VideoCapture.get(video_1, property_id))
                    video_2 = cv2.VideoCapture(media_2_path)
                    length_video_2 = int(cv2.VideoCapture.get(video_2, property_id))
                    if length_video_1 == length_video_2:
                        frame = 0
                        is_same_video = True
                        while frame < length_video_1:
                            ret_1, frame_1 = video_1.read()
                            ret_2, frame_2 = video_2.read()
                            # Compare video by frame if different, continue
                            if not np.array_equal(frame_1, frame_2):
                                is_same_video = False
                                break
                            frame += (length_video_1 // 5) - 1
                        if is_same_video:
                            duplicate_indexes.add(j) # Save duplicated video index
                            if show_same: print('SAME VIDEO:', media_1_path, '--', media_2_path)
                elif media_1_extension in live_extensions: # Live
                    live_1 = pyheif.read_heif(media_1_path)
                    image_from_live_1 = Image.frombytes(mode = live_1.mode, size = live_1.size, data = live_1.data)
                    live_2 = pyheif.read_heif(media_2_path)
                    image_from_live_2 = Image.frombytes(mode = live_2.mode, size = live_2.size, data = live_2.data)
                    if list(image_from_live_1.getdata()) == list(image_from_live_2.getdata()):
                        duplicate_indexes.add(j) # Save duplicated live index
                        if show_same: print('SAME LIVE:', media_1_path, '--', media_2_path)
                else:
                    if show_unsupport: print('Error: unsupported', media_1_extension, 'media format')
                    break
            else:
                continue # Different extensions
        # Save media at index i if in supported extensions
        if media_1_extension in support_extensions:
            extension_counter[media_1_extension] += 1
            # Create folder due to extension if not exist
            if not os.path.exists(des_path):
                os.makedirs(des_path)
            media_src = os.path.join(src_path, all_media_files[i])
            str_of_move_media_files = str(num_of_move_media_files)
            full_media_extension = '.' + media_1_extension
            media_des = os.path.join(des_path, prefix[:-len(str_of_move_media_files)] + str_of_move_media_files + full_media_extension)
            # Move file with prefix name
            move_media_des = shutil.move(media_src, media_des)
            print('Moved media:', move_media_des)
            num_of_move_media_files += 1
        else:
            if show_unsupport: print('Error: unsupported', media_1_extension, 'media format')
    src_dup_path = src_path + '_duplicated'
    if os.path.exists(src_dup_path):
        shutil.rmtree(src_dup_path)
    os.rename(src_path, src_dup_path)
    os.rename(src_backup_path, src_path)
    print('---------- Moved done ----------')
    print('Each moved media extensions:', extension_counter)
    print('Number of moved media files:', num_of_move_media_files)
    if sort_media: get_sorted_media(des_path, prefix, start_num)
    sys.exit(0)

def get_real_path(src, des):
    src = os.path.join('/', src)[1:]
    des = os.path.join('/', des)[1:]
    join_src_path = os.path.join(os.getcwd(), src)
    if os.path.exists(join_src_path):
        join_des_path = os.path.join(os.getcwd(), des)
        if os.path.exists(join_des_path):
            shutil.rmtree(join_des_path)
        return (join_src_path, join_des_path)
    else:
        print('Error: invalid src')
        sys.exit(1)

def get_sorted_media(des_path, prefix, start_num):
    print('---------- Sort media processing ----------')
    num_of_sorted_media_files = start_num
    sorted_path = des_path + '_sorted'
    if os.path.exists(sorted_path):
        shutil.rmtree(sorted_path)
    os.makedirs(sorted_path)
    all_media_files = list(filter(lambda x: not x.startswith('.'), os.listdir(des_path)))
    last_modified_dict = {media_filename: os.path.getmtime(os.path.join(des_path, media_filename)) for media_filename in all_media_files}
    sorted_last_modified = sorted(last_modified_dict.items(), key = lambda x: x[1])
    for media_filename, _ in tqdm(sorted_last_modified):
        media_src = os.path.join(des_path, media_filename)
        str_of_sorted_media_files = str(num_of_sorted_media_files)
        media_extension = os.path.splitext(media_filename)[1][1:].upper()
        full_media_extension = '.' + media_extension
        media_des = os.path.join(sorted_path, prefix[:-len(str_of_sorted_media_files)] + str_of_sorted_media_files + full_media_extension)
        # Move file with prefix name
        sorted_media_des = shutil.move(media_src, media_des)
        print('Sorted media:', sorted_media_des)
        num_of_sorted_media_files += 1
    os.rmdir(des_path)
    print('---------- Sorted done ----------')

if __name__ == '__main__':
    merge_media()
