#This is the main python file for the PassLocker programm see readme
#---------------------------------------------
#Author: Adam Thornes
#OS: Rasperian
#Date: 08/01/2019
#File Version: v2.2.1
#---------------------------------------------

import sys, os, time
import getpass #User can type in their password without showing on screen
import DisplayHandler as console
import Encryptor #Handles all encryption algorithms and checking
import FileHandler #Handles writing/editing files
import CommandHandler as CMD

#Variables stored here ------------|
username = ""
validationKey = ""
securityKey = ""
isInConfirm = False
#----------------------------------|    

    
def EndProgram(clear=True):
    if(clear):
        console.cls()
    console.out(1)
    time.sleep(0.3)
    sys.exit()

def VerifyUser():    
    console.out(20)
    #Get user credentials from input
    user = input("")
    if(not ParseForCommand(user)):
        console.out(21)
        passw = getpass.getpass("")            
        #Check if user credentials are correct
        #First read from file
        fileContents = FileHandler.GetUserAccount(user)    
        
        if(fileContents == None):        
            return [False, "Invalid"]

        filePass = fileContents[1]
        salt = fileContents[0]
        username = user
        return [Encryptor.CheckPass(passw, filePass, salt), passw]
    return [False, "Command"]
   
def CreateAccount():    
    console.out(16,0.03)    
    
    askCommand = True
    while(askCommand):
        newUser = input("")
        newPass = ""   
        if(not ParseForCommand(newUser)):
            askCommand = False
        
    doesMatch = False    
    while(not doesMatch):
        console.out(21)        
        newPass = getpass.getpass("")
        if(not ParseForCommand(newPass)):  #Only run rest of routine if input was not a command     
            console.out(22)        
            check = getpass.getpass("")
            
            if(newPass == check):
                doesMatch = True        
            else:
                console.out(23)
                
    newSalt = Encryptor.GenerateSALT()
    encPass = Encryptor.OneWayEncryptor(newPass, newSalt)
    FileHandler.CreateUserAccount(newUser, encPass, newSalt)
    
def ParseForCommand(userInput):
    if(userInput == "" or userInput == " "):
        return False
    #Check input text for any command (i.e. exit or configuration command)
    if(userInput.lower() == "exit" or userInput.lower() == "-exit"):
        EndProgram()
    elif(userInput[0] == "-"):
        console.out(2)
        #Split command to parts
        partCommand = userInput.split()
        leadCmd = partCommand[0]
        if(leadCmd=="-config"):
            if(len(partCommand) > 1):
                ConfigManager(partCommand)
            else:
                console.outs([9,2])
        #elif(leadCmd=="-key"):
            #Used to manage the external security key for the program (Not currently neccessary)
        #    pass
        else:
            console.outs([8,2])
        console.out(2)
        return True
    return False
        
def ConfigManager(splitCommand):
    updated = False
    cmd = splitCommand[1]
    #Need following commands: view, edit <command> <value>, reset
    if(cmd == "" or cmd == "h" or cmd == "help"):
        console.out(81)
    elif(cmd == "view" or cmd == "v"):
        console.out(10)
        for setting in FileHandler.ReadSettingsFile():            
            if(setting[0] != "#" and setting[0] != " "):
                splitSetting = setting.split("=")            
                toPrint = splitSetting[0] + " = " + splitSetting[1]                
                console.SlowPrint(toPrint[:-1], 0.02, ">")
                updated = False
    elif(cmd == "edit" or cmd == "e"):
        if(len(splitCommand) >= 4): #Needs to be -config edit <setting> <newValue>
            state = FileHandler.UpdateSettingsFile(splitCommand[2], splitCommand[3])
            if(state):
                #setting changed
                console.out(11)
                updated = True
            else:
                #setting not found
                console.out(12)            
    if(updated):
        GetSettings()
    
def PasswordLocker():  
    console.cls()  
    running = True
    console.out(25)
    while(running):             
        console.out(26)
        userInput = input("")
        if(not ParseForCommand(userInput)):            
            #Verify with active session
            if(Encryptor.ValidateSecurityKey(securityKey, FileHandler.ReadSecurityFile(username), validationKey)):            
                Command.Run(userInput)
            else:
                console.out(3)
                running = False
            
def GetSettings():
    #Get settings
    settings = FileHandler.ReadSettingsFile()
    for setting in settings:
        if(setting[0] != "#"):
            splitSetting = setting.split("=")
            settingOption = splitSetting[0]
            settingVal = splitSetting[1][:-1]
            if(settingOption == "sffpsl"):                
                if(settingVal.lower() == "setup"):
                    HandleSetup()
                else:      
                    FileHandler.UpdateSecurityPath(settingVal)
                    VerifySFFPSL()
            elif(settingOption == "fileloc"):
                #Update file location
                FileHandler.UpdateFilePath(settingVal)
            elif(settingOption == "quickwrite"):
                if(settingVal.lower() == "true"):
                    console.OverriteTypeDelay(True)
                else:
                    console.OverriteTypeDelay(False)
            elif(settingOption == "backuppath"):
                if(FileHandler.DoesFolderExist(settingVal)):                    
                    FileHandler.UpdateBackupPath(settingVal)
                elif(settingVal.lower() == "default"):
                    FileHandler.UpdateBackupPath("")                    
                else:
                    console.out(13)
     
def VerifySFFPSL():
    canVerify = False
    global isInConfirm
    
    if(FileHandler.ReadSFFPSL()):
        #Now check contents of file are valid
        if(FileHandler.CheckTestFile()):
            canVerify = True       
            return True
    if(not canVerify and isInConfirm == False):
        isInConfirm = True
        #Coudn't verify/find SFFPSL file
        console.out(-4)
        console.Wait(0.5)
        
        #Now give user option to change file location
        didCommand = True
        while(didCommand):
            console.out(-5)
            inputVal = input("")
            didCommand = ParseForCommand(inputVal) 
        if(not VerifySFFPSL()):
            EndProgram(False)
    return False
def HandleSetup():
    assigned = False
    console.out(-1)
    while(not assigned):
        console.out(-2)
        inputVal = input("")
        inputVal = inputVal.replace("\\", "/")
        if(FileHandler.DoesFolderExist(inputVal)):
            #Create File
            FileHandler.UpdateSettingsFile("sffpsl",inputVal) #Update settings file first
            FileHandler.CreateSFFPSL(inputVal)
            FileHandler.CreateTestFile()
            assigned = True
        else:
            #Folder doesn't exist
            console.outs([-3,0])

#console.cls() #Clear the screen            

#First load settings
GetSettings()

#Verify SFFPSL

console.outs([6,0])
time.sleep(0.3)

#First check if user account exists
fileFound = FileHandler.DoesAccountExist()
if(not fileFound):
    #Create user account since it doesn't exist
    try:
        CreateAccount() 
        console.out(17) #Success, account created
    except Exception:
        console.out(18) #Failure
        raise

#Now get the user to log in to their account
credentialPass = False

validationKey = Encryptor.GenerateSALT()
while(not credentialPass):    
    verification = VerifyUser() 
    if( not verification[0]):
        if(verification[1] == "Invalid"):
            #console.cls()
            console.out(24,0.03)         
    else:
        #Success, user has logged in 
        securityKey = Encryptor.GenerateSecurityKey()        
        FileHandler.CreateSecurityFile(Encryptor.OneWayEncryptor(securityKey,validationKey), username )
        Command = CMD.CommandHandler(username, verification[1])
        credentialPass = verification

        
PasswordLocker()

   
