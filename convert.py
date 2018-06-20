import cv2
import os
import img2pdf
import shutil

import imutils


def pdf2jpg(path_to_file):
    with open(path_to_file, 'rb') as f:
        pdf = f.read()
    new_path = path_to_file.replace('.PDF', '.jpg')

    startmark = b'\xff\xd8'
    startfix = 0
    endmark = b'\xff\xd9'
    endfix = 2
    i = 0

    njpg = 0
    while True:
        istream = pdf.find(b'stream', i)
        if istream < 0:
            break
        istart = pdf.find(startmark, istream, istream + 20)
        if istart < 0:
            i = istream + 20
            continue
        iend = pdf.find(b'endstream', istart)
        if iend < 0:
            raise Exception('Did not find end of stream!')
        iend = pdf.find(endmark, iend - 20)
        if iend < 0:
            raise Exception('Did not find end of JPG!')

        istart += startfix
        iend += endfix
        jpg = pdf[istart:iend]

        with open(new_path, 'wb') as jpgfile:
            jpgfile.write(jpg)

        njpg += 1
        i = iend
    return new_path


def sort_path_lambda(el):
    return int(el.split(os.sep)[-1].split('.')[0])


PDF_ROOT = 'path_to_dir_with_pdfs'
FINAL_PDF_NAME = 'output_name'
NEED_ORDER = True

# traverse root directory, and list directories as dirs and files as files
for root, dirs, files in os.walk(PDF_ROOT):
    path = root.split(os.sep)

    print(root)
    print((len(path) - 1) * '---', os.path.basename(root))

    new_dir = os.path.join(root, 'result')
    try:
        os.mkdir(new_dir)
    except FileExistsError:
        pass

    cropped_paths = []
    for file_name in files:
        if not file_name.upper().endswith('.PDF'):
            continue

        print(len(path) * '---', file_name)

        jpg_path = pdf2jpg(os.path.join(root, file_name))
        img = cv2.imread(jpg_path)
        crop_img = img[100:3650, 100:2700]
        rotated_cropped = imutils.rotate_bound(crop_img, 90)

        cropped_jpg_path = os.path.join(new_dir, file_name.replace('.PDF', '.jpg'))
        cv2.imwrite(cropped_jpg_path, rotated_cropped)
        cropped_paths.append(cropped_jpg_path)

    with open('{}.pdf'.format(FINAL_PDF_NAME), 'wb') as f:
        sorted_paths = sorted(cropped_paths, key=sort_path_lambda)
        f.write(img2pdf.convert([i for i in sorted_paths]))

    # clean up from intermediate artifacts
    shutil.rmtree(new_dir)
