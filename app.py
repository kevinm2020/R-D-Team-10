import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import codecs
import os


class SteganographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Steganography App")

        self.create_widgets()

        self.original_image = None
        self.stego_image = None

    def create_widgets(self):
        # Header
        header = tk.Label(self.root, text="Steganography App", font=("Helvetica", 16))
        header.pack(pady=10)

        # Encode Section
        self.encode_frame = tk.Frame(self.root)
        self.encode_frame.pack(pady=10)

        tk.Label(self.encode_frame, text="Select Original Image:").grid(row=0, column=0)
        self.original_image_entry = tk.Entry(self.encode_frame, width=40)
        self.original_image_entry.grid(row=0, column=1)
        tk.Button(self.encode_frame, text="Browse", command=self.browse_original_image).grid(row=0, column=2)

        tk.Label(self.encode_frame, text="Enter Message:").grid(row=1, column=0)
        self.message_entry = tk.Entry(self.encode_frame, width=40)
        self.message_entry.grid(row=1, column=1, columnspan=2)

        tk.Button(self.encode_frame, text="Encode", command=self.encode_message).grid(row=2, columnspan=3)

        # Preview Section
        tk.Label(self.encode_frame, text="Original Image Preview:").grid(row=3, columnspan=3)
        self.original_image_preview = tk.Label(self.encode_frame)
        self.original_image_preview.grid(row=4, columnspan=3, pady=5)

        # Decode Section
        self.decode_frame = tk.Frame(self.root)
        self.decode_frame.pack(pady=10)

        tk.Label(self.decode_frame, text="Select Stego Image:").grid(row=0, column=0)
        self.stego_image_entry = tk.Entry(self.decode_frame, width=40)
        self.stego_image_entry.grid(row=0, column=1)
        tk.Button(self.decode_frame, text="Browse", command=self.browse_stego_image).grid(row=0, column=2)

        tk.Button(self.decode_frame, text="Decode", command=self.decode_message).grid(row=1, columnspan=3)

        # Decoded Message and Preview Section
        tk.Label(self.decode_frame, text="Decoded Message:").grid(row=2, column=0)
        self.decoded_message_display = tk.Text(self.decode_frame, height=5, width=50)
        self.decoded_message_display.grid(row=2, column=1, columnspan=2)

        tk.Label(self.decode_frame, text="Decoded Image Preview:").grid(row=3, columnspan=3)
        self.decoded_image_preview = tk.Label(self.decode_frame)
        self.decoded_image_preview.grid(row=4, columnspan=3, pady=5)

    def browse_original_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.original_image_entry.delete(0, tk.END)
            self.original_image_entry.insert(0, file_path)
            self.display_image(file_path, self.original_image_preview)
            self.original_image = Image.open(file_path)

    def browse_stego_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.stego_image_entry.delete(0, tk.END)
            self.stego_image_entry.insert(0, file_path)
            self.display_image(file_path, self.decoded_image_preview)

    def display_image(self, path, label):
        img = Image.open(path)
        img.thumbnail((200, 200))  # Resize for preview
        img = ImageTk.PhotoImage(img)
        label.config(image=img)
        label.image = img  # Keep a reference to avoid garbage collection

    def encode_message(self):
        image_path = self.original_image_entry.get()
        message = self.message_entry.get()

        if not os.path.isfile(image_path) or not message:
            messagebox.showerror("Error", "Please select a valid image and enter a message.")
            return

        # Encode the message into the image
        img = Image.open(image_path)
        encoded_image = self.steganography_encode(img, message)

        output_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if output_path:
            encoded_image.save(output_path)
            messagebox.showinfo("Success", "Message encoded successfully!")

    def decode_message(self):
        stego_image_path = self.stego_image_entry.get()

        if not os.path.isfile(stego_image_path):
            messagebox.showerror("Error", "Please select a valid stego image.")
            return

        # Decode the message from the image
        img = Image.open(stego_image_path)
        message = self.steganography_decode(img)
        self.decoded_message_display.delete(1.0, tk.END)
        self.decoded_message_display.insert(tk.END, message)

        # Preview the decoded image if available
        self.display_image(stego_image_path, self.decoded_image_preview)

    def steganography_encode(self, img, message):
        binary_message = ''.join(format(ord(char), '08b') for char in message) + '00000000'  # Null byte to mark end
        data_index = 0
        pixels = img.load()

        for y in range(img.height):
            for x in range(img.width):
                if data_index < len(binary_message):
                    r, g, b = pixels[x, y]
                    # Change the least significant bit
                    r = (r & ~1) | int(binary_message[data_index])
                    pixels[x, y] = (r, g, b)
                    data_index += 1
                else:
                    return img
        return img

    def steganography_decode(self, img):
        binary_message = ""
        pixels = img.load()

        for y in range(img.height):
            for x in range(img.width):
                r, g, b = pixels[x, y]
                binary_message += str(r & 1)

        message = ""
        for i in range(0, len(binary_message), 8):
            byte = binary_message[i:i + 8]
            if byte == '00000000':  # End of message
                break
            message += chr(int(byte, 2))
        return message


if __name__ == "__main__":
    root = tk.Tk()
    app = SteganographyApp(root)
    root.mainloop()
