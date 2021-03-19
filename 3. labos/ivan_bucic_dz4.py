import sys
import time

import numpy as np
from PIL import Image
from scipy.fftpack import dctn


# py .\ivan_bucic_dz4.py lenna.ppm 0 output.txt

# Divide components
def divide_image(image):
    Y, Cb, Cr = list(), list(), list()
    for row in image:
        Y_row, Cb_row, Cr_row = list(), list(), list()
        for pixel in row:
            Y_row.append(pixel[0])
            Cb_row.append(pixel[1])
            Cr_row.append(pixel[2])
        Y.append(Y_row)
        Cb.append(Cb_row)
        Cr.append(Cr_row)
    return Y, Cb, Cr


# Divide in blocks
def block_divide(image_width, image_height, image, block_width=8, block_height=8):
    matrix_of_blocks = list()
    for width_offset in range(0, image_width - block_width + 1, block_width):
        current_row_of_blocks = list()
        for height_offset in range(0, image_height - block_height + 1, block_height):
            current_block = list()
            for i in range(width_offset, width_offset + 8):
                current_row_in_block = list()
                for j in range(height_offset, height_offset + 8):
                    current_row_in_block.append(image[i][j])
                current_block.append(current_row_in_block)
            current_row_of_blocks.append(current_block)
        matrix_of_blocks.append(current_row_of_blocks)

    return matrix_of_blocks


# Get block of interest
def block_of_interest(blocks_image, index_of_block_of_interest):
    if index_of_block_of_interest > (len(blocks_image) * len(blocks_image[0])):
        print("Invalid block index.")
        exit(1)
    else:
        block_row = index_of_block_of_interest // len(blocks_image)
        block_column = index_of_block_of_interest % len(blocks_image[0])

        return blocks_image[block_row][block_column]


# DCT
def DCT(Y_blocks, Cb_blocks, Cr_blocks):
    Y_DCT, Cb_DCT, Cr_DCT = list(), list(), list()
    for block_row_id in range(len(Y_blocks)):
        Y_DCT_row, Cb_DCT_row, Cr_DCT_row = list(), list(), list()
        for block_id in range(len(Y_blocks[0])):
            Y_DCT_row.append(dctn(Y_blocks[block_row_id][block_id], norm='ortho'))
            Cb_DCT_row.append(dctn(Cb_blocks[block_row_id][block_id], norm='ortho'))
            Cr_DCT_row.append(dctn(Cr_blocks[block_row_id][block_id], norm='ortho'))
        Y_DCT.append(Y_DCT_row)
        Cb_DCT.append(Cb_DCT_row)
        Cr_DCT.append(Cr_DCT_row)
    return np.array(Y_DCT), np.array(Cb_DCT), np.array(Cr_DCT)


# Quantize
def quantize(Y, Cb, Cr):
    K_table1 = [[16, 11, 10, 16, 24, 40, 51, 61],
                [12, 12, 14, 19, 26, 58, 60, 55],
                [14, 13, 16, 24, 40, 57, 69, 56],
                [14, 17, 22, 29, 51, 87, 80, 62],
                [18, 22, 37, 56, 68, 109, 103, 77],
                [24, 35, 55, 64, 81, 104, 113, 92],
                [49, 64, 78, 87, 103, 121, 120, 101],
                [72, 92, 95, 98, 112, 100, 103, 99]]
    K_table2 = [[17, 18, 24, 47, 99, 99, 99, 99],
                [18, 21, 26, 66, 99, 99, 99, 99],
                [24, 26, 56, 99, 99, 99, 99, 99],
                [47, 66, 99, 99, 99, 99, 99, 99],
                [99, 99, 99, 99, 99, 99, 99, 99],
                [99, 99, 99, 99, 99, 99, 99, 99],
                [99, 99, 99, 99, 99, 99, 99, 99],
                [99, 99, 99, 99, 99, 99, 99, 99]]
    for blocks_row_id in range(len(Y)):
        for block_id in range(len(Y[0])):
            Y[blocks_row_id][block_id] = np.round(Y[blocks_row_id][block_id] / K_table1)
            Cb[blocks_row_id][block_id] = np.round(Cb[blocks_row_id][block_id] / K_table2)
            Cr[blocks_row_id][block_id] = np.round(Cr[blocks_row_id][block_id] / K_table2)


# Check file type
def check_file_type(type_of_file, file_name, to_print=False):
    if type_of_file == file_name:
        if to_print:
            print('File is ' + file_name + '.\n')
    else:
        if to_print:
            print('File is not ' + file_name + '.\n')
        exit(1)


# Save YCvCr matrix with printing YCvCb matrix
def save_image(Y, Cb, Cr, query_block, file_name):
    Y_block = block_of_interest(Y, query_block)
    Cb_block = block_of_interest(Cb, query_block)
    Cr_block = block_of_interest(Cr, query_block)
    Y_string, Cb_string, Cr_string = '', '', ''
    for i in range(len(Y_block)):
        for j in range(len(Y_block[0])):
            Y_string += '{:3}'.format(str(int(Y_block[i][j]))) + ' '
            Cb_string += '{:3}'.format(str(int(Cb_block[i][j]))) + ' '
            Cr_string += '{:3}'.format(str(int(Cr_block[i][j]))) + ' '
        Y_string += '\n'
        Cb_string += '\n'
        Cr_string += '\n'
    print(Y_string + '\n' + Cb_string + '\n' + Cr_string)

    with open(file_name, 'w') as f:
        f.write('%s\n' % Y_string + '\n' + Cb_string + '\n' + Cr_string)


def main():
    time_s = time.time()

    if len(sys.argv) != 4:
        print('Invalid number of program args.\n')
        exit(1)

    # File reading
    with open(sys.argv[1], 'rb') as file:
        file_type = file.readline().decode('utf8').strip()
        check_file_type(file_type, 'P6', to_print=False)

        resolution = file.readline().decode('utf8').strip()
        width, height = resolution.split(' ')
        width, height = int(width), int(height)

    block_index = int(sys.argv[2])
    file_output = sys.argv[3]

    image_YCbCr = Image.open(sys.argv[1]).convert('YCbCr')
    image_YCbCr = np.array(image_YCbCr, dtype=np.int) - 128
    print(f"Runtime of RGB to YCbCr is {time.time() - time_s}s")

    Y, Cb, Cr = divide_image(image_YCbCr)

    # Divide in blocks
    Y_blocks = np.array(block_divide(width, height, Y, block_width=8, block_height=8))
    Cb_blocks = np.array(block_divide(width, height, Cb, block_width=8, block_height=8))
    Cr_blocks = np.array(block_divide(width, height, Cr, block_width=8, block_height=8))
    print(f"Runtime of the block divide is {time.time() - time_s}s")

    Y_DCT, Cb_DCT, Cr_DCT = DCT(Y_blocks, Cb_blocks, Cr_blocks)
    print(f"Runtime of DCT-2D is {time.time() - time_s}s")

    quantize(Y_DCT, Cb_DCT, Cr_DCT)
    print(f"Runtime of quantize is {time.time() - time_s}s")

    save_image(Y_DCT, Cb_DCT, Cr_DCT, block_index, file_output)

    print(f"Total time is {time.time() - time_s}s")


if __name__ == '__main__':
    main()
