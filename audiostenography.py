import tkinter as tk
from tkinter import messagebox, filedialog
import os
import subprocess
import webbrowser
import threading
import wave
import base64
from PIL import Image,ImageTk
import io
import tempfile
import sys
from cryptography.fernet import Fernet, InvalidToken
import random
import smtplib
from email.message import EmailMessage
import string
import re
import qrcode
from playsound import playsound
import uuid
import zipfile
import ctypes
import sqlite3
import hashlib

DB_FILE = "users.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(name, email, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", 
                  (name, email, hash_password(password)))
        conn.commit()
        return True, "User registered successfully."
    except sqlite3.IntegrityError:
        return False, "Email already exists."
    finally:
        conn.close()

def login_user(email, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ? AND password = ?", 
              (email, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user

icon_path = r"C:\Users\Mahalakshmi\Downloads\image\lockkey.png"

base64_icon = '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'

icon_data = base64.b64decode(base64_icon)

root = tk.Tk()
init_db()
current_user = None
#Create a PhotoImage object from the bytes
icon_image= tk.PhotoImage(data=icon_data)
root.iconphoto(True,icon_image)
root.title("Audio Encode And Decode")
root.geometry("600x500")
root.configure(bg='gold')


# Center the window
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = int((screen_width / 2) - (600 / 2))
y = int((screen_height / 2) - (600 / 2))
root.geometry(f"600x600+{x}+{y}")


button_frame = tk.Frame(root, bg="grey")
button_frame.pack(expand=True)


# ------------------ Utility Functions ------------------

def text_to_binary(text):
    return ''.join(format(ord(i), '08b') for i in text)

def binary_to_text(binary_data):
    chars = [chr(int(binary_data[i:i+8], 2)) for i in range(0, len(binary_data), 8)]
    return ''.join(chars).split("###")[0]

def generate_password():
    return Fernet.generate_key()  # Proper Fernet key

def encrypt_message(message, key):
    fernet = Fernet(key)
    return fernet.encrypt(message.encode()).decode()  # Encrypted string

def decrypt_message(encrypted_message, key):
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_message.encode()).decode()  # Decrypted string
def compress_file_to_zip(file_path):
    zip_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4().hex}.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(file_path, arcname=os.path.basename(file_path))
    return zip_path
def convert_to_wav(input_path):
    if input_path.lower().endswith(".wav"):
        return input_path, False  # Not converted

    input_dir = os.path.dirname(input_path)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    unique_name = f"output_stego_{base_name}_{uuid.uuid4().hex}.wav"
    output_path = os.path.join(input_dir, unique_name)

    try:
        subprocess.run(["ffmpeg", "-y", "-i", input_path, output_path],
                       shell=True, check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output_path, True  # Was converted
    except subprocess.CalledProcessError as e:
        raise RuntimeError("FFmpeg failed to convert the file:\n" + e.stderr.decode())

#Play audio preview function 
def play_audio(file_path):
    try:
        if not os.path.exists(file_path):
            messagebox.showerror("Error", "File not found!")
            return
        playsound(file_path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to play audio:\n{e}")
        
def hide_file_windows(path):
    """Hides the given file using Windows file attributes."""
    try:
        ctypes.windll.kernel32.SetFileAttributesW(path, 2)  # 2 = Hidden
    except Exception as e:
        print("Error hiding file:", e)

def unhide_file_windows(path):
    """Unhides the given file using Windows file attributes."""
    try:
        ctypes.windll.kernel32.SetFileAttributesW(path, 0)  # 0 = Normal
    except Exception as e:
        print("Error unhiding file:", e)

def send_password_email(sender_email, smtp_password, receiver_email, password_msg, audio_file_path):
    try:
        qr = qrcode.make(password_msg)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_qr:
            qr.save(temp_qr.name)
            qr_path = temp_qr.name

        msg = EmailMessage()
        msg.set_content(
            "Your decoding password is attached as a QR code.\n\n"
            "Also, your audio file with hidden content is attached.\n\n"
            "Scan the QR to retrieve your password securely."
        )
        msg['Subject'] = 'Audio Steganography - Encrypted Content'
        msg['From'] = sender_email
        msg['To'] = receiver_email

        with open(qr_path, 'rb') as img_file:
            msg.add_attachment(img_file.read(), maintype='image', subtype='png', filename='password_qr.png')

        with open(audio_file_path, 'rb') as audio_file:
            msg.add_attachment(audio_file.read(), maintype='audio', subtype='wav', filename='output_stego.wav')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, smtp_password)
            smtp.send_message(msg)

        os.remove(qr_path)

    except Exception as e:
        raise RuntimeError("Failed to send email: " + str(e))


def encode_audio(input_file, output_file, secret_msg):
    song = wave.open(input_file, mode='rb')
    frame_bytes = bytearray(list(song.readframes(song.getnframes())))
    secret_msg += '###'
    bits = text_to_binary(secret_msg)

    if len(bits) > len(frame_bytes):
        raise ValueError("Message too large to encode in this audio")

    for i in range(len(bits)):
        frame_bytes[i] = (frame_bytes[i] & 254) | int(bits[i])

    with wave.open(output_file, 'wb') as mod_audio:
        mod_audio.setparams(song.getparams())
        mod_audio.writeframes(frame_bytes)

    song.close()

def decode_audio(file):
    song = wave.open(file, mode='rb')
    frame_bytes = bytearray(list(song.readframes(song.getnframes())))
    extracted = ''.join([str(byte & 1) for byte in frame_bytes])
    song.close()
    return binary_to_text(extracted)

def calculate_capacity(audio_path):
    with wave.open(audio_path, mode='rb') as song:
        frames = song.getnframes()
        capacity_bits = frames  # 1 bit per byte using LSB
        capacity_chars = capacity_bits // 8
        return capacity_chars

# ------------------ GUI Windows ------------------

def button1_clicked():
    win = tk.Toplevel(root)
    win.title("Hide Text and File in Audio")
    win.geometry("700x300")

    # Labels
    tk.Label(win, text="Audio File Path").grid(row=0, column=0)
    tk.Label(win, text="Message").grid(row=1, column=0)
    tk.Label(win, text="Sender Email (Gmail)").grid(row=2, column=0)
    tk.Label(win, text="SMTP Password (Gmail)").grid(row=3, column=0)
    tk.Label(win, text="Receiver Email").grid(row=4, column=0)
    tk.Label(win, text="Hide File(optional)").grid(row=5, column=0)

    # Entries
    file_entry = tk.Entry(win, width=50)
    msg_entry = tk.Entry(win, width=60)
    email_entry = tk.Entry(win, width=60)
    smtp_pass_entry = tk.Entry(win, width=60, show='*')
    recv_entry = tk.Entry(win, width=60)
    file_to_hide_entry = tk.Entry(win, width=60)

    file_entry.grid(row=0, column=1)
    msg_entry.grid(row=1, column=1)
    email_entry.grid(row=2, column=1)
    smtp_pass_entry.grid(row=3, column=1)
    recv_entry.grid(row=4, column=1)
    file_to_hide_entry.grid(row=5, column=1)

    # File Browsing
    def browse_audio_file():
        filename = filedialog.askopenfilename(
            filetypes=[
                ("Audio Files", "*.wav *.mp3 *.m4a *.aac *.flac *.ogg *.wma"),
                ("All Files", "*.*")
            ]
        )
        file_entry.delete(0, tk.END)
        file_entry.insert(0, filename)

        if filename:
            try:
                converted_path, is_converted = convert_to_wav(filename)
                cap = calculate_capacity(converted_path)

                # Delete temp converted file if needed
                if is_converted and os.path.exists(converted_path):
                    os.remove(converted_path)

                messagebox.showinfo("Capacity Info", f"Max characters that can be hidden: {cap}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to get capacity:\n{e}")


    def browse_file_to_hide():
        file_path = filedialog.askopenfilename()
        file_to_hide_entry.delete(0, tk.END)
        file_to_hide_entry.insert(0, file_path)

    tk.Button(win, text="Browse", command=browse_audio_file).grid(row=0, column=2)
    tk.Button(win, text="Play Audio", command=lambda: play_audio(file_entry.get())).grid(row=0, column=3)
    tk.Button(win, text="Browse", command=browse_file_to_hide).grid(row=5, column=2)

    # Start Encoding
    def start_encoding():
        try:
            input_original = file_entry.get()
            input_path, is_converted = convert_to_wav(input_original)

            if not input_path or not os.path.exists(input_path):
                messagebox.showerror("Error", "Please select a valid WAV file.")
                return

            message_text = msg_entry.get()
            file_path = file_to_hide_entry.get().strip()
            file_content = ""

            if file_path and os.path.exists(file_path):
                compressed_path = compress_file_to_zip(file_path)
                with open(compressed_path, "rb") as f:
                    encoded_file = base64.b64encode(f.read()).decode('utf-8')
                    file_name = os.path.basename(compressed_path)
                    file_content = f"<<<MSG_END>>>{file_name}<<<FILE_END>>>{encoded_file}"

            full_text = f"{message_text}{file_content}"
            key = generate_password()
            encrypted_msg = encrypt_message(full_text, key)

            capacity = calculate_capacity(input_path)
            if len(encrypted_msg) > capacity:
                messagebox.showerror("Error", f"Message too long! Max characters that can be hidden: {capacity}")
                return

            # Step 1: Create hidden folder
            base_dir = os.path.dirname(input_original)
            hidden_folder = os.path.join(base_dir, "output_stego")

            if not os.path.exists(hidden_folder):
                os.makedirs(hidden_folder)
                hide_file_windows(hidden_folder)  # Hide the folder itself

            # Step 2: Create file path inside hidden folder
            original_name = os.path.splitext(os.path.basename(input_original))[0]
            unique_output = f"output_stego_{original_name}_{uuid.uuid4().hex}.wav"
            output_path = os.path.join(hidden_folder, unique_output)

            encode_audio(input_path, output_path, encrypted_msg)
            # Hide only the final stego file
            hide_file_windows(output_path)

            # Delete the converted WAV only if it was newly created (i.e., not originally WAV)
            if is_converted and os.path.exists(input_path):
                try:
                    os.remove(input_path)
                except Exception as e:
                    print("Could not delete converted file:", e)


            send_password_email(
                sender_email=email_entry.get(),
                smtp_password=smtp_pass_entry.get(),
                receiver_email=recv_entry.get(),
                password_msg=key,
                audio_file_path=output_path
            )

            # Only hide the final stego file
            hide_file_windows(output_path)

            # Delete the converted WAV if it was newly created (i.e. not originally .wav)
            if input_path != input_original and os.path.exists(input_path):
                os.remove(input_path)

            messagebox.showinfo("Success", "Audio encoded successfully!")


        except Exception as e:
            messagebox.showerror("Error", str(e))


    tk.Button(win, text="Hide", bg='blue', fg='white', command=start_encoding).grid(row=6, columnspan=2, pady=10)

def button2_clicked():
    win = tk.Toplevel(root)
    win.title("Extract Hidden Text and File")
    win.geometry("580x250")

    tk.Label(win, text="File Path").grid(row=0, column=0)
    file_entry = tk.Entry(win, width=50)
    file_entry.grid(row=0, column=1)

    def browse_file():
        filename = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        file_entry.delete(0, tk.END)
        file_entry.insert(0, filename)

    tk.Button(win, text="Browse", command=browse_file).grid(row=0, column=2)


    tk.Label(win, text="Password").grid(row=1, column=0)
    pass_entry = tk.Entry(win, width=60, show='*')
    pass_entry.grid(row=1, column=1)

    def start_decoding():
        try:
            input_path = file_entry.get()
            if not input_path or not os.path.exists(input_path):
                messagebox.showerror("Error", "Please select a valid WAV file.")
                return

            raw_secret = decode_audio(input_path)
            user_key = pass_entry.get().strip().encode()
            decrypted = decrypt_message(raw_secret, user_key)

            # Parse message + file
            if "<<<MSG_END>>>" in decrypted and "<<<FILE_END>>>" in decrypted:
                message_text, file_part = decrypted.split("<<<MSG_END>>>")
                file_name, encoded_file = file_part.split("<<<FILE_END>>>")

                # Ask user where to save file
                file_ext = os.path.splitext(file_name)[1]
                save_path = filedialog.asksaveasfilename(
                    defaultextension=file_ext,
                    filetypes=[(f"{file_ext.upper()} File", f"*{file_ext}"), ("All Files", "*.*")],
                    initialfile=file_name
                )
                if save_path:
                    with open(save_path, 'wb') as f:
                        f.write(base64.b64decode(encoded_file))

                messagebox.showinfo(
                    "Secret Extracted",
                    f"The secret message is:\n\n{message_text}\n\nThe hidden file was saved as:\n{save_path}"
            )

            else:
                # Only message (no file)
                messagebox.showinfo("Secret Message", f"The secret message is:\n\n{decrypted}")

        except Exception as e:
            messagebox.showerror("Error", str(e))


    tk.Button(win, text="Decode Audio", bg='blue', fg='white', command=start_decoding).grid(row=2, columnspan=2, pady=10)

def show_login_window():
    login_win = tk.Toplevel(root)
    login_win.title("User Login")
    login_win.geometry("400x250")

    tk.Label(login_win, text="Email").grid(row=0, column=0)
    tk.Label(login_win, text="Password").grid(row=1, column=0)

    email_entry = tk.Entry(login_win, width=40)
    pass_entry = tk.Entry(login_win, width=40, show="*")
    email_entry.grid(row=0, column=1)
    pass_entry.grid(row=1, column=1)

    def attempt_login():
        global current_user
        user = login_user(email_entry.get(), pass_entry.get())
        if user:
            current_user = user
            messagebox.showinfo("Login Successful", f"Welcome {user[1]}!")
            login_win.destroy()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials")

    def open_register_window():
        login_win.destroy()
        show_register_window()

    tk.Button(login_win, text="Login", command=attempt_login).grid(row=2, columnspan=2, pady=10)
    tk.Button(login_win, text="Register", command=open_register_window).grid(row=3, columnspan=2)

def show_register_window():
    reg_win = tk.Toplevel(root)
    reg_win.title("Register")
    reg_win.geometry("400x300")

    tk.Label(reg_win, text="Name").grid(row=0, column=0)
    tk.Label(reg_win, text="Email").grid(row=1, column=0)
    tk.Label(reg_win, text="Password").grid(row=2, column=0)

    name_entry = tk.Entry(reg_win, width=40)
    email_entry = tk.Entry(reg_win, width=40)
    pass_entry = tk.Entry(reg_win, width=40, show="*")

    name_entry.grid(row=0, column=1)
    email_entry.grid(row=1, column=1)
    pass_entry.grid(row=2, column=1)

    def attempt_register():
        name = name_entry.get()
        email = email_entry.get()
        password = pass_entry.get()
        success, msg = register_user(name, email, password)
        if success:
            messagebox.showinfo("Registered", msg)
            reg_win.destroy()
            show_login_window()
        else:
            messagebox.showerror("Error", msg)

    tk.Button(reg_win, text="Register", command=attempt_register).grid(row=3, columnspan=2, pady=10)

def on_hide_click():
    if not current_user:
        messagebox.showwarning("Login Required", "Please login to use this feature.")
        return
    button1_clicked()

def on_extract_click():
    if not current_user:
        messagebox.showwarning("Login Required", "Please login to use this feature.")
        return
    button2_clicked()


def project_info():
    html_code =  html_code = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Project Information</title>
        <style>
            .header {
              display: flex;
              justify-content: space-between;
              align-items: flex-start;
              padding: 10px;
            }
           .header img {
              width: 100px;
            }
            body {
                background-color: #ffffff ;
                font-family: Arial, sans-serif;
                padding: 40px;
            }
            h2 {
                color: #0000FF;
            }
            table {
                width: 80%;
                border-collapse: collapse;
                margin-top: 20px;
                background-color: #FFFFFF;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            th, td {
                padding: 12px;
                border: 1px solid #4B3F72;
                text-align: left;
                colour:#000000
            }
            th {
                background-color: #F4C430;
                #000000
            }
            .section-title {
                margin-top: 40px;
                color:#0000FF;
            }
            .highlight {
                font-weight: bold;
                color: #000000;
            }
        </style>
    </head>
    <body>
    
    <div class="header">
          <div></div> <!-- Left side (empty) -->
          <img src="data:image/png;base64,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" alt="Logo">
    </div>
        <h2>Project Information</h2>
        <p>This project was developed by <span class="highlight">
        <p>Mr.K B Sri krish-ST#IS#7864-srikrish1319@gmail.com</p>
        <p>Ms.K.B.Mahalakshmi-ST#IS#7865-kbmaha24@gmail.com</p>
        <p>Ms.M.Pooja Verma-ST#IS#7866- mpoojaverma12@gmail.com</p>
        <p>Ms.Nithyashree Bose-ST#IS#7867-nithyashreebose@gmail.com</p>
        <p>This project was developed as part of a <b>Cyber Security Internship</b>. It is designed to <b>secure real-world organizations from cyber frauds and hacker attacks</b>.</p>
        
        <h3 class="section-title">Project Details</h3>
        <table>
            <tr><th>Project Name</th><td>ADVANCED AUDIO STEGANOGRAPHY USING LSB TECHNIQUE</td></tr>
            <tr><th>Project Description</th><td>This project securely hides secret messages and files inside audio using the LSB (Least Significant Bit) technique. It supports various audio formats and converts them to WAV if necessary for embedding. A message is encrypted and shared via email as a QR code for safe decoding. Users need to register or log in to access features, which ensures controlled usage. Additional files can be hidden along with the message, and both are extracted using a password-protected process.</td></tr>
            <tr><th>Project Start Date</th><td>24-June-2025</td></tr>
            <tr><th>Project End Date</th><td>18-July-2025</td></tr>
            <tr><th>Project Status</th><td><b>Completed</b></td></tr>
        </table>
        
        <h3 class="section-title">Developer Details</h3>
        <style>
        table {
          width: 1400px;
          table-layout: fixed;
          word-wrap: break-word;
        }
        td, th {
          padding: 10px;
        }
        </style>
         <table>
        <tr>
            <th>Name</th>
            <th>Employee ID</th>
            <th>Email</th>
        </tr>
        <tr>
            <td>Mr.K B Sri krish</td>
            <td>ST#IS#7864</td>
            <td>srikrish1319@gmail.com</td>
        </tr>
        <tr>
            <td>Ms.K.B.Mahalakshmi</td>
            <td>ST#IS#7865</td>
            <td>kbmaha24@gmail.com</td>
        </tr>
        <tr>
            <td>Ms.M.Pooja Verma</td>
            <td>ST#IS#7866</td>
            <td>mpoojaverma12@gmail.com</td>
        </tr>
        <tr>
            <td>Ms.Nithyashree Bose</td>
            <td>ST#IS#7867</td>
            <td>nithyashreebose@gmail.com</td>
        </tr>
    </table>
    
    <h3 class="section-title">Company Details</h3>
        <table>
            <tr><th>Company Name</th><td>Supraja Technologies</td></tr>
            <tr><th>Email</th><td>contact@suprajatechnologies.com</td></tr>
        </table>
    </body>
    </html>
    """
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html') as temp_file:
        temp_file.write(html_code)
        webbrowser.open('file://' + os.path.realpath(temp_file.name))

# ------------------ UI Layout ------------------
tk.Button(root, text="Project Info", font=("Arial", 14, "bold"), bg='blue', fg='white', command=project_info).pack(pady=20)
tk.Label(root, text="Audio Steganography", font=("Arial", 20, "bold"),bg='white',fg='blue').pack(pady=25)
#Base64 image as background
background_image_base64 = "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"
background_image_data = base64.b64decode(background_image_base64)
background_image = Image.open(io.BytesIO(background_image_data))
background_image = background_image.resize((200,150),Image.Resampling.LANCZOS)

background_photo = ImageTk.PhotoImage(background_image)
background_label = tk.Label(root, image=background_photo)
background_label.pack(pady=10)

Login_button=tk.Button(root, text="Login / Register", font=("Arial", 12), bg="red", fg="white", command=show_login_window).pack(pady=10)
button_frame = tk.Frame(root, bg="coral",width=300,height=110)
button_frame.pack(pady=20)

button1 = tk.Button(button_frame, text="Hide", font=("Arial", 14, "bold"),padx=10, pady=5, command=on_hide_click, bg='blue', fg='white')
button2 = tk.Button(button_frame, text="Extract", font=("Arial", 14, "bold"),padx=10, pady=5, command=on_extract_click, bg='blue', fg='white')
button1.place(x=50, y=10, width=200, height=40)
button2.place(x=50, y=60, width=200, height=40)

button_frame.pack(expand=True)


root.mainloop() 
