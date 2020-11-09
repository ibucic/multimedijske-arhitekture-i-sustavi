import sys
import math
# import time


# py .\ivan_bucic_dz1.py lenna.ppm 0 output.txt


# Data content to pixels
def data_to_pixels(data_content, bytes_for_pixel, bytes_per_row):
    content_rows = [content[i: i + bytes_per_row] for i in range(0, len(data_content), bytes_per_row)]
    pixels = list()
    for content_row in content_rows:
        current_row = list()
        for i in range(0, len(content_row), bytes_for_pixel):
            pixel = [int(element) for element in content_row[i: i + bytes_for_pixel]]
            current_row.append(pixel)
        pixels.append(current_row)

    return pixels


# RGB to YCbCr with shifting
def RGB_to_YCbCr(image_width, image_height, pixel_image, shift=-128, to_shift=False):
    image = [[[] for _ in range(image_width)] for _ in range(image_height)]

    for i in range(width):
        for j in range(height):
            RGB = [pixel_image[i][j][k] if pixel_image[i][j][k] < 256 else 255 for k in range(3)]
            Y = 0.299 * RGB[0] + 0.587 * RGB[1] + 0.114 * RGB[2]
            Cb = -0.1687 * RGB[0] - 0.3313 * RGB[1] + 0.5 * RGB[2] + 128
            Cr = 0.5 * RGB[0] - 0.4187 * RGB[1] - 0.0813 * RGB[2] + 128

            if to_shift:
                image[i][j] = [Y + shift, Cb + shift, Cr + shift]
            else:
                image[i][j] = [Y, Cb, Cr]

    return image


# Shift image domain
def shift_image_domain(image_width, image_height, image, shift=-128):
    for i in range(image_width):
        for j in range(image_height):
            image[i][j][0] += shift
            image[i][j][1] += shift
            image[i][j][2] += shift


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


# DCT-2D
def DCT_2D(image):
    DCT_2D_image = list()
    for row_of_blocks in image:
        current_row_of_blocks = list()
        for block in row_of_blocks:
            current_block = DCT_2D_on_block(block, block_size=8)
            current_row_of_blocks.append(current_block)
        DCT_2D_image.append(current_row_of_blocks)

    return DCT_2D_image


# DCT-2D on block (8x8)
def DCT_2D_on_block(query_block, block_size=8):
    current_block = list()
    for u in range(block_size):
        current_row = list()
        for v in range(block_size):
            current_value = [0.0, 0.0, 0.0]
            # C = 0.25 * (0.5 if (v == 0 or u == 0) else 1.0)
            C = 0.25 * ((1 / math.sqrt(2) if u == 0 else 1.0) * (1 / math.sqrt(2) if v == 0 else 1.0))

            for i, row_in_block in enumerate(query_block):
                cos_u = math.cos(((2 * i + 1) * u * math.pi) / 16)
                for j, pixel in enumerate(row_in_block):
                    cos_v = math.cos(((2 * j + 1) * v * math.pi) / 16)
                    for pixel_id in range(3):
                        current_value[pixel_id] += pixel[pixel_id] * cos_u * cos_v
            for value_id in range(3):
                current_value[value_id] *= C
            current_row.append(current_value)
        current_block.append(current_row)

    return current_block


# Quantization tensor
def create_quantization_tensor(block_size=8):
    # Create K tables
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

    tensor = list()
    for i in range(block_size):
        current_row = list()
        for j in range(block_size):
            current_row.append([K_table1[i][j], K_table2[i][j], K_table2[i][j]])
        tensor.append(current_row)

    return tensor


# Quantize
def quantize(image):
    quantize_image = list()
    quantization_tensor = create_quantization_tensor()
    for row_of_blocks in image:
        current_row_of_blocks = list()
        for block in row_of_blocks:
            current_block = quantize_block(block, quantization_tensor)
            current_row_of_blocks.append(current_block)
        quantize_image.append(current_row_of_blocks)

    return quantize_image


# Quantize block
def quantize_block(query_block, quantization_tensor):
    current_block = list()
    for i, row_in_block in enumerate(query_block):
        current_row_in_block = list()
        for j, pixel in enumerate(row_in_block):
            Y = int(round(pixel[0] / quantization_tensor[i][j][0]))
            Cb = int(round(pixel[1] / quantization_tensor[i][j][1]))
            Cr = int(round(pixel[2] / quantization_tensor[i][j][2]))
            current_row_in_block.append([Y, Cb, Cr])
        current_block.append(current_row_in_block)

    return current_block


# Check file type
def check_file_type(type_of_file, file_name, to_print=False):
    if type_of_file == file_name:
        if to_print:
            print('File is ' + file_name + '.\n')
    else:
        if to_print:
            print('File is not ' + file_name + '.\n')
        exit(1)


# Create YCbCr matrix
def create_YCbCr_matrix(block):
    YCbCr_matrix = [[] for _ in range(3)]
    for row_in_block in block:
        YCbCr_row = [[] for _ in range(3)]
        for pixel in row_in_block:
            for i in range(3):
                YCbCr_row[i].append(pixel[i])
        for i in range(3):
            YCbCr_matrix[i].append(YCbCr_row[i])

    return YCbCr_matrix


# Print YCbCr matrix
def print_YCbCr_matrix(matrix):
    matrix_string = ''
    for i in range(3):
        matrix_string += '\n'.join([''.join(['{:3}'.format(item) for item in row]) for row in matrix[i]]) + '\n\n'

    print(matrix_string)


# Save YCvCr matrix with choice of printing YCvCb matrix
def save_YCbCr_matrix(matrix, file_name, to_print=False):
    matrix_string = ''
    for i in range(3):
        matrix_string += '\n'.join([''.join(['{:3}'.format(item) for item in row]) for row in matrix[i]]) + '\n\n'

    with open(file_name, 'w') as f:
        f.write('%s\n' % matrix_string)

    if to_print:
        print(matrix_string)


if __name__ == '__main__':

    # time_s = time.time()

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

        max_value = int(file.readline().decode('utf8').strip())

        bytes_per_pixel = 3 if int(max_value) < 256 else 6

        content = file.read()
        content_pixels = data_to_pixels(content, bytes_per_pixel, bytes_per_row=(width * bytes_per_pixel))

    block_index = int(sys.argv[2])
    file_output = sys.argv[3]

    # RGB to YCbCr with shift
    image_YCbCr = RGB_to_YCbCr(width, height, content_pixels, to_shift=True)
    # print(f"Runtime of RGB to YCbCr is {time.time() - time_s}s")

    # Divide in blocks
    image_YCbCr_blocks = block_divide(width, height, image_YCbCr, block_width=8, block_height=8)
    # print(f"Runtime of the block divide is {time.time() - time_s}s")

    # # # DCT-2D # # #
    # image_DCT_2D = DCT_2D(image_YCbCr_blocks)
    # # # Quantize # # #
    # image_quantize = quantize(image_DCT_2D)

    # DCT-2D on block of interest
    DCT_2D_block = DCT_2D_on_block(block_of_interest(image_YCbCr_blocks, block_index), block_size=8)
    # print(f"Runtime of DCT-2D is {time.time() - time_s}s")
    # Quantize block of interest
    quantized_block_of_interest = quantize_block(DCT_2D_block, create_quantization_tensor())
    # print(f"Runtime of quantize is {time.time() - time_s}s")

    # Create, save and print created YCbCr matrix
    matrix_YCbCr = create_YCbCr_matrix(quantized_block_of_interest)
    save_YCbCr_matrix(matrix_YCbCr, file_output, to_print=True)
