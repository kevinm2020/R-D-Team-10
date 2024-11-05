import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import cv2
import numpy as np


# Calculate MSE
def get_mse(original_image, modified_image):
    original = np.array(original_image)
    modified = np.array(modified_image)
    mse = np.mean((original - modified) ** 2)
    return mse


# Calculate PSNR
def calculate_psnr(original_image, modified_image):
    mse = get_mse(original_image, modified_image)
    if mse == 0:
        return float('inf')  # Infinite PSNR if images are identical
    return 10 * np.log10(255.0 ** 2 / mse)


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


def encode_message(original_image_path, output_image_path, message_path):
    # Open and convert image to RGB or RGBA if necessary
    img = Image.open(original_image_path)
    if img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGB')  # Convert grayscale to RGB

    pixels = img.load()

    with open(message_path, "r", encoding="utf-8-sig") as file:
        message = file.read()


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
    img.save(output_image_path)



# Placeholder for extracting message from an image
def extract_message(stego_image_path):
    img = Image.open(stego_image_path)
    pixels = img.load()

    width, height = img.size

    char_bits = ""
    message = ""

    # Loop through each pixel
    for y in range(height):
        for x in range(width):
            pixel = pixels[x, y]

            # Determine if the image is grayscale (1 channel), RGB (3 channels), or RGBA (4 channels)
            if len(pixel) == 4:  # RGBA
                r, g, b, a = pixel
                colors = (r, g, b)  # Only modify RGB values, not alpha (a)
            elif len(pixel) == 3:  # RGB
                r, g, b = pixel
                colors = (r, g, b)
            elif len(pixel) == 1:  # Grayscale (PGM)
                g = pixel[0]
                colors = (g,)

            # Extract the LSB from each color channel
            for color in colors:
                char_bits += str(color & 1)

                # After collecting 8 bits, convert them into a character
                if len(char_bits) == 8:
                    char = chr(int(char_bits, 2))
                    message += char

                    # Clear the bits for the next character
                    char_bits = ""

                    # Stop extraction if the custom delimiter "####END####" is found
                    if "####END####" in message:
                        # Remove the delimiter and return the extracted message
                        return message.replace("####END####", "")

    return message

class SteganographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Steganography App")

        # Original Image and Message Frame
        self.frame1 = tk.Frame(root)
        self.frame1.pack(pady=10)

        self.original_image_label = tk.Label(self.frame1, text="Original Image:")
        self.original_image_label.grid(row=0, column=0)

        self.original_image_entry = tk.Entry(self.frame1, width=50)
        self.original_image_entry.grid(row=0, column=1)

        self.original_image_browse_button = tk.Button(self.frame1, text="Browse", command=self.browse_original_image)
        self.original_image_browse_button.grid(row=0, column=2)


        self.output_image_label = tk.Label(self.frame1, text="Output Image Path:")
        self.output_image_label.grid(row=1, column=0)

        self.output_entry = tk.Entry(self.frame1, width=50)
        self.output_entry.grid(row=1, column=1)

        self.output_image_browse_button = tk.Button(self.frame1, text="Browse", command=self.encode_image_entry)
        self.output_image_browse_button.grid(row=1, column=2)


        self.message_label = tk.Label(self.frame1, text="Message:")
        self.message_label.grid(row=2, column=0)

        self.message_entry = tk.Entry(self.frame1, width=50)
        self.message_entry.grid(row=2, column=1)

        self.message_file_browse_button = tk.Button(self.frame1, text="Browse Message File",
                                                    command=self.browse_message_file)
        self.message_file_browse_button.grid(row=2, column=2)

        self.encode_button = tk.Button(self.frame1, text="Encode", command=self.encode_message)
        self.encode_button.grid(row=3, columnspan=3)


        # Stego Image Frame
        self.frame2 = tk.Frame(root)
        self.frame2.pack(pady=10)

        self.stego_image_label = tk.Label(self.frame2, text="Stego Image:")
        self.stego_image_label.grid(row=0, column=0)

        self.stego_image_entry = tk.Entry(self.frame2, width=50)
        self.stego_image_entry.grid(row=0, column=1)

        self.stego_image_browse_button = tk.Button(self.frame2, text="Browse", command=self.browse_stego_image)
        self.stego_image_browse_button.grid(row=0, column=2)

        self.decode_button = tk.Button(self.frame2, text="Decode", command=self.decode_message)
        self.decode_button.grid(row=1, columnspan=3)

        self.decoded_message_display = tk.Text(self.frame2, height=5, width=50)
        self.decoded_message_display.grid(row=2, columnspan=3)

        # PSNR Frame
        self.frame3 = tk.Frame(root)
        self.frame3.pack(pady=10)

        self.psnr_original_label = tk.Label(self.frame3, text="Original Image for PSNR:")
        self.psnr_original_label.grid(row=0, column=0)

        self.psnr_original_entry = tk.Entry(self.frame3, width=50)
        self.psnr_original_entry.grid(row=0, column=1)

        self.psnr_original_browse_button = tk.Button(self.frame3, text="Browse", command=self.browse_psnr_original)
        self.psnr_original_browse_button.grid(row=0, column=2)

        self.psnr_modified_label = tk.Label(self.frame3, text="Modified Image for PSNR:")
        self.psnr_modified_label.grid(row=1, column=0)

        self.psnr_modified_entry = tk.Entry(self.frame3, width=50)
        self.psnr_modified_entry.grid(row=1, column=1)

        self.psnr_modified_browse_button = tk.Button(self.frame3, text="Browse", command=self.browse_psnr_modified)
        self.psnr_modified_browse_button.grid(row=1, column=2)

        self.psnr_calculate_button = tk.Button(self.frame3, text="Calculate PSNR", command=self.calculate_psnr_value)
        self.psnr_calculate_button.grid(row=2, columnspan=3)

        self.psnr_value_display = tk.Text(self.frame3, height=1, width=50)
        self.psnr_value_display.grid(row=3, columnspan=3)

        # Extracted Message Frame
        self.frame4 = tk.Frame(root)
        self.frame4.pack(pady=10)

        self.extract_image_label = tk.Label(self.frame4, text="Image to Extract Message From:")
        self.extract_image_label.grid(row=0, column=0)

        self.extract_image_entry = tk.Entry(self.frame4, width=50)
        self.extract_image_entry.grid(row=0, column=1)

        self.extract_image_browse_button = tk.Button(self.frame4, text="Browse", command=self.browse_extract_image)
        self.extract_image_browse_button.grid(row=0, column=2)

        self.extract_message_button = tk.Button(self.frame4, text="Extract Message", command=self.extract_message)
        self.extract_message_button.grid(row=1, columnspan=3)

        self.extracted_message_display = tk.Text(self.frame4, height=5, width=50)
        self.extracted_message_display.grid(row=2, columnspan=3)

        # Image Previews
        self.original_image_preview = tk.Label(self.frame1)
        self.original_image_preview.grid(row=4, columnspan=3)

        self.decoded_image_preview = tk.Label(self.frame2)
        self.decoded_image_preview.grid(row=4, columnspan=3)

    def browse_original_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.ppm;*.pgm;*.bmp")])
        self.original_image_entry.delete(0, tk.END)
        self.original_image_entry.insert(0, file_path)
        self.display_image(file_path, self.original_image_preview)

    def encode_image_entry(self):
        file_path = filedialog.asksaveasfilename(defaultextension="*.*")
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, file_path)

    def browse_stego_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.ppm;*.pgm;*.bmp")])
        self.stego_image_entry.delete(0, tk.END)
        self.stego_image_entry.insert(0, file_path)

    def browse_psnr_original(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.ppm;*.pgm;*.bmp")])
        self.psnr_original_entry.delete(0, tk.END)
        self.psnr_original_entry.insert(0, file_path)

    def browse_psnr_modified(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.ppm;*.pgm;*.bmp")])
        self.psnr_modified_entry.delete(0, tk.END)
        self.psnr_modified_entry.insert(0, file_path)

    def browse_extract_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.ppm;*.pgm;*.bmp")])
        self.extract_image_entry.delete(0, tk.END)
        self.extract_image_entry.insert(0, file_path)

    def browse_message_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        self.message_entry.delete(0, tk.END)
        self.message_entry.insert(0, file_path)

    def display_image(self, image_path, label):
        try:
            img = Image.open(image_path)
            img.thumbnail((150, 150))  # Resize for preview
            img_tk = ImageTk.PhotoImage(img)
            label.config(image=img_tk)
            label.image = img_tk
        except Exception as e:
            messagebox.showerror("Error", f"Unable to load image: {e}")

    def encode_message(self):
        original_image_path = self.original_image_entry.get()
        output_image_path = self.output_entry.get()

        if not os.path.isfile(original_image_path):
            messagebox.showerror("Error", "Please select a valid original image.")
            return

        message_path = self.message_entry.get()

        encode_message(original_image_path, output_image_path, message_path)
        messagebox.showinfo("Success", "Message encoded successfully!")

    def decode_message(self):
        stego_image_path = self.stego_image_entry.get()
        if not os.path.isfile(stego_image_path):
            messagebox.showerror("Error", "Please select a valid stego image.")
            return

        extracted_message = extract_message(stego_image_path)
        self.decoded_message_display.delete(1.0, tk.END)
        self.decoded_message_display.insert(tk.END, extracted_message)

    def calculate_psnr_value(self):
        original_image_path = self.psnr_original_entry.get()
        modified_image_path = self.psnr_modified_entry.get()

        if not os.path.isfile(original_image_path) or not os.path.isfile(modified_image_path):
            messagebox.showerror("Error", "Please select valid image files.")
            return

        psnr_value = calculate_psnr(original_image_path, modified_image_path)
        self.psnr_value_display.delete(1.0, tk.END)
        self.psnr_value_display.insert(tk.END, f"PSNR: {psnr_value:.2f} dB")

    def extract_message(self):
        stego_image_path = self.extract_image_entry.get()
        if not os.path.isfile(stego_image_path):
            messagebox.showerror("Error", "Please select a valid image to extract the message from.")
            return

        extracted_message = extract_message(stego_image_path)
        self.extracted_message_display.delete(1.0, tk.END)
        self.extracted_message_display.insert(tk.END, extracted_message)


if __name__ == "__main__":
    root = tk.Tk()
    app = SteganographyApp(root)
    root.mainloop()
