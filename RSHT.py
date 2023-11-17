import json
import socket, os, sys
from time import sleep
import PySimpleGUI as sg
from threading import Thread
from _thread import start_new_thread
from PySimpleGUI import Window, Text, Input, Button, Output, WIN_CLOSED


class RSHT:
    def __init__(self, sock=None):
        self.debug = False
        self.disconnect_from = None

        self.clientsdict = {
        "shell-1":"",
        "shell-2":"",
        "shell-3":"",
        "shell-4":"",
        "shell-5":"",
        "shell-6":"",
        "shell-7":"",
        "shell-8":"",
    }
        
        if sock is None:
            self.sock = socket.socket()
            sock = True


    def threaded(self, s, n, name):
        broken = None
        while True:
            if broken:
                print(f"Connection lost with {name}")
                try:
                    s.close(0)
                    s.shutdown(2)
                except:
                    pass
                self.clientsdict[n] = ""
                self.the_n -= 1
                self.window[n].update("")
                self.window[n].update(disabled=True)
                self.window[f"exit-{n}"].update(disabled=True)
                self.current_sock = None
                break
            try:
                data = s.recv(1024)
            except ConnectionAbortedError:
                broken = True
            except ConnectionResetError:
                broken = True
            except OSError:
                broken = True
            else:
                if not data:
                    broken = True
                else:
                    msg = data.decode("cp850")
                    if not(msg.isspace() or msg == "") and not(self.debug):
                        print(name+"-> "+msg, end="")
                    if self.debug:
                        print(self.disconnect_from)


    def handler(self, host, port):
        self.sock.bind((host, port))
        print(f"Address {host}:{port} binded successfully.")
        self.sock.listen()
        print("Listening...")
        self.the_n=0
        while True:
            conn, raddr = self.sock.accept()
            if self.debug:
                print(type(conn))
            #self.the_n+=1

            c=0
            for client in list(self.clientsdict.keys()):
                c+=1
                if self.clientsdict[client] == "":
                    if self.debug:
                        print(client)
                    self.clientsdict[client] = conn
                    self.window[client].update(client.replace("shell-", "Client "))
                    self.window[client].update(disabled=False)
                    self.window[f"exit-{client}"].update(disabled=False)
                    break
                if c == 8:
                    conn.send(b"Server is at his max capacity, try again later.")
                    conn.close()
                    break

            #self.clientsdict[f"shell-{self.the_n}"] = conn
            name = f"Client{client.replace('shell-', '')}"
            print(f"New connection established with {raddr[0]}:{raddr[1]}")
            start_new_thread(self.threaded, (conn, client, name,))

    
    def broadcast(self, message):
        for client in list(self.clientsdict.values()):
            if type(client) == socket.socket:
                client.send(message.encode())
            else:
                pass


    def sender(self, s, msg):
        if self.debug:
            print("Message sent.")
        s.send(msg)


    def GUI(self):
        sg.theme("DarkBlue2")

        if self.debug:
            dbgbtn = sg.Button("show self.clientsdict", key="sscd")
        else:
            dbgbtn = sg.Text(visible=False)

        button_layout = [
            [ 
                Text("1."), Button("", button_color="black on white", disabled=True, expand_x=True, key="shell-1"),
                Button("X", size=(2,1), button_color="black on indian red", disabled=True, key="exit-shell-1")
            ],
            [ 
                Text("2."), Button("", button_color="black on white", disabled=True, expand_x=True, key="shell-2"),
                Button("X", size=(2,1), button_color="black on indian red", disabled=True, key="exit-shell-2")
            ],
            [ 
                Text("3."), Button("", button_color="black on white", disabled=True, expand_x=True, key="shell-3"),
                Button("X", size=(2,1), button_color="black on indian red", disabled=True, key="exit-shell-3") 
            ],
            [ 
                Text("4."), Button("", button_color="black on white", disabled=True, expand_x=True, key="shell-4"),
                Button("X", size=(2,1), button_color="black on indian red", disabled=True, key="exit-shell-4") 
            ],
            [ 
                Text("5."), Button("", button_color="black on white", disabled=True, expand_x=True, key="shell-5"),
                Button("X", size=(2,1), button_color="black on indian red", disabled=True, key="exit-shell-5")
            ],
            [ 
                Text("6."), Button("", button_color="black on white", disabled=True, expand_x=True, key="shell-6"),
                Button("X", size=(2,1), button_color="black on indian red", disabled=True, key="exit-shell-6") 
            ],
            [
                Text("7."), Button("", button_color="black on white", disabled=True, expand_x=True, key="shell-7"),
                Button("X", size=(2,1), button_color="black on indian red", disabled=True, key="exit-shell-7")
            ],
            [ 
                Text("8."), Button("", button_color="black on white", disabled=True, expand_x=True, key="shell-8"),
                Button("X", size=(2,1), button_color="black on indian red", disabled=True, key="exit-shell-8")
            ],
            [ 
                dbgbtn
            ]
        ]

        layout = [ 
            [ sg.Col(button_layout, expand_x=True) ],
            [ 
                Input("", expand_x=True, key="-msg-to-send-"), 
                Button("Send", key="-send-", button_color="black on white", bind_return_key=True, size=(5, 1)),
                Button("Broadcast", key="-broadcast-", button_color="black on indian red", size=(10, 1)),
                Button("Keep On Top", button_color="black on indian red", size=(10, 1), key="-kot-")
            ],
            [ Output(key="-output-", expand_x=True, expand_y=True, background_color="black", text_color="white") ]
            ]

        self.window = sg.Window(title="TCP Client Manager MultiThread",layout=layout, resizable=True, icon="icon.ico", titlebar_background_color="grey", finalize=True)
        self.window.maximize()

        green = "DarkSeaGreen4"
        red = "indian red"

        kot = False
        broadcast = False
        self.current_sock = None
        

        while True:
            event, value = self.window.read()
            

            if self.debug:
                print(f"Event : {event}")
                print(f"Value : {value}")

            if event == WIN_CLOSED:
                self.sock.close()
                break

            else:
                msg = value["-msg-to-send-"]
                if event == "-send-":
                    if broadcast:
                        start_new_thread(self.broadcast, (msg,))
                        self.window["-msg-to-send-"].update("")

                    else:
                        if self.current_sock is not None:
                            if msg == "cls":
                                self.window["-output-"].update("")
                            else:
                                start_new_thread(self.sender, (self.current_sock, msg.encode()))
                            self.window["-msg-to-send-"].update("")
                        else:
                            if self.debug:
                                print("Self.CurrentSock is None?")
                            else:
                                pass
                    self.window.refresh()


                elif event == "-broadcast-":      
                    broadcast = not(broadcast)
                    if self.debug:    
                        print(f"Broadcast : {broadcast}")
                    if broadcast:
                        self.window["-broadcast-"].update(button_color="DarkSeaGreen4")
                    else:
                        self.window["-broadcast-"].update(button_color="black on indian red")
                    self.window.refresh()
                        

                elif event == "-kot-":      
                    kot = not(kot)
                    if self.debug:    
                        print(f"Kot : {kot}")
                    if kot:
                        self.window["-kot-"].update(button_color="DarkSeaGreen4")
                    else:
                        self.window["-kot-"].update(button_color="black on indian red")
                    self.window.refresh()
                    self.window.TKroot.wm_attributes("-topmost", kot)

                elif "exit-" in event:
                    self.disconnect_from = event.replace("exit-", "")
                    tmpsock = self.clientsdict[self.disconnect_from]
                    try:
                        tmpsock.shutdown(2)
                        tmpsock.close()
                    except Exception as e:
                        if self.debug:
                            print("Error closing socket")
                        else:
                            pass

                elif event == "sscd":
                    print(self.clientsdict)

                elif event == "stn":
                    print(self.the_n)

                elif event.startswith("shell-"):
                    print(f"Intreacting with Client{event.replace('shell-', '')}")
                    self.current_sock = self.clientsdict[event]
                    if self.debug:
                        print(f"Current sock : {self.current_sock}")





rsht = RSHT()                                                    #MAIN CLASS
GUI = Thread(target=rsht.GUI)                                    #GUI and SENDING MESSAGES 

var = json.load(open("config.json"))
host = var["host"]
port = var["port"]

if port.isdigit():
    port = int(port)
else:
    sg.theme("DarkBlue14")
    sg.Popup("Use a valid port in config file.", icon="icon.ico", no_titlebar=True, auto_close_duration=1)
    sys.exit()

handler = Thread(target=rsht.handler, args=[host, int(port),]) #SERVER AND CLIENTS MANAGING

GUI.start()
sleep(2)
handler.start()