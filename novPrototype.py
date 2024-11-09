# Purpose of the Digital Steganography App:
# The Digital Steganography App is designed to provide a simple yet effective way to hide secret text within an image.
# The app utilizes the Least Significant Bit (LSB) method for hiding messages in digital images, allowing users to
# securely embed text within an image without significantly altering the original image quality.
# The app also provides encryption and decryption capabilities using AES to ensure the confidentiality of the hidden messages.
# This tool is ideal for secure communication, data protection, and discreet information sharing.
#
# University of Texas at Dallas Department of Computer Science: Digital Steganography
# CS 4485.0W1 (Falll 2024)
# Company Mentor: Salih, Raed Mahdi
# Faculty Advisor: Miguel Razo-Razo
# RD-Team-10 Members (Solomon Bedane, Kevin Martinez, Samuel Rodriguez, Sri Suvarna Lakshmi Remella, Youssef El-Mansouri)
 
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.simpledialog import askstring
from PIL import Image, ImageTk
import numpy as np
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import os
from hashlib import sha256
 
class SteganographyTool:
    def __init__(self, window):
        self.window = window
        self.original_image_path = None
        self.encoded_image_path = None
        self.text_content = tk.StringVar()
        self.text_file_path = None
        self.encryption_passphrase = None
        self.text_file_size = None  # Added to store the file size
        self.setup_ui()
 
    def setup_ui(self):
        # Left Frame: Controls (Buttons)
        self.frame_left = tk.Frame(self.window, padx=10, pady=10)
        self.frame_left.pack(side="left", fill="y")
 
        self.select_image_button = tk.Button(self.frame_left, text="Select Image", command=self.select_image)
        self.select_image_button.grid(row=0, column=0, pady=10)
 
        self.select_text_button = tk.Button(self.frame_left, text="Select Text File", command=self.select_text)
        self.select_text_button.grid(row=1, column=0, pady=10)
 
        self.encode_button = tk.Button(self.frame_left, text="Encode", command=self.encode_image)
        self.encode_button.grid(row=2, column=0, pady=10)
 
        self.decode_button = tk.Button(self.frame_left, text="Decode", command=self.decode_image)
        self.decode_button.grid(row=3, column=0, pady=10)
 
        self.save_decoded_text_button = tk.Button(self.frame_left, text="Save Decoded Text", command=self.save_decoded_text)
        self.save_decoded_text_button.grid(row=4, column=0, pady=10)
 
        # Encryption Section
        self.encryption_label = tk.Label(self.frame_left, text="Encryption Passphrase:")
        self.encryption_label.grid(row=5, column=0, pady=10)
        self.encryption_button = tk.Button(self.frame_left, text="Enter Passphrase", command=self.set_passphrase)
        self.encryption_button.grid(row=6, column=0, pady=10)
 
        # Right Frame: Tabbed Interface for Image Display
        self.frame_right = tk.Frame(self.window, padx=10, pady=10)
        self.frame_right.pack(side="left", fill="y", expand=True)
 
        self.tab_control = ttk.Notebook(self.frame_right)
 
        # Tab 1: Selected Image
        self.selected_image_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.selected_image_tab, text="Selected Image")
 
        # Tab 2: Encoded Image
        self.encoded_image_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.encoded_image_tab, text="Encoded Image")
 
        # Pack the tab control
        self.tab_control.grid(row=0, column=0, padx=20, pady=20)
 
        # Labels inside tabs to display images
        self.selected_image_label = tk.Label(self.selected_image_tab)
        self.selected_image_label.pack(pady=20)
 
        self.encoded_image_label = tk.Label(self.encoded_image_tab)
        self.encoded_image_label.pack(pady=20)
 
        # Add a scrollable Text widget for decoded text
        self.decoded_text_frame = tk.Frame(self.frame_right)
        self.decoded_text_frame.grid(row=1, column=0, pady=10)
 
        # Scrollbar
        self.scrollbar = tk.Scrollbar(self.decoded_text_frame)
        self.scrollbar.pack(side="right", fill="y")
 
        # Text widget to display decoded text with scrollbar
        self.decoded_text_label = tk.Text(self.decoded_text_frame, wrap="word", height=10, width=50)
        self.decoded_text_label.pack(side="left", fill="both", expand=True)
       
        # Link scrollbar to the Text widget
        self.decoded_text_label.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.decoded_text_label.yview)
       
        # Initially disable text editing
        self.decoded_text_label.config(state=tk.DISABLED)
 
        # Information Labels for displaying PSNR and file size
        self.info_frame = tk.Frame(self.frame_right, padx=10, pady=10)
        self.info_frame.grid(row=2, column=0, pady=10)
 
        # PSNR and image size labels
        self.psnr_original_label = tk.Label(self.info_frame, text="PSNR of Original Image (dB): N/A")
        self.psnr_original_label.grid(row=0, column=0, pady=5)
 
        self.psnr_stego_label = tk.Label(self.info_frame, text="PSNR of Stego-Image (dB): N/A")
        self.psnr_stego_label.grid(row=1, column=0, pady=5)
 
        self.image_size_label = tk.Label(self.info_frame, text="Image Size (dB): N/A")  # Updated label
        self.image_size_label.grid(row=2, column=0, pady=5)
 
    def set_passphrase(self):
        """Prompt the user to enter a passphrase for encryption/decryption."""
        self.encryption_passphrase = askstring("Enter Passphrase", "Enter encryption passphrase:")
        if not self.encryption_passphrase:
            messagebox.showerror("Error", "Passphrase is required for encryption/decryption.")
        else:
            messagebox.showinfo("Success", "Passphrase set successfully!")
 
    def select_image(self):
        """Allow user to select an image file."""
        self.original_image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if self.original_image_path:
            self.display_image(self.original_image_path, self.selected_image_label)
 
            # Calculate PSNR for the original image and update the label
            psnr_original = self.calculate_psnr(self.original_image_path, self.original_image_path)
            self.psnr_original_label.config(text=f"PSNR of Original Image (dB): {psnr_original:.2f}")
 
            # Calculate the image size in dB (using PSNR for image quality)
            image_size_db = self.calculate_psnr(self.original_image_path, self.original_image_path)  # Use PSNR as the 'size' in dB
            self.image_size_label.config(text=f"Image Size (dB): {image_size_db:.2f}")
 
    def select_text(self):
        """Allow user to select a text file and calculate its file size."""
        self.text_file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if self.text_file_path:
            # Calculate the file size in KB
            self.text_file_size = os.path.getsize(self.text_file_path) / 1024  # Size in KB
            with open(self.text_file_path, 'r') as file:
                text = file.read()
                if self.encryption_passphrase:
                    text = self.decrypt_text(text)  # Decrypt text if passphrase is set
                self.text_content.set(text)
 
            # Update file size label
            self.image_size_label.config(text=f"File Size (KB): {self.text_file_size:.2f}")  # Keep this label for file size (KB)
 
    def encrypt_text(self, text):
        """Encrypt the text using AES encryption."""
        # Use SHA-256 to hash the passphrase and ensure it is 32 bytes
        key = sha256(self.encryption_passphrase.encode()).digest()
        cipher = AES.new(key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(text.encode(), AES.block_size))
        iv = base64.b64encode(cipher.iv).decode('utf-8')
        ct = base64.b64encode(ct_bytes).decode('utf-8')
        return iv + ct  # Return IV + Ciphertext
 
    def decrypt_text(self, encrypted_text):
        """Decrypt the text using AES decryption."""
        iv = base64.b64decode(encrypted_text[:24])
        ct = base64.b64decode(encrypted_text[24:])
        key = sha256(self.encryption_passphrase.encode()).digest()
        cipher = AES.new(key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return pt.decode('utf-8')
 
    def encode_image(self):
        """Encode the selected text into the selected image."""
        if not self.original_image_path or not self.text_content.get():
            messagebox.showerror("Error", "Please select both an image and a text file.")
            return
 
        if not self.encryption_passphrase:
            messagebox.showerror("Error", "Please enter a passphrase before encoding.")
            return
 
        original_image = Image.open(self.original_image_path)
        pixels = original_image.load()
 
        # Encrypt the text before encoding
        text = self.text_content.get()
        encrypted_text = self.encrypt_text(text)
 
        end_marker = '11111111'  # End marker to indicate the end of the hidden text
        binary_text = ''.join(format(ord(c), '08b') for c in encrypted_text) + end_marker
        text_length = len(binary_text)
 
        # Ensure the image is large enough to hold the text
        if text_length > original_image.width * original_image.height * 3:
            messagebox.showerror("Error", "Text is too large for this image!")
            return
 
        # Encode the text into the image
        index = 0
        for y in range(original_image.height):
            for x in range(original_image.width):
                r, g, b = pixels[x, y]
                if index < text_length:
                    r = (r & 0xFE) | int(binary_text[index])  # Modify LSB of Red
                    index += 1
                if index < text_length:
                    g = (g & 0xFE) | int(binary_text[index])  # Modify LSB of Green
                    index += 1
                if index < text_length:
                    b = (b & 0xFE) | int(binary_text[index])  # Modify LSB of Blue
                    index += 1
                pixels[x, y] = (r, g, b)
 
            if index >= text_length:
                break
 
        # Save encoded image and update encoded image path
        encoded_image_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if encoded_image_path:
            original_image.save(encoded_image_path)  # Save the stego image
            self.encoded_image_path = encoded_image_path  # Update the path to the encoded image
            self.display_image(encoded_image_path, self.encoded_image_label)  # Display the encoded image
 
            # Calculate PSNR of the original and encoded (stego) image
            psnr_stego = self.calculate_psnr(self.original_image_path, encoded_image_path)
            self.psnr_stego_label.config(text=f"PSNR of Stego-Image (dB): {psnr_stego:.2f}")
 
            messagebox.showinfo("Success", "Image encoded and saved successfully!")
 
    def calculate_psnr(self, original_image_path, encoded_image_path):
        """Calculate PSNR (Peak Signal to Noise Ratio) between two images."""
        original_image = np.array(Image.open(original_image_path))
        encoded_image = np.array(Image.open(encoded_image_path))
 
        mse = np.mean((original_image - encoded_image) ** 2)
        if mse == 0:
            return float('inf')  # If MSE is 0, images are identical, PSNR is infinite
        max_pixel = 255.0
        psnr = 10 * np.log10((max_pixel ** 2) / mse)
        return psnr
 
    def display_image(self, image_path, label):
        """Display an image on the specified label."""
        image = Image.open(image_path)
        image.thumbnail((200, 200))
        img = ImageTk.PhotoImage(image)
        label.config(image=img)
        label.image = img
 
    def decode_image(self):
        """Decode the hidden text from the selected image."""
        if not self.encoded_image_path:
            messagebox.showerror("Error", "Please select an encoded image.")
            return
 
        encoded_image = Image.open(self.encoded_image_path)
        pixels = encoded_image.load()
 
        binary_text = ""
        for y in range(encoded_image.height):
            for x in range(encoded_image.width):
                r, g, b = pixels[x, y]
                binary_text += str(r & 1)  # Extract LSB of Red
                binary_text += str(g & 1)  # Extract LSB of Green
                binary_text += str(b & 1)  # Extract LSB of Blue
 
        end_marker_index = binary_text.find('11111111')
        if end_marker_index != -1:
            binary_text = binary_text[:end_marker_index]  # Remove the end marker
            decoded_text = ''.join(chr(int(binary_text[i:i+8], 2)) for i in range(0, len(binary_text), 8))
           
            # Decrypt the text if passphrase is set
            if self.encryption_passphrase:
                decoded_text = self.decrypt_text(decoded_text)
           
            self.decoded_text_label.config(state=tk.NORMAL)
            self.decoded_text_label.delete(1.0, tk.END)
            self.decoded_text_label.insert(tk.END, decoded_text)
            self.decoded_text_label.config(state=tk.DISABLED)
        else:
            messagebox.showerror("Error", "No hidden text found in this image.")
   
    def save_decoded_text(self):
        """Save the decoded text to a file."""
        if self.decoded_text_label.get(1.0, tk.END).strip():
            save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
            if save_path:
                with open(save_path, 'w') as file:
                    file.write(self.decoded_text_label.get(1.0, tk.END).strip())
                messagebox.showinfo("Success", "Decoded text saved successfully!")
        else:
            messagebox.showerror("Error", "No decoded text to save.")
 
if __name__ == "__main__":
    # Initialize the main window
    root = tk.Tk()
    root.title("Digital Steganography App")
 
    # Create the Steganography tool
    app = SteganographyTool(root)
 
    # Run the Tkinter event loop
    root.mainloop()
