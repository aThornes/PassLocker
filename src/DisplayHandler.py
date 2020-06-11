#This is the display handler for Pass Locker 
#---------------------------------------------
#Author: Adam Thornes
#OS: Rasperian
#Date: 08/01/2019
#File Version: v2.0.2
#---------------------------------------------

import time, os
#Dialouge Handler
fastType = False

def OverriteTypeDelay(fastOn): 
    global fastType
    fastType = fastOn

def cls():
    #Clears the screen console
    os.system('cls' if os.name=='nt' else 'clear')

def Wait(timeDelay):
    if(not fastType):
        time.sleep(timeDelay)

def GetDialouge(indexNo):
    #Setup Dialogues
    if(indexNo==-1):
        return ["SETUP MODE"] 
    elif(indexNo==-2):
        return ["Please enter a path for SFFPSL"]     
    elif(indexNo==-3):
        return ["Path does not exist."]       
    elif(indexNo==-4):
        return ["Could not verify user identity... "]    
    elif(indexNo==-5):
        return ["Press enter to continue..."]
    
    #Dialouge 1-5 : common outputs  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    elif(indexNo==0):
        return ["-------------------------------------------"]
    elif(indexNo==1):
        return["Program terminated..."]
    elif(indexNo==2):
        return[""]
    elif(indexNo==3):
        return["Session expired."]
    elif(indexNo==4):
        return["Invalid number of arguments, see 'help'",""]
    elif(indexNo==5):
        return["Invalid command, not found. See 'help'",""]
        
    #Dialouge 6-15 : main outputs  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    elif(indexNo==6):
        return ["Welcome"]
    elif(indexNo==7):
        return ["Are you sure? (Y/N)"]   
    elif(indexNo==8):
        return ["Invalid command"]
    elif(indexNo==9):
        return ["Invalid arguments"]
    elif(indexNo==10):
        return ["Displaying configuration settings:"]
    elif(indexNo==11):
        return ["Setting changed"]
    elif(indexNo==12):
        return ["Invalid setting"]
    elif(indexNo==13):
        return ["WARNING: Backup path invalid, switching to default"]
    elif(indexNo==14):
        return ["Procedure aborted."]     
        
    #Dialouge 16-25 : account outputs <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    elif(indexNo==16):
        return["No account found, directing to account setup...", "Input your desired username: (or type 'exit' to cancel)"]
    elif(indexNo==17):
        return["Account creation was successful"]
    elif(indexNo==18):
        return["Something went wrong, account creation failed"]
    elif(indexNo==20):
        return ["Log in to continue.", "Please enter your username"]
    elif(indexNo==21):
        return ["Password:"]
    elif(indexNo==22):
        return ["Re-enter Password:"]
    elif(indexNo==23):
        return ["Passwords must match!"]
    elif(indexNo==24):
        return ["Incorrect credentials, try again (or type 'exit' to cancel)"]
    elif(indexNo==25):
        return ["Welcome, you have successfully logged in to your password locker"]
        
    #Dialouge 26-35 : Primary locker outputs <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    elif(indexNo==26):
        return ["Please enter your command:"]
    elif(indexNo==27):
        return ["Here are the available commands"]
    elif(indexNo==28):
        return ["Command aliases are:"]
    elif(indexNo==29):
        return ["No available aliases."]
    elif(indexNo==30):
        return ["Command parameters are:"]
    elif(indexNo==31):
        return ["No parameters required."]
    elif(indexNo==32):
        return ["Command not found, use 'help' to view available commands"]  
        
    #Dialouge 33-40 : Command locker outputs <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    elif(indexNo==33):
        return ["Your stored groups are:"]    
    elif(indexNo==34):
        return ["Your stored passwords are:"]
    elif(indexNo==35):
        return ["You have no stored passwords."]
    elif(indexNo==36):
        return ["Invalid page number"]    
        
    #'Create' Dialouges
    elif(indexNo==38):
        return ["Successfully added password"]
    elif(indexNo==39):
        return ["Failed to add password."]
    elif(indexNo==40):
        return ["Error, password already exists."]
    elif(indexNo==41):
        return ["Successfully edited password"]
    elif(indexNo==42):
        return ["Failed to edit password"]
    elif(indexNo==43):
        return ["Error, password does not exist"]
    elif(indexNo==45):
        return ["Successfully deleted password"]
    elif(indexNo==46):
        return ["Failed to delete the password"]
    elif(indexNo==47):
        return ["Successfully found password, displaying..."]
    elif(indexNo==48):
        return ["Your generated password is:"]
    elif(indexNo==49):
        return ["Would you like to generate a new password? (Y/N)"]
    elif(indexNo==50):
        return ["Save this to your locker? (Y/N)"]    
    elif(indexNo==51):
        return ["Enter a title for you password ('c' to cancel)"]    
           
    elif(indexNo==52):
        return ["Possible password parameters are as follows:"]
    elif(indexNo==60):
        return ["Do you wish to backup or restore files?"]
    elif(indexNo==61):
        return ["Invalid option, try again."]
    elif(indexNo==62):
        return ["Specify a backup location"]
    elif(indexNo==63):
        return ["Do you wish to use this path? (Y/N)"]
    elif(indexNo==64):
        return ["Are you sure you wish to restore? (Y/N) This will overrite the active directory."]
    elif(indexNo==65):
        return ["Backup successful."]
    elif(indexNo==66):
        return ["Restore successful."]
    elif(indexNo==67):
        return ["Something went wrong, attempt unsuccessful"]
    elif(indexNo==68):
        return ["The following files failed to copy:"]
        
    #Config help
    elif(indexNo==80):
        return["-config help"]
    elif(indexNo==81):
        return["Configuration help","---------------------------","-config view                               : shows current configuration options", "-config edit <setting name> <setting value>: Update setting"]
      
#Writes the string out (letter by letter)
def out(indexNo, delay=0.02, prefix = ""):    
    for vals in GetDialouge(indexNo):     
        if(indexNo ==0):
            SlowPrint(vals,0.01, prefix)
        else:
            SlowPrint(vals,delay, prefix)  
        time.sleep(delay * 10)
    
def outs(indexNos, delay=0.02, prefix = ""):
    for nos in indexNos:
        out(nos, delay, prefix)
        if(not fastType):
            time.sleep(delay)
        
def SlowPrint(str, printDelay, prefix = ""):
    if(str==""):
        prefix = ""
    if(fastType):
        printDelay = 0        
    str = prefix + str
    counter = 0
    for c in str:        
        print(c, end='', flush=True)
        if(c!= " " and counter < 100):
            counter += 1
            time.sleep(printDelay)        
    print("")

def SlowPrintArray(strs, printDelay , prefix = ""):
    for str in strs:
        SlowPrint(str, printDelay, prefix)

def PrintList(mixedList, printDelay, prefix = "", ignorePrefixAt = []): 
    runVal = 0
    for val in mixedList:    
        if runVal in ignorePrefixAt:
            prefix = ""
        #First check if number or string
        if(isinstance(val, int)):
            #print(str(val) + " is number")            
            out(val,printDelay)
        elif(isinstance(val,str)):            
            #print(val + " is string")
            SlowPrint(val, printDelay, prefix)
        elif(isinstance(val, list)):
            PrintList(val, printDelay, prefix)
        runVal +=1