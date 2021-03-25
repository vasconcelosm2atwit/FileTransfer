from tkinter import *
from tkinter import ttk
import socket
import threading
import os
import pickle
from PIL import ImageTk,Image
from tkinter import filedialog

LARGE_FONT= ("Verdana", 12) #FINAL VARIABLE FOR FONT AND SIZE

#SERVER APPLICATION ON SIMPLE FILE TRASNFER APPLICATION
#ENGINEERED BY:
#   MICHAEL VASCONCELOS
#   MICHELLE VASCONCELOS


# CONTROLLER CLASS, THIS CLASS IS RESPONSIBLE FOR RUNNING THE OTHER PAGES AND PROVIDING INFORMATION 
class ServerGui(Tk):

    def __init__(self, *args, **kwargs):
        
        Tk.__init__(self, *args, **kwargs)
        Tk.iconbitmap(self,default="images/test.ico")
        Tk.wm_title(self,"Server")

        self.geometry("800x600") #Original size

        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #intiate socket
        self.ip = socket.gethostbyname(socket.gethostname()) #Get IP
        self.port = "5000" #Initiate port
        self.newport = StringVar() #so it updates after each run
        self.newport.set("0") #initiate port holder for 0

        self.connected_client = StringVar() #updatable variable -> Holds Client connected
        self.connected_client.set("No client connected") #initiating
        self.connection_detected = StringVar() #updatable variable -> Connection_detected @Holds IP from user connected
        self.connection_detected.set("0") #0 = none, do something about this later

        self.files_being_shared_list = list()
        

        #Main container
        container = Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        

        #loads it then save fraames to this frame, make it sure we can
        #acess mltiple pages
        self.frames = {}

        for F in (StartPage,PageOne):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")


        self.show_frame(StartPage) #show start page

    # raise it
    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()

    #Initiate socket connection
    def start_server(self):
        server_address= (self.ip,int(self.port))
        self.sock.bind(server_address)
        self.sock.listen(100)


    #Create a handshake connection loop, stays open until its done
    def server_client_loop(self):
        arr = os.listdir("share") #Acess folder -> SHARE

        

        print("Files being shared: ")
        for x in range(len(arr)):
            a = 'share/' + arr[x]
            arr[x] = arr[x].replace(",","") #Rename files with a , on it to avoid error
            #print(str(x) + " " + arr[x]) #prints on cmd
            f = 'share/' + arr[x]
            os.rename(a,f)

        arr = os.listdir("share") #Acess folder -> SHARE

        for x in range(len(arr)):
            print(str(x) + " " + arr[x]) #prints on cmd

        self.files_being_shared_list = arr

        data_arr = pickle.dumps(arr) #Create a list using pickle DUMPing to send over to client
        print("connecting to files on share") #confirmation

        

        #connection loop
        while True:
            connection, client_address= self.sock.accept() #Accepts client connection

            self.client_connected = client_address #Holds client address

            self.connected_client.set(client_address[0]) #hold client IP
            self.connection_detected.set(connection) #Holds connection info

            print(connection) #Prints on console
            print(client_address[0])
            connection.send(data_arr)

            #threading the connection to hold the connection, starts connection loop
            threading.Thread(target=self.start_client,args=(connection,client_address,)).start()

    #Connection
    def start_client(self,connection,client_address):

        data = connection.recv(1024).decode() #RECEIVES DATA FROM CLIENT THIS IS THE FILE THE CLIENT HAS ASKED FOR
        path_change = 'share\\' + data #ASSIGN THE PATH TO THE DATA RECEIVED
        data = path_change #REASSIGN TO DATA
        
        #IF DATA DOES NOT EXIST RETURN A X0 CODE
        if not os.path.exists(data):
            connection.send("x0".encode())

        else:
            st = os.stat(data).st_size
            st = str(st)
            connection.send(bytes(st,'utf-8')) #send file size to the client
            #connection.send("file-exists".encode()) #SENDS CONFIRMATION THAT FILES EXIST TO CLIENT
            if data != '':
                file = open(data,'rb') #READ and WRITE FILE
                data = file.read(1024)
                while data:
                    connection.send(data)
                    data = file.read(1024)

                connection.shutdown(socket.SHUT_RDWR)
                connection.close()

##### INITIATING START PAGE, THIS IS THE INITIAL PAGE WHEN PROGRAM IS OPPENED  - START PAGE -------- ##################################   
class StartPage(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self,parent)
        #labeling page


        self.logo_l = Label(self)
        self.img_logo = Image.open("images/logo.png")
        self.img_logo = self.img_logo.resize((350,150),Image.ANTIALIAS)
        self.logo_l.image = ImageTk.PhotoImage(self.img_logo)

        label_logo = ttk.Label(self, image=self.logo_l.image)
        label_logo.pack(padx=10) #pack label

        label = ttk.Label(self, text="Please enter a port to start server", font=LARGE_FONT,style="BW.TLabel")
        label.pack(padx=10) #pack label

        self.ip_frame= Frame(self, width=100, height=50,pady=3)
        self.ip_frame.pack() # pack ip frame page this shows the ip information

        #running essential funcs
        self.labels(controller)
        self.buttons(controller)

        label2 = Label(self, text="Engineered By:\nMichael Vasconcenlos\nMichelle Vasconcelos",font=LARGE_FONT,)
        label2.pack(side=BOTTOM)

        

        #Label current IP and gets the port used for connection
    def labels(self,controller):
        label_ip_name = Label(self.ip_frame,text="Current Ip",font=LARGE_FONT).grid(row=0,column=0,sticky="w")
        label_show_Ip = Label(self.ip_frame,text=controller.ip, font=LARGE_FONT).grid(row=0,column=1,padx=5,sticky="e")
        
        #gets the port entry
        label_port_name = Label(self.ip_frame,text="Enter a Port",font=LARGE_FONT).grid(row=1,column=0,sticky="w")
        self.port_entry = ttk.Entry(self.ip_frame) 

        #grid
        self.port_entry.grid(row=1,column=1,padx=5)

    # THIS IS THE ACESS BUTTON TO RUN THE SERVER, ONCE BUTTON CONNECT IS PRESSED THIS FUNCTION IS ACTIVATED
    #   STARTS SERVER AND OPEN PORT
    def run_server(self,controller):
        self.set_Port(controller)
        controller.start_server()
        thread = threading.Thread(target=controller.server_client_loop)
        #make test_loop terminate when the user exits the window
        thread.daemon = True 
        thread.start()
        controller.show_frame(PageOne)

    # gets port entry
    def set_Port(self,controller):
        controller.port = self.port_entry.get()
        #self.newport = controller.port
        controller.newport.set(controller.port)
        print(controller.port)


        #change pages buttoms
    def buttons(self,controller):
        button = ttk.Button(self,text="Start server",
            command=lambda: self.run_server(controller))
        button.pack()


################# THIS IS PAGE ONE, THIS PAGE IS RESPONSIBLE TO DISPLAY THE CONNECTED CLIENTS ###############
class PageOne(Frame):
    def __init__(self,parent,controller):
        Frame.__init__(self,parent)
        label = Label(self,text="Server Initiated...", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        #Initiate frames
        self.server_info_frame = Frame(self,width=100)
        self.server_info_frame.pack()

        self.connected_info = Frame(self,width=100)
        self.connected_info.pack()
        self.buttons(controller)
        
        self.cvs = Canvas(self)
        self.files_information = Frame(self.cvs) 
        self.sb = Scrollbar(self,orient="vertical",command=self.cvs.yview)
        self.cvs.configure(yscrollcommand=self.sb.set)


        self.sb.pack(side="right",fill="y")
        self.cvs.pack(fill="both",expand=True)
        self.cvs.create_window((4,4), window=self.files_information, anchor="center", 
                                  tags="self.all_frame")

        self.files_information.bind("<Configure>", self.onFrameConfigure)

        self.shared_files(controller)


        self.info_txt = Frame(self,width=100)
        self.info_txt.pack()

        self.show_text() # show important text

        #essential functions
        self.labels(controller)
        

    def shared_files(self,controller):
        info_label = list()
        counter = 0
        for word in controller.files_being_shared_list:
            counter += 1
            info_label.append(ttk.Label(self.files_information,text=str(counter) + "-> " + word,wraplength=600,font=LARGE_FONT,justify=LEFT))

        if len(controller.files_being_shared_list) != 0:
            for i in range(len(controller.files_being_shared_list)):
                info_label[i].grid(row=(i+1),column=0,padx=5,pady=5,sticky="w")

    def onFrameConfigure(self,event):
        # update scrollregion after starting 'mainloop'
        # when all widgets are in Canvas
        self.cvs.configure(scrollregion=self.cvs.bbox('all'))

    #Labels that display current connect client
    def labels(self,controller):
        label_ip = Label(self.server_info_frame,text="Server Ip",font=LARGE_FONT).grid(row=0,column=0,sticky="w")
        label_show_Ip = Label(self.server_info_frame,text=controller.ip, font=LARGE_FONT).grid(row=0,column=1,sticky="w")
        label_port = Label(self.server_info_frame,text="Server Port",font=LARGE_FONT).grid(row=1,column=0,sticky="w")
        label_show_port = Label(self.server_info_frame,textvariable=controller.newport, font=LARGE_FONT).grid(row=1,column=1,sticky="w")

        client_info_label = Label(self.server_info_frame,text="Connect client: ",font=LARGE_FONT).grid(row=3,column=0,sticky="w")
        show_client_info = Label(self.server_info_frame,textvariable=controller.connected_client, font=LARGE_FONT).grid(row=3,column=1,sticky="w")

    #Button to activate next page
    def buttons(self,controller):
        button2 = ttk.Button(self,text="Show files being shared",
            command=lambda: self.shared_files(controller))
        button2.pack(side=TOP)

        button1 = ttk.Button(self,text="shutdown Server",
            command=lambda: self.close_server(controller))
        button1.pack(side=BOTTOM)

    #Funct to kill the page
    def close_server(self,controller):
        controller.destroy()

    #Shows information text
    def show_text(self):
        text = "If you wish to share files\n\nPlease add all files into the folder: [ Share ] in the same path as this application\n\nRestart the server application after new files have being added into the folder"
        text_info = Label(self.connected_info, text = text, wraplength=600,font=LARGE_FONT)
        text_info.grid(row=4,column=1,columnspan=3)


##################### PAGE TWO --- PAGE PROVIDES INFORMATION ON FILES BEING SHARED ########### NOT IN USE # MAYBE IN FUTURE UPDATE ###



#Running application
server = ServerGui() 
server.mainloop()