# from paddleocr import PaddleOCR

# OCR = PaddleOCR(enable_mkldnn=True, use_angle_cls=False, use_gpu=False)
# pic = 'doc/imgs/1.jpg'

# result = OCR.ocr(pic, cls=False)

# for idx in range(len(result)):
#     res = result[idx]
#     for line in res:
#         print(line)

# import os
# import cv2
# from paddleocr import PPStructure, draw_structure_result, save_structure_res

# table_engine = PPStructure(layout=False, show_log=True)
# save_folder = './output'
# img_path = 'ppstructure/docs/table/table.jpg'
# img = cv2.imread(img_path)
# result = table_engine(img, True)
# # import pdb 
# # pdb.set_trace()
# save_structure_res(result, save_folder, os.path.basename(img_path).split('.')[0])

# for line in result:
#     line.pop('img')
#     print(line)

import os

import cv2

from paddleocr import PPStructure, save_structure_res

table_engine = PPStructure(show_log=True, image_orientation=True)

save_folder = './output'
img_path = 'ppstructure/docs/table/1.png'
img = cv2.imread(img_path)
result = table_engine(img)
save_structure_res(result, save_folder, os.path.basename(img_path).split('.')[0])

for line in result:
    line.pop('img')
    print(line)
