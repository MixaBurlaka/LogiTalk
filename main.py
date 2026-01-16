import io




from customtkinter import *
from socket import *
import threading
import base64
from PIL import Image, ImageTk
import data as d












class LogiTalk(CTk):
 def __init__(self):
     super().__init__()
     self.title('LogiTalk')
     self.geometry('400x300')
     self.resizable(width=True, height=True)


     self.username = 'Ілля'




     #Меню
     self.frame = CTkFrame(self,  width=200, height=self.winfo_height())
     self.frame.pack_propagate(False)
     #self.frame.configure(width=0)
     self.frame.place(x=0, y=0)
     self.is_show_menu = True
     self.frame_width = 200








     #Нікнейм
     self.label = CTkLabel(self.frame, text=f"Привіт, {self.username}")
     self.label.pack(pady=30)
     self.entry = CTkEntry(self.frame)
     self.entry.pack()


     #Підтвердження нікнейму
     self.username_button = CTkButton(self.frame, text="Прийняти", command=self.set_username)
     self.username_button.pack(pady=30)




     #Кольорова тема
     self.label_theme = CTkOptionMenu(self.frame, values=['Світла','Темна'], command=self.change_theme)
     self.label_theme.pack(pady=20, side=BOTTOM)
     self.theme = 'light'








     #Кнопка для меню
     self.btn = CTkButton(self, text='◀️', command=self.toggle_show_menu, width=30)
     self.btn.place(x=0, y=0)
     self.menu_show_speed = 20 #швидкість появи бокового меню








     #Чат
     self.chat_text = CTkScrollableFrame(self)
     self.chat_text.place(x=0)








     #Введення повідомлення
     self.message_input = CTkEntry(self, placeholder_text='Ваше повідомлення')
     self.message_input.place(x=0, y=250)








     #Кнопка відправки повідомлення
     self.send_button = CTkButton(self, text='▶️', width=40, height=30, command=self.send_message)
     self.send_button.place(x=200, y=250)










     try:
         self.sock = socket(AF_INET, SOCK_STREAM)
         self.sock.connect((d.HOST, d.PORT))
         hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднується до чату!\n"
         self.sock.send(hello.encode('utf-8'))
         threading.Thread(target=self.recv_message, daemon=True).start()
     except Exception as e:
         self.add_message(f"Не вдалось підключитись до сервера: {e}")




     self.adaptive_ui()


 def set_username(self):
     self.username = self.entry.get()
     self.label.configure(text=f"Привіт, {self.username}")
     self.entry.delete(0, END)




 def add_message(self, message, img=None, own_message=False):
     bg_color = "#4a4a4a" if own_message else "#2d2d2d"
     message_frame = CTkFrame(self.chat_text, fg_color=bg_color)
     if own_message:
         message_frame.pack(pady=5, anchor='e')
     else:
         message_frame.pack(pady=5, anchor='w')
     wraplength_size = self.winfo_width() - self.frame.winfo_width() - 40




     if not img:
         CTkLabel(message_frame, text=message, wraplength=wraplength_size, text_color='white', justify='left').pack(pady=5, padx=10)
     else:
         CTkLabel(message_frame, text=message, wraplength=wraplength_size, text_color='white', justify='left', image=img, compound='top').pack(
             pady=5, padx=10)




 def send_message(self):
     message = self.message_input.get()
     if message:
         self.add_message(f"{self.username}: {message}", own_message=True)
         data = f"TEXT@{self.username}@{message}\n"
         try:
             self.sock.sendall(data.encode('utf-8'))
         except:
             pass
         self.message_input.delete(0, END)




 def recv_message(self):
     buffer = ""
     while True:
         try:
             chunk = self.sock.recv(4096)
             if not chunk:
                 break
             buffer += chunk.decode('utf-8', errors='ignore')




             while "\n" in buffer:
                 line, buffer = buffer.split("\n", 1)
                 self.handle_line(line.strip())




         except:
             break
     self.sock.close()




 def handle_line(self, line):
     if not line:
         return
     parts = line.split("@", 3)
     msg_type = parts[0]

     if msg_type == "TEXT":
         if len(parts) == 3:
             author = parts[1]
             message = parts[2]
             self.add_message(f"{author}: {message}")
     elif msg_type == "IMAGE":
         if len(parts) >= 4:
             author = parts[1]
             filename = parts[2]
             b64_img = parts[3]
             try:
                 img_data = base64.b64decode(b64_img)
                 pil_img = Image.open(io.BytesIO(img_data))
                 ctk_img = CTkImage(pil_img, size=(300, 300))
                 self.add_message(f"{author}: надіслав(ла) зображення: {filename}", img=ctk_img)
             except Exception as e:
                 self.add_message(f"Помилка відображення: {e}")
     else:
         self.add_message(line)




 def open_image(self):
     file_name = filedialog.askopenfilename()
     if not file_name:
         return
     try:
         with open(file_name, "rb") as f:
             raw = f.read()
         b64_data = base64.b64encode(raw).decode()
         short_name = os.path.basename(file_name)
         data = f"IMAGE@{self.username}@{short_name}@{b64_data}\n"
         self.sock.sendall(data.encode())
         self.add_message('', CTkImage(light_image=Image.open(file_name), size=(300, 300)))
     except Exception as e:
         self.add_message(f"Не вдалося надіслати зображення: {e}")




 def change_theme(self, value):
     if value == 'Темна':
         set_appearance_mode('dark')
     else:
         set_appearance_mode('light')








 def toggle_show_menu(self):
     if self.is_show_menu:
         self.is_show_menu = False
         self.close_menu()
     else:
         self.is_show_menu = True
         self.show_menu()








 def show_menu(self):
     if self.frame_width <= 200:
         self.frame_width += self.menu_show_speed
         self.frame.configure(width=self.frame_width, height=self.winfo_height())
         if self.frame_width >= 30:
             self.btn.configure(text='◀')
             self.btn.lift()
     if self.is_show_menu:
         self.after(20, self.show_menu)








 def close_menu(self):
     if self.frame_width >= 0:
         self.frame_width -= self.menu_show_speed
         self.frame.configure(width=self.frame_width, height=self.winfo_height())
         if self.frame_width >= 30:
             self.btn.configure(text='▶')
             self.btn.lift()
     if not self.is_show_menu:
         self.after(20, self.close_menu)








 def adaptive_ui(self):
     self.chat_text.configure(width=self.winfo_width() - self.frame.winfo_width(),
                              height=self.winfo_height() - self.message_input.winfo_height() - 10)
     self.chat_text.place(x=self.frame.winfo_width()-1)








     self.message_input.configure(width=self.winfo_width() - self.frame.winfo_width()-self.send_button.winfo_width())
     self.message_input.place(x=self.frame.winfo_width(), y = self.winfo_height() - self.send_button.winfo_height())








     self.send_button.place(x=self.winfo_width() - self.send_button.winfo_width(),
                            y = self.winfo_height() - self.send_button.winfo_height())








     self.frame.configure(height=self.winfo_height())








     self.after(20, self.adaptive_ui)
















main = LogiTalk()
main.mainloop()















