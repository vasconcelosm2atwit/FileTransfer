from tkinter import *
from tkinter import ttk
import socket
import threading
import os
import pickle
from PIL import ImageTk, Image
from tkinter import filedialog
import tkinter.font as font

LARGE_FONT= ("Verdana", 12)

## CLIENT APPLICATION FOR SIMPLE FILE TRASNFER
#ENGINEERED BY Michael Vasconcelos



#CONTROLLER CLASS, THIS CLASS IS RESPONSIBLE FOR CONTROLLER THE OTHER PAGES AND CONNECTING TO SERVER
class Client(Tk):

    def __init__(self, *args, **kwargs):
        
        Tk.__init__(self, *args, **kwargs)

        Tk.iconbitmap(self,default="images/test.ico")  #Load Icon
        Tk.wm_title(self,"Client") #name client

        self.geometry("800x600") #Resolution

        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #Starting socket

        #Essential variables for connection holding
        self.server_ip = ""
        self.server_port = ""

        #Holding server information IP AND PORT
        self.connected_ip = StringVar()
        self.connected_port = StringVar()
        self.connected_ip.set("none")
        self.connected_port.set("none")
        #File information variable
        self.files_pack = StringVar()
        self.files_pack.set("0")

        self.file_value = StringVar()
        self.file_value.set("0")

        self.file_to_download_name = StringVar()
        self.file_to_download_name.set("")

        #Download bar updatable variable
        self.download_bar = IntVar()
        self.download_bar.set(0)

        self.finish = StringVar()
        self.finish.set("")

        self.bar_max = StringVar()
        self.bar_max.set("")

        #Initiating container
        container = Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        #loads it then save fraames to this frame, make it sure we can
        #acess mltiple pages
        self.frames = {}

        for F in (StartPage,PageOne,PageTwo):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")


        self.show_frame(StartPage) #Display starting page


    def get_page(self, page_name):
        for page in self.frames.values():
            if str(page.__class__.__name__) == page_name:
                return page
        return None 

    #Initiate connection to desired server
    def initiate_connection(self,serverIp,serverPort):
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server_address = (serverIp,int(serverPort))
        self.sock.connect(self.server_address)
        self.connect_to_server()

    #confirm connection to server
    def connect_to_server(self):
        print("Connecting......")
        test = self.sock.recv(1024) #Gets response from server
        test_arr = pickle.loads(test) #Gets the list of items from the server to display on client
        self.file_value.set(repr(test_arr)) #adds to variable

    # raise frames
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


###################### STATING PAGE, THIS PAGE IS RESPONSIBLE FOR CONNECTING TO SERVER AND ASKING FOR LOGIN INFO (IP AND PORT) ##########
class StartPage(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self,parent)
        
        self.logo_l = Label(self)
        self.img_logo = Image.open("images/logo.png")
        self.img_logo = self.img_logo.resize((350,150),Image.ANTIALIAS)
        self.logo_l.image = ImageTk.PhotoImage(self.img_logo)

        label_logo = ttk.Label(self, image=self.logo_l.image)
        label_logo.pack(padx=10) #pack label

        label = ttk.Label(self, text="Please Enter Server Adress To Connect", font=LARGE_FONT,style="BW.TLabel")
        label.pack(padx=10) #pack label

        #Page frame
        self.connect_frame = Frame(self,width=100,height=100)
        self.connect_frame.pack()

        self.labels()
        self.buttons(controller)

        label2 = Label(self, text="Engineered By:\nMichael Vasconcelos",font=LARGE_FONT,)
        label2.pack(side=BOTTOM)

    # LABELS ON PAGE, THIS ASK FOR THE INFORMATION
    def labels(self):
        login_ip = Label(self.connect_frame,text="Enter Server IP: ", font=LARGE_FONT).grid(row=0,column=0,sticky="w")
        login_port = Label(self.connect_frame,text="Enter Port: ", font= LARGE_FONT).grid(row=1,column=0,sticky="w")

        self.ip_entry = ttk.Entry(self.connect_frame)
        self.port_entry = ttk.Entry(self.connect_frame)

        self.ip_entry.grid(row=0,column=1)
        self.port_entry.grid(row=1,column=1)

    #SENTS THE INFORMATION ENTRIES
    def set_entries(self,controller):
        controller.server_ip = self.ip_entry.get()
        controller.server_port = self.port_entry.get()

        controller.connected_ip.set(controller.server_ip)
        controller.connected_port.set(controller.server_port)

    #CONNECT TO SERVER
    def connect(self,controller):
        self.set_entries(controller)
        controller.initiate_connection(controller.server_ip,controller.server_port)
        controller.show_frame(PageOne)
        
    #BUTTONS
    def buttons(self,controller):
        button = ttk.Button(self,text="Connect to Server",
            command=lambda: self.connect(controller))
        button.pack(side=TOP)

####################################################################### PAGE ONE ################################################
######## THIS PAGE IS RESPONSIBLE FOR SHOWING THE FILES FROM SERVER, THIS IS WHERE YOU ARE ABLE TO DOWNLOAD FILES
class PageOne(Frame):
    def __init__(self,parent,controller):
        Frame.__init__(self,parent)
        label = Label(self,text="Connected to server", font=LARGE_FONT)
        label.pack(pady=10,padx=10)


        self.image_files_func() #initiate images

        #server frame
        self.server_info_f = Frame(self,height=50,width=100)
        self.server_info_f.pack()

        self.buttons(controller) #pages buttons

        #Canvas for scrollbar and pictures
        self.cvs = Canvas(self)
        self.all_frame = Frame(self.cvs) 
        self.sb = Scrollbar(self,orient="vertical",command=self.cvs.yview)
        self.cvs.configure(yscrollcommand=self.sb.set)


        self.sb.pack(side="right",fill="y")
        self.cvs.pack(fill="both",expand=True)
        self.cvs.create_window((4,4), window=self.all_frame, anchor="center", 
                                  tags="self.all_frame")

        self.all_frame.bind("<Configure>", self.onFrameConfigure)

        self.labels(controller)
        self.print_values(controller)

    def onFrameConfigure(self,event):
        # update scrollregion after starting 'mainloop'
        # when all widgets are in Canvas
        self.cvs.configure(scrollregion=self.cvs.bbox('all'))

    #this runs the server on a loop until its terminated, this is the button activation
    def run_server_loop(self,controller,fileName):
        print("sent: " + fileName)
        controller.file_to_download_name.set(fileName)
        thread = threading.Thread(target=lambda: self.download_File(controller,fileName))
        #make test_loop terminate when the user exits the window
        thread.daemon = True 
        thread.start()
        #x = 
        controller.show_frame(PageTwo)

    #DOWNLOADING FILE
    def download_File(self,controller,fileName):
        loading = 0 #loading for bar variable
        counter = 0 #counter for loading bar value
        r = 0
        kb_f = 0
        mb_f = 0
        gb_f = 0

        if fileName:
            print("file name: "+ fileName)#Confirms the file name on cmd
            controller.sock.send(fileName.encode()) #sends file to server

            confirmation = controller.sock.recv(1024) #receives confirmation from server
            st = str(confirmation)
            result = re.sub('[^0-9]','', st)
            #st = str(result)
            print("confirmation: " + result)

            r = float(result)
            kb_f = float(1024)
            mb_f = float(kb_f** 2)
            gb_f= float(mb_f ** 3) # 1,073,741,824

            x_f = 0

            if r < kb_f:
                x = '{0} {1}'.format(r,'Bytes' if 0 == r > 1 else 'Byte')
                controller.bar_max.set(x)
            elif kb_f <= r < mb_f:
                x = '{0:.2f} KB'.format(r/kb_f)
                controller.bar_max.set(x)
            elif mb_f <= r < gb_f:
                x = '{0:.2f} MB'.format(r/mb_f)
                controller.bar_max.set(x)
            elif gb_f <= r :
                x =  '{0:.2f} GB'.format(r/gb_f)
                controller.bar_max.set(x)

            #controller.bar_max.set(result)


            write_name = 'from_server ' + fileName #re write file ADD from_server to it
            if os.path.exists(write_name): 
                os.remove(write_name)

            with open(write_name,'wb') as file:
                #start loop -> loop ends when file is fully downloaded
                while True:
                    data = controller.sock.recv(1024)

                    loading = "{!r}".format(data) #write file into loading
                    
                    #Loading bar
                    if counter > 10:
                        counter += 0.001
                        controller.download_bar.set(counter)
                    elif counter > 30:
                        counter += 0.0001
                        controller.download_bar.set(counter)
                    elif counter > 50:
                        counter += 0.0001
                        controller.download_bar.set(counter)
                    elif counter > 70:
                        counter += 0.00001
                        controller.download_bar.set(counter)
                    elif counter > 80:
                        counter += 0.000001
                        controller.download_bar.set(counter)
                    elif counter > 90:
                        counter = 90
                        controller.download_bar.set(counter)
                    else:
                        counter +=0.01
                        controller.download_bar.set(counter) #update loading bar

                    if not data:
                        break

                            
                    
                   # self.update()#update page

                    file.write(data) #write data

                print(fileName,'successfully downloaded.')#sends confirmation to cmd that file is fully downloaded
                controller.download_bar.set(100)#sets to 100% to max download bar
                self.update()# update page again
                controller.finish.set("done")
                #shutdown server
                controller.sock.shutdown(socket.SHUT_RDWR)
                controller.sock.close()
                fileName = ""

    #labels for information
    def labels(self,controller):
        ip_label = Label(self.server_info_f,text="IP",font=LARGE_FONT).grid(row=0,column=0,sticky="e")
        ip_show = Label(self.server_info_f,textvariable=controller.connected_ip,font=LARGE_FONT).grid(row=0,column=1,sticky="w")
        port_label = Label(self.server_info_f,text="Port",font=LARGE_FONT).grid(row=1,column=0,sticky="e")
        port_show = Label(self.server_info_f,textvariable=controller.connected_port,font=LARGE_FONT).grid(row=1,column=1,sticky="w")
        
    #display files
    def files_display(self,controller):
        hold = controller.file_value.get()
 
        hold = hold[1:] # Remove first character of the string. -> removes the "[" on first index of the String
        hold = hold[:-1] #Remove last character on the string. -> Removes the ']' on the last index of the String
        hold = hold.replace("'","")
        hold = hold.strip()
        files_all = hold.split(",") #Splits at , (commas) to a list
        test_list = list()

        for i in range(len(files_all)):
            test_list.append(files_all[i])


        images_list = list()
        py_list = list()
        text_list = list()
        pdf_list = list()
        rest_list = list()


        for i in files_all:
            rest_list.append(i) 

        self.show_all_files_img(controller,rest_list)

    #Initiate all pictures from folder image on client
    def image_files_func(self):

        width=50
        height=50

        self.all_l = Label(self)
        self.img_all = Image.open("images/files.png")
        self.img_all = self.img_all.resize((50,50),Image.ANTIALIAS)
        self.all_l.image = ImageTk.PhotoImage(self.img_all)

        self.docx_l = Label(self)
        self.img_docx = Image.open("images/docx.png")
        self.img_docx = self.img_docx.resize((50,50),Image.ANTIALIAS)
        self.docx_l.image = ImageTk.PhotoImage(self.img_docx)

        self.pic_l = Label(self)
        self.img_pic = Image.open("images/pic.png")
        self.img_pic = self.img_pic.resize((50,50),Image.ANTIALIAS)
        self.pic_l.image = ImageTk.PhotoImage(self.img_pic)

        self.mp3_l = Label(self)
        self.img_mp3 = Image.open("images/mp3.png")
        self.img_mp3 = self.img_mp3.resize((50,50),Image.ANTIALIAS)
        self.mp3_l.image = ImageTk.PhotoImage(self.img_mp3)

        self.pdf_l = Label(self)
        self.img_pdf = Image.open("images/pdf.png")
        self.img_pdf = self.img_pdf.resize((50,50),Image.ANTIALIAS)
        self.pdf_l.image = ImageTk.PhotoImage(self.img_pdf)

        self.py_l = Label(self)
        self.img_py = Image.open("images/py.png")
        self.img_py = self.img_py.resize((50,50),Image.ANTIALIAS)
        self.py_l.image = ImageTk.PhotoImage(self.img_py)

        self.txt_l = Label(self)
        self.img_txt = Image.open("images/txt.png")
        self.img_txt = self.img_txt.resize((50,50),Image.ANTIALIAS)
        self.txt_l.image = ImageTk.PhotoImage(self.img_txt)

        self.vid_l = Label(self)
        self.img_vid = Image.open("images/video.png")
        self.img_vid = self.img_vid.resize((50,50),Image.ANTIALIAS)
        self.vid_l.image = ImageTk.PhotoImage(self.img_vid)

        self.zip_l = Label(self)
        self.img_zip = Image.open("images/zip.png")
        self.img_zip = self.img_zip.resize((50,50),Image.ANTIALIAS)
        self.zip_l.image = ImageTk.PhotoImage(self.img_zip)


    #add all pictures to file names
    def show_all_files_img(self,controller,all_holder):
        all_files_list = all_holder

        all_show = list()
        all_labels = list()
        all_buttons = list()

        for word in all_files_list:
            word =  word.strip()
            if word.endswith(".png"):
                all_show.append(ttk.Label(self.all_frame,image=self.pic_l.image))
            elif word.endswith(".docx"):
                all_show.append(ttk.Label(self.all_frame,image=self.docx_l.image))
            elif word.endswith(".pdf"):
                all_show.append(ttk.Label(self.all_frame,image=self.pdf_l.image))
            elif word.endswith(".py"):
                all_show.append(ttk.Label(self.all_frame,image=self.py_l.image))
            elif word.endswith(".mp3"):
                all_show.append(ttk.Label(self.all_frame,image=self.mp3_l.image))
            elif word.endswith(".mp4"):
                all_show.append(ttk.Label(self.all_frame,image=self.vid_l.image))
            elif word.endswith(".zip"):
                all_show.append(ttk.Label(self.all_frame,image=self.zip_l.image))
            else:
                all_show.append(ttk.Label(self.all_frame,image=self.all_l.image))
            
            all_labels.append(ttk.Label(self.all_frame,text=word,wraplength=600,font=LARGE_FONT,justify=LEFT))
            all_buttons.append(ttk.Button(self.all_frame,text="download",
                command=lambda word=word: self.run_server_loop(controller,word)))

        if len(all_files_list) != 0:
            for i in range(len(all_files_list)):
                all_show[i].grid(row=(i+1),column=1,padx=5,pady=5,sticky="w")
                all_labels[i].grid(row=(i+1),column=2,padx=5,pady=5,sticky="w")
                all_buttons[i].grid(row=(i+1),column=3,padx=5,pady=5,sticky="w")


    #print file names on cmd for confirmation
    def print_values(self,controller):
        hold = controller.file_value.get()
 
        hold = hold[1:] # Remove first character of the string. -> removes the "[" on first index of the String

        hold = hold[:-1] #Remove last character on the string. -> Removes the ']' on the last index of the String

        test1 = hold.split(",") #Splits at , (commas) to a list

    #button to acess next page
    def buttons(self,controller):
        button = ttk.Button(self,text="Show Shared Files By The Server",style="C.TButton",
            command=lambda: self.files_display(controller))
        button.pack(side=TOP)

################################################### PAGE TWO ###########################
#THIS PAGE IS RESPONSIBLE FOR SHOWING THE DOWNLOAD STATUS AND DOWNLOAD BAR
class PageTwo(Frame):
    def __init__(self,parent,controller):
        Frame.__init__(self,parent)
        label = Label(self,text="Downloading.....", font=LARGE_FONT)
        label.pack(pady=10,padx=10)
        self.solve = " "

        self.controller = controller #STARTS CONTROLLER

        #frame
        self.page2_f = Frame(self,height=100,width=100)
        self.page2_f.pack()
        #text label
        self.page3_label(controller)

        #progress bar
        self.progress = ttk.Progressbar(self,orient="horizontal",maximum = 100, length=200,
            mode="determinate", variable=controller.download_bar)
        self.progress.pack()
        
        #pack labels and buttons
        self.pack_labels(controller)
        self.buttons(controller,PageOne)
        self.check_if_done(controller)
        

    # more labels
    def page3_label(self,controller):
        self.text_l = Label(self.page2_f,text="File:",font=LARGE_FONT)
        self.text_label = Label(self.page2_f,textvariable=controller.file_to_download_name,font=LARGE_FONT)
        self.file_label = Label(self.page2_f,text = "Size:",font=LARGE_FONT)
        self.file_size_l = Label(self.page2_f,textvariable=controller.bar_max,font=LARGE_FONT)
        self.t2_label = Label(self,text="Download completed!",font=LARGE_FONT)

    def pack_labels(self,controller):
        self.text_l.grid(row=0,column=0,sticky="w")
        self.text_label.grid(row=0,column=1,sticky="w")
        self.file_label.grid(row=1,column=0,sticky="w")
        self.file_size_l.grid(row=1,column=1,stick="w")

    def check_if_done(self,controller):
        if controller.finish.get():
            self.button2.pack()
            self.t2_label.pack()

        self.after(1,lambda: self.check_if_done(controller))



    #RECONNECT TO SERVER WHEN THE FILE IS DONE DOWNLOADING AND USER WANTS TO DOWNLOAD MORE FILE
    def reconnect(self,controller,PageTwo):
        self.button2.pack_forget()
        self.t2_label.pack_forget()
        controller.finish.set("")   
        print("reconnect")
        controller.initiate_connection(controller.server_ip,controller.server_port)
        controller.show_frame(PageOne)
        controller.download_bar.set(0)

    #BUTTONS
    def buttons(self,controller,PageOne):
        self.button2 = Button(self,text="Download More Files",
            command=lambda: self.reconnect(controller,PageOne))

#runs client
client = Client()
client.mainloop()
