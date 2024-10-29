from PIL import Image
import os

def remove_non_ascii(text):
    return ''.join(char for char in text if ord(char) <= 127)


#Convert message to binary
def message_binary(message):
    #Go through each character in string, convert to ASCII, and then format it into binary
    #Join all binary bits with ''. No whitespace
    binary = ''.join(format(ord(char), '08b') for char in message)
    return binary

# Modify LSB of pixel
def modify_pixel(pixel, bit):
    if len(pixel) == 4:  # RGBA
        r, g, b, a = pixel
        r = (r & ~1) | int(bit[0])
        g = (g & ~1) | int(bit[1])
        b = (b & ~1) | int(bit[2])
        return (r, g, b, a)
    elif len(pixel) == 3:  # RGB
        r, g, b = pixel
        r = (r & ~1) | int(bit[0])
        g = (g & ~1) | int(bit[1])
        b = (b & ~1) | int(bit[2])
        return (r, g, b)
    elif len(pixel) == 1:  # Grayscale (PGM)
        g = pixel[0]
        g = (g & ~1) | int(bit[0])
        return (g,)


def encode_message(image, output, message):
    # Open and convert image to RGB or RGBA if necessary
    img = Image.open(image)
    if img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGB')  # Convert grayscale to RGB

    pixels = img.load()

    # Convert message to binary
    ascii_message = remove_non_ascii(message)
    delimiter = message_binary("####END####")
    binary_message = message_binary(ascii_message) + delimiter

    binary_index = 0
    width, height = img.size

    # Starting from first pixel, insert message
    for y in range(height):
        for x in range(width):
            if binary_index < len(binary_message):
                pixel = pixels[x, y]

                # Ensure pixel is a tuple
                if isinstance(pixel, int):
                    pixel = (pixel, pixel, pixel)  # Grayscale to RGB

                # Take 3 bits from the binary text
                bit_chunk = binary_message[binary_index:binary_index + 3].ljust(3, '0')
                # Modify the pixel's RGB values
                new_pixel = modify_pixel(pixel, bit_chunk)
                pixels[x, y] = new_pixel
                binary_index += 3

    # Save the modified image
    img.save(output)


#list images function
def list_images(folder):
    images = [f for f in os.listdir(folder)]
    return images

def list_files(folder):
    files = [f for f in os.listdir(folder)]
    return files


#Get user input for image being used and file
#input

hide_another = True
while hide_another:
    #Information about what's supported
    print("Supported image types: BMP, PPM, PGM")
    print("Hides Text Only\n")
    print("Welcome to Command Line Interface...\n")

    #Display image names in Image folder
    image_folder = "Images folder"
    images_in_folder = list_images(image_folder)
    for img in images_in_folder:
        print(f" - {img}")

    #get image input
    print("\n")
    image_name = input("Please enter image name: ")
    image_folder = "Images folder"
    image_path = os.path.join(image_folder, image_name)

    # Create output image folder if it doesn't exist
    output_image_input = input("Please enter output image name: ")
    output_folder = "Output image folder"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)  # Create the folder
    output_path = os.path.join(output_folder, output_image_input)


    #Display Secret files choices
    Secret_files_folder = "Secret files folder"
    files_in_folder = list_files(Secret_files_folder)
    for files in files_in_folder:
        print(f" - {files}")

    #Get text input
    print("\n")
    text_name = input("Please enter text file: ")
    text_folder = "Secret files folder"
    text_file = os.path.join(text_folder, text_name)

    with open(text_file, "r", encoding="utf-8-sig") as file:
        message = file.read()


    encode_message(image_path, output_path, message)

    another = input("Would you like to encode another message? y/n: ")
    if another == "n":
        hide_another = False


