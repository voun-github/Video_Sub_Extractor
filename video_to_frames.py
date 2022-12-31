import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import cv2 as cv
from tqdm import tqdm

logger = logging.getLogger(__name__)


def extract_frames(video_path: Path, frames_dir: Path, key_area: tuple, start: int, end: int, every: int) -> int:
    """
    Extract frames from a video using OpenCVs VideoCapture
    :param video_path: path of the video
    :param frames_dir: the directory to save the frames
    :param key_area: coordinates of the frame containing subtitle
    :param start: start frame
    :param end: end frame
    :param every: frame spacing
    :return: count of images saved
    """

    x1, y1, x2, y2 = key_area

    capture = cv.VideoCapture(str(video_path))  # open the video using OpenCV

    if start < 0:  # if start isn't specified lets assume 0
        start = 0
    if end < 0:  # if end isn't specified assume the end of the video
        end = int(capture.get(cv.CAP_PROP_FRAME_COUNT))

    capture.set(1, start)  # set the starting frame of the capture
    frame = start  # keep track of which frame we are up to, starting from start
    while_safety = 0  # a safety counter to ensure we don't enter an infinite while loop (hopefully we won't need it)
    saved_count = 0  # a count of how many frames we have saved

    while frame < end:  # let's loop through the frames until the end

        _, image = capture.read()  # read an image from the capture

        if while_safety > 500:  # break the while if our safety max's out at 500
            break

        # sometimes OpenCV reads Nones during a video, in which case we want to just skip
        if image is None:  # if we get a bad return flag or the image we read is None, lets not save
            while_safety += 1  # add 1 to our while safety, since we skip before incrementing our frame variable
            continue  # skip

        if frame % every == 0:  # if this is a frame we want to write out based on the 'every' argument
            while_safety = 0  # reset the safety count
            # crop and save key area
            cropped_frame = image[y1:y2, x1:x2]
            frame_position = capture.get(cv.CAP_PROP_POS_MSEC)
            save_name = f"{frames_dir}/{frame_position}.jpg"  # create the save path
            cv.imwrite(save_name, cropped_frame)  # save the extracted image
            saved_count += 1  # increment our counter by one

        frame += 1  # increment our frame count

    capture.release()  # after the while has finished close the capture
    return saved_count  # and return the count of the images we saved


def video_to_frames(video_path: Path, frames_dir: Path, key_area: tuple, every: int = 2, chunk_size: int = 250) -> None:
    """
    Extracts the frames from a video using multiprocessing
    :param video_path: path to the video
    :param frames_dir: directory to save the frames
    :param key_area: coordinates of the frame containing subtitle
    :param every: extract every this many frames
    :param chunk_size: how many frames to split into chunks (one chunk per cpu core process)
    :return: path to the directory where the frames were saved, or None if fails
    """

    capture = cv.VideoCapture(str(video_path))  # load the video
    frame_count = int(capture.get(cv.CAP_PROP_FRAME_COUNT))  # get its total frame count
    capture.release()  # release the capture straight away

    # ignore chunk size if it's greater than frame count
    chunk_size = chunk_size if frame_count > chunk_size else frame_count - 1

    if frame_count < 1:  # if video has no frames, might be and opencv error
        logger.error("Video has no frames. Check your OpenCV installation")
        return None  # end function call

    # split the frames into chunk lists
    frame_chunks = [[i, i + chunk_size] for i in range(0, frame_count, chunk_size)]
    # make sure last chunk has correct end frame, also handles case chunk_size < total
    frame_chunks[-1][-1] = min(frame_chunks[-1][-1], frame_count - 1)
    logger.debug(f"Frame chunks = {frame_chunks}")

    prefix = "Extracting frames from video chunks"  # a prefix string to be printed in progress bar
    logger.debug("Using multiprocessing for extracting frames")

    # execute across multiple cpu cores to speed up processing, get the count automatically
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(extract_frames, video_path, frames_dir, key_area, f[0], f[1], every)
                   for f in frame_chunks]  # submit the processes: extract_frames(...)
        pbar = tqdm(total=len(frame_chunks), desc=prefix, colour="green")
        for f in as_completed(futures):  # as each process completes
            error = f.exception()
            if error:
                logger.exception(error)
            pbar.update()
        pbar.close()
    logger.info("Done extracting frames from video!")