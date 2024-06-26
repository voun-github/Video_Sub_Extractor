import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import custom_paddleocr.paddleocr as cp
import utilities.utils as utils

logger = logging.getLogger(__name__)

MODEL_PATH = Path(__file__).parent.parent / "models" / cp.DEFAULT_OCR_MODEL_VERSION / utils.Config.ocr_rec_language
paddle_ocr = cp.PaddleOCR(
    det_model_dir=f"{MODEL_PATH}/det",
    rec_model_dir=f"{MODEL_PATH}/rec",
    cls_model_dir=f"{MODEL_PATH}/cls",
    use_angle_cls=True,
    lang=utils.Config.ocr_rec_language,
    show_log=False
)


def extract_bboxes(files: Path, drop_score: float = 0.9) -> list:
    """
    Returns the bounding boxes of detected texted in images.
    :param files: Directory with images for detection.
    :param drop_score: Filter the results by score and those results below this score will not be returned.
    """
    boxes = []
    for file in files.iterdir():
        result = paddle_ocr.ocr(str(file))
        result = result[0]
        if result:
            score = result[0][1][1]
            if score > drop_score:
                box = result[0][0]
                boxes.append(box)
    return boxes


def extract_text(text_output: Path, files: list) -> None:
    """
    Extract text from a frame using paddle ocr.
    :param text_output: directory for extracted texts.
    :param files: files with text for extraction.
    """
    for file in files:
        result = paddle_ocr.ocr(str(file))
        result = result[0]
        if result:
            text_list = [line[1][0] for line in result]
            text = " ".join(text_list)
            name = Path(f"{text_output}/{file.stem}.txt")
            with open(name, 'w', encoding="utf-8") as text_file:
                text_file.write(text)


def frames_to_text(frame_output: Path, text_output: Path) -> None:
    """
    Extracts the texts from frames using multiprocessing
    :param frame_output: directory of the frames
    :param text_output: directory for extracted texts
    """
    chunk_size = utils.Config.text_extraction_chunk_size  # Size of files given to each processor.
    # Number of processes to be used.
    ocr_max_processes = utils.Config.ocr_gpu_max_processes if utils.Config.use_gpu else None

    if utils.Process.interrupt_process:  # Cancel if process has been cancelled by gui.
        logger.warning("Text extraction process interrupted!")
        return

    logger.info("Starting text extraction from frames...")

    files = [file for file in frame_output.iterdir()]
    file_chunks = [files[i:i + chunk_size] for i in range(0, len(files), chunk_size)]

    prefix = "Text Extraction"
    logger.debug("Using multiprocessing for text extraction")

    with ProcessPoolExecutor(ocr_max_processes) as executor:
        futures = [executor.submit(extract_text, text_output, files) for files in file_chunks]
        for i, _ in enumerate(as_completed(futures)):  # as each  process completes
            utils.print_progress(i, len(file_chunks) - 1, prefix)
    logger.info("Text extractions done!")
