import im
import time

server = im.IMServerProxy("/Applications/XAMPP/xamppfiles/htdocs/MessagingClient/IMserver.php")
messagekey = {"Doctor": 0, "Nurse": 0}
lastseenmessagekey = None
userrole = None

def setconnection(userid, status):
    '''Sets the connection status of the user.'''
    connectionkey = "{}Connected".format(userid)
    server[connectionkey] = str(status)
    print("Connection for {} set to: {}".format(userid, status))

def reset():
    '''Resets the connection and status of the users.'''
    setconnection("Doctor", False)
    setconnection("Nurse", False)
    updateuserstatus("Doctor", "ready")
    updateuserstatus("Nurse", "waiting")
    print("All users disconnected and reset.")
    time.sleep(1)
    print("exiting now")
    time.sleep(2)

def setupuser():
    '''Sets the default status of the users. (doctor ready, nurse waiting)'''
    default = "unkown"
    doctorstatus = getstatus("Doctor") if "DoctorStatus" in server.keys() else default
    nursestatus = getstatus("Nurse") if "NurseStatus" in server.keys() else default
    if doctorstatus == default:
        updateuserstatus("Doctor", "ready")
    if nursestatus == default:
        updateuserstatus("Nurse", "waiting")
    print("Doctor Status: {}".format(getstatus('Doctor')))
    print("Nurse Status: {}".format(getstatus('Nurse')))

def checkconnection():
    '''Checks the connection status of both users.'''
    doctorstatus = checkconnectionindividual("Doctor")
    nursestatus = checkconnectionindividual("Nurse")
    if doctorstatus == nursestatus == "True":
        print("Doctor and Nurse are connected.")
    elif doctorstatus == "True" and nursestatus == "False":
        print("Only the Doctor is connected.")
    elif doctorstatus == "False" and nursestatus == "True":
        print("Only The Nurse is connected.")
    else:
        print("No one is connected.")

def checkconnectionindividual(userid):
    '''Checks the connection status of the user.'''
    connectionkey = "{}Connected".format(userid)
    try:
        status = server[connectionkey].strip()
        status = status.decode('utf-8') 
        # print("{} Connected? {}".format(userid, status)) #!debugging
    except KeyError:
        status = "False"
    return status

def getstatus(userid):
    '''Gets the status of the user. (ready or waiting)'''
    try:
        convertedstatus = server["{}Status".format(userid)].decode('utf-8').strip()
        return convertedstatus
    except KeyError:
        return "waiting"

def updateuserstatus(userid, status):
    '''Updates the status of the user. (ready or waiting)'''
    server["{}Status".format(userid)] = status

def statuschecker():
    '''Checks the status of the users and allows the user to override the current status.'''
    doctorstatus = getstatus("Doctor")
    nursestatus = getstatus("Nurse")
    if doctorstatus == "ready":
        print("Doctor's Turn to send the next message")
    elif nursestatus == "ready":
        print("Nurse's Turn to send the next message")
    else:
        print("ERROR.")
    time.sleep(1)
    override = input("Do you want to override the current status? (yes/no): ").strip().lower()
    if override == "yes":
        overridestatus(doctorstatus, nursestatus)
    else:
        print("Exiting now")
        time.sleep(1)

def statuscheckerinrecent():
    '''Similar to above method, with less functionality for mainfunction5.'''
    doctorstatus = getstatus("Doctor")
    nursestatus = getstatus("Nurse")
    if doctorstatus == "ready":
        print("Doctor's Turn to send the next message")
    elif nursestatus == "ready":
        print("Nurse's Turn to send the next message")
    else:
        print("ERROR.")
    time.sleep(1)

def overridestatus(doctor_status, nurse_status):
    '''Overrides the current status of the users, used in above method'''
    if doctor_status == "ready":
        updateuserstatus("Doctor", "waiting")
        updateuserstatus("Nurse", "ready")
        print("Nurse's Turn to send the next message")
        print("Exiting now")
        time.sleep(1)
    elif nurse_status == "ready":
        updateuserstatus("Nurse", "waiting")
        updateuserstatus("Doctor", "ready")
        print("Doctor's Turn to send the next message")
        print("Exiting now")
        time.sleep(1)
    else:
        print("ERROR")
        print("Exiting now")
        time.sleep(1)

def getlatestmessage(chosenuser):
    '''Gets the latest message from the chosen user. (Doctor or Nurse)'''
    reversekeys = sorted(server.keys(), key=getmessagekey, reverse=True) 
    for key in reversekeys:
        if chosenuser in key.decode('utf-8'):
            messagebody = server[key]
            if isinstance(messagebody, bytes):
                messagebody = messagebody.decode('utf-8')
            return key, messagebody
    return None, None 

def waitforreply(user, otheruser, sequence):
    '''Waits for a reply from the other user. (Doctor or Nurse)'''
    # print("Waiting for a message from {}.....".format(otheruser))
    while True:
        latestkey, latestmessage = getlatestmessage(otheruser) 
        if latestmessage:
            latestsequencee = getmessagekey(latestkey)  
            if latestsequencee > sequence:
                print("Previous Message from {}: {} (not updated)".format(otheruser, latestmessage))
                return
        time.sleep(5)

#user should be either "Doctor" or "Nurse"
def sendmessage(usertype):
    '''Sends a message from the user. (Doctor or Nurse)'''
    user = "Doctor" if usertype == 1 else "Nurse"
    if checkconnectionindividual(user) == "True":
        print("Current status of {}: {}".format(user, getstatus(user)))
        if getstatus(user) == "ready":
            otheruser = "Nurse" if usertype == 1 else "Doctor"
            messagekey[user] = messagekey[user] + 1
            sequence = messagekey[user]
            getcurrenttime = int(time.time() * 1000)
            print("Enter your message below:")
            message = input(">>> ")
            key = "message{}{}_{}".format(user, getcurrenttime, sequence)
            server[key] = message
            updateuserstatus(user, "waiting")
            updateuserstatus(otheruser, "ready")
            print("Message sent by {}: {}".format(user, message))
            waitforreply(user, otheruser, sequence)
        else:
            print("You have to wait for a reply before sending another message.")
            time.sleep(1)
            print("Exiting now")    
            time.sleep(2)
    else:
        print("{} is not connected. Please connect to send messages.".format(user))
        time.sleep(1)
        print("Exiting now")    
        time.sleep(2)

def searchspecificmessage():
    '''Searches for a specific message using the message key.'''
    searchinput = input("Enter the message key: ")
    convertedsearchinput = searchinput.encode('utf-8') if isinstance(searchinput, str) else searchinput
    if convertedsearchinput in server.keys():
        message = server[convertedsearchinput].decode('utf-8')
        print("the message you are searching for is: {}".format(message))
    else:
        print("key '{}' does not exist.".format(searchinput))

def getmessagekey(key):
    '''Gets the message key from the message.'''
    if isinstance(key, bytes):
        key = key.decode('utf-8')
    removeletters = key.split('message')[-1]
    onlynumbers = filter(str.isdigit, removeletters)
    allnumbers = ''.join(onlynumbers)
    if allnumbers: 
        return int(allnumbers)
    else:
        return 0 

def showmessages(chosenfilter=None):
    '''Shows all the messages in the chat history. (Doctor or Nurse)'''
    print("Please Wait...")
    time.sleep(1)
    print("Chat History:")
    sortedkeys = sorted(server.keys(), key=getmessagekey)
    for key in sortedkeys:
        if isinstance(key, bytes):
            key = key.decode('utf-8')
            if chosenfilter and chosenfilter not in key:
                continue
        message = server[key]
        if isinstance(message, bytes):
            message = message.decode('utf-8')
        sender = "Doctor" if "Doctor" in key else "Nurse"
        print(f" {sender}: {message.strip()} (with key: {key})") #! format method not workinf
    print("End of chat history")

def clearmessages():
    '''Clears all the messages in the chat history.'''
    server.clear()

def deletemessage():
    '''Deletes a specific message using the message key.'''
    messageid = input("Enter message ID (key) to delete: ")
    
    convertedmessageid = messageid.encode('utf-8') if isinstance(messageid, str) else messageid
    if convertedmessageid in server.keys():
        del server[convertedmessageid]
        print("Message with ID {} deleted.".format(messageid))
    else:
        print("Key {} not found.".format(messageid))

#--------------------------------------------------------------

def mainfunction1():
    '''Connects the user to the server. (Doctor or Nurse)'''
    global userrole
    print("Press (1) if you are a Doctor")
    print("Press (2) if you are a Nurse")
    userid = input(">>> ")
    if userid == "1":
        userrole = "Doctor"
        setconnection(userrole, True)
    elif userid == "2":
        userrole = "Nurse"
        setconnection(userrole, True)
    else:
        print("Invalid selection. Exiting...")
        return
    print("{} connected successfully.".format(userrole))
    time.sleep(1)
    print("exiting now")
    time.sleep(2)


def mainfunction2():
    '''Disconnects the user from the server. (Doctor or Nurse)'''
    global userrole
    if userrole is None:
        print("No user is currently connected.")
        time.sleep(1)
        return
    else:
        setconnection(userrole, False)
        print("{} disconnected".format(userrole))
        userrole = None
    time.sleep(1)
    print("exiting now")
    time.sleep(2)


    userid = input(">>> ")
    setconnection("Doctor" if userid == "1" else "Nurse", False)
    print("Disconnected.")
    time.sleep(1)
    print("exiting now")
    time.sleep(2)

def mainfunction3():
    '''Checks the connection status of the users.'''
    checkconnection()
    time.sleep(1)
    print("exiting now")
    time.sleep(2)

def mainfunction4():
    '''Sends a message from the user. (Doctor or Nurse)'''
    global userrole
    if userrole is None:
        print("Please connect first as either a Doctor or a Nurse.")
        time.sleep(1)
        return
    try: 
        if userrole not in ["Doctor", "Nurse"]:
            raise ValueError("Error.")
        usertype = 1 if userrole == "Doctor" else 2
        sendmessage(usertype)
        time.sleep(1)
        usertype = 2 if usertype == 1 else 1
    except ValueError:
        print("Error")
        time.sleep(1)

def mainfunction5():
    '''Gets the most recent message from the other user.'''
    global lastseenmessagekey
    global userrole
    if userrole is None:
        print("Please connect first.")
        return
    chosenuser = "Doctor" if userrole == "Nurse" else "Nurse"
    latestkey, latestmessage = getlatestmessage(chosenuser)
    if latestkey and latestkey != lastseenmessagekey:
        print("Most recent message from other user:\n {}".format(latestmessage))
        lastseenmessagekey = latestkey
    else:
        print("NO NEW MESSAGE HAS BEEN SENT YET")
        time.sleep(1)
        print("Please wait for a message to be sent.")
        time.sleep(1)
        statuscheckerinrecent()
        time.sleep(1)
        print("You can press (3) to see if the other user is still connected")
    time.sleep(1)
    print("exiting now")
    time.sleep(2)

def mainfunction6():
    '''Shows all the messages in the chat history. (allows filtering)'''
    filter = input("Do you want to filter messages? (yes/no): ").lower().strip()
    chosenfilter = None
    if filter == "yes":
        newchoice = input("Enter (1) To see Messages sent by doctor or (2) to see messages sent by nurse: ")
        if newchoice not in ["1", "2"]:
            time.sleep(1)
            print("Invalid choice. Exiting...")
            time.sleep(1)
            return
        chosenfilter = "Doctor" if newchoice == "1" else "Nurse"
    showmessages(chosenfilter)
    time.sleep(1)
    print("exiting now")
    time.sleep(2)

def mainfunction7():
    '''Shows a specific message using the message key.'''
    searchspecificmessage()
    time.sleep(1)
    print("exiting now")
    time.sleep(2)

def mainfunction8():
    '''Deletes all the messages in the chat history.'''
    clearmessages()
    print("All messages deleted.")
    time.sleep(1)
    print("exiting now")
    time.sleep(2)

def mainfunction9():
    '''Deletes a specific message using the message key.'''
    deletemessage()
    time.sleep(1)
    print("Exiting Now")
    time.sleep(2)

def mainfunction10():
    '''Prints all the keys in the chat history.'''
    print("Getting all keys...")
    time.sleep(1)
    print(server.keys())
    time.sleep(1)
    print("Exiting now")
    time.sleep(2)

def displaymenu():
    '''Displays the menu for the user in python terminal'''
    print("---------------------------------")
    print(" ")
    print("Welcome to the Messaging System")
    print(" ")
    print("OPTIONS:")
    print("1. Connect")
    print("2. Disconnect")
    print("3. Check Connection Status")
    print("4. Send Message")
    print("5. Get Most Recent Message")
    print("6. Show All Messages")
    print("7. Show Specific Message (using key)")
    print("8. Delete All Messages")
    print("9. Delete Specific Message (using key)")
    print("10. Print all keys")
    print("11. Quit")
    print(" ")
    print("X. Instructions")
    print("Z. Check and Override Status")
    print("R. Disconnect and Reset")
    print(" ")
    print("---------------------------------")



#--------------------------------------------------------------

def main():
   # #!debugging prints
    # setupuser()
    # checkconnectionindividual("Doctor")
    # checkconnectionindividual("Nurse")

    while True:
        
        displaymenu()

        try:
            print("Select an option")
            choice = input(">>> ")
            print("---------------------------------")
            if choice == "1":
                mainfunction1()
            elif choice == "2":
                mainfunction2()
            elif choice =="3":
                mainfunction3()
            elif choice == "4":
                mainfunction4()
            elif choice == "5":
                mainfunction5()
            elif choice == "6":
                mainfunction6()
            elif choice == "7":
                mainfunction7()
            elif choice == "8":
                mainfunction8()
            elif choice == "9":
                mainfunction9()
            elif choice == "10":
                mainfunction10()
            elif choice == "11":
                print("Disconnecting Both Users...")
                reset()
                print("Exiting Program..")
                time.sleep(2)
                break
            elif choice == "x" or choice == "X":
                print("Instructions:")
                print("1. You will only be able to send a message once it is your turn, Press (Z) to check.")
                time.sleep(0.5)
                print("2. You can only send one message at a time.")
                time.sleep(0.5)
                print("3. Press (4) to send a message.")
                time.sleep(0.5)
                print("4. You can check the most recent message from the other user by pressing (5).")
                time.sleep(0.5)
                print("5. repeat steps (3) and (4) to hold a conversation.")
                time.sleep(2)
                print("exiting now")
                time.sleep(2)
            elif choice == "z" or choice == "Z":
                statuschecker()
            elif choice == "r" or choice == "R":
                reset()
            else:
                print("Please enter a number between 1 and 10.")
                time.sleep(1)
            print("\n")
        except KeyboardInterrupt:
            reset()
            print("Exiting Program..")
            time.sleep(2)
            break

        

if __name__ == "__main__":
    main()