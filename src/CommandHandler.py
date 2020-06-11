#This is the command handler for Pass Locker 
#---------------------------------------------
#Author: Adam Thornes
#OS: Rasperian
#Date: 07/01/2019
#File Version: v3.1.4
#---------------------------------------------

import DisplayHandler as console
import Encryptor as enc
import FileHandler as File
import CommandInfo
import time, math


#List of available commands
def GetCommandList():
    #Holds all commands and information to be passed to its class
    commandList = []
    commandList.append(["Help", ["<{commandName}>"], "Returns list of commands, also try 'Help <commandName>'", None, "Commands are not case sensitive, however parameters may be"])
    commandList.append(["ShowPasswords", ["<{search_group}>", "<{page_number}>"], "Displays list of stored passwords", ["List", "Passwords", "PassList"], None])
    commandList.append(["ViewGroups", ["<{page_number}>"], "Displays saved groups", ["Groups", "ShowGroups"], None])
    commandList.append(["AddPass", ["<title>", "<password>", "<{username}>","<{additional_info}>", "<{group}>" ], "Add a password to the locker", ["Add","NewPass", "NewPassword", "AddPassword"], "Use GenPass to create a password for you. Optionally, include a username. Sidenote: passwords cannot contain spaces"])
    commandList.append(["EditPass", ["<title>","<password>", "<{username}>", "<{additional_info}>", "<{group}>" ], "Overrite a password", ["Edit", "Overrite", "Change"], "Can also use 'edit <passTitle> {pass=<newpass>} {user=<newuser>} {group=<newgroup>} -> group=null removes group from pass"])
    commandList.append(["EditTitle", ["<current_title>","<new_title>" ], "Change the title of a saved password", ["NewTitle", "Rename"], None])
    commandList.append(["GetPass", ["<password_name>"], "Display the given password", ["ShowPass", "ViewPass", "Password", "Show", "View"], "Screen clears on next command"])
    commandList.append(["DelPass", ["<password_name>"], "Delete the given password, WARNING: irrevocable", ["Delete"], None])
    commandList.append(["GenPass", ["<{requirements}>"], "Generate a random password", ["Create", "Generate"], "Use 'requirements' to view how to specify your generated password"])
    commandList.append(["Requirements", [], "Displays information on the GenPass command", None, "Informs how to use requirements for the GenPass command"])
    commandList.append(["Backup", ["<{backup(view help)}>", "<{filelocation}>"], "Backup data files to extenal path", None, "<backup> = 'backup' to save to file, 'restore' to restore from file (WARNING overrites active directory) Specify specific filelocation or use config path."])
    return commandList
    

class CommandHandler:
    def __init__(self, user, passw):
        salt = enc.GenerateSALT()
        self.sessionSALT = salt
        self.user = enc.AESEncrypt(user, salt)
        self.passw = enc.AESEncrypt(passw, salt)
        self.toClear = False
        
        #Define all commands, add to self
        commandList = []
        for cmds in GetCommandList():            
            commandList.append(CommandInfo.Command(cmds[0], getattr(self, cmds[0]), cmds[1], cmds[2], cmds[3], cmds[4]))
        self.commandList = commandList
        
    def Run(self, command):
        self.WillClear() # Clears the console screen if neccessary
        cmd = command.split()
        leadCmd = cmd[0].lower()
        cmdParams = []
        #Now check with commands and their aliases
        foundCommand = CommandInfo.GetCommandFromTitle(leadCmd, self.commandList, True)
        if(foundCommand != None):
            cmdParams = self.GetParameters(cmd, foundCommand.Parameters())
            if(cmdParams == None):
                console.out(4)
            else:
                foundCommand.Run(cmdParams)
        elif(command == "devfillpass"):
            #TEMP - development command ONLY            
            for i in range(0,34):
                self.AddPass(["test" + str(i),"pass" + str(i), "user" + str(i)])
            console.SlowPrint("Added dev passwords", 0.02)
        else:
            console.outs([32,0])
          
                
    def GetParameters(self, userCommand, storedParams):
        #print(storedParams)
        userCommand.pop(0) # Remove original command (not a parameter)        
        #Check if correct number of parameters have been passed, return None if insufficient parameters (will ignore extra params)
        cmdParams = len(storedParams) #Number of parameters available
        requiredParams = 0
        for storedParam in storedParams:
            if "{" not in storedParam : # parameters with {, denote optional parameters
                requiredParams += 1
        if(len(userCommand) < requiredParams):
            return None
        else:
            return userCommand
        
    def WillClear(self):
        if(self.toClear): #Clear the screen if a password was shown recently
            console.cls()            
            self.toClear = False; #Reset parameter as password is no longer on screen
            
    def GetFileEncryptionKey(self):
        return enc.AESDecrypt(self.passw, self.sessionSALT)
            
    #|||||||||| ---------------------- STORED COMMAND PROCEDURES -------------------------------------- ||||||||    
    
    def Help(self, params):
        if(len(params) == 0):            
            console.outs([0,27], 0.02)
            for command in self.commandList:
                toPrint = command.Title() + " "
                for params in command.Parameters():
                    toPrint += params + " "
                toPrint += ": " + command.Description()
                console.SlowPrint(toPrint, 0.007, ">")
            console.outs([0,2])
        elif(len(params) == 1):
            # Show command help for specific command (returns the additional text)
            foundCommand = CommandInfo.GetCommandFromTitle(params[0],self.commandList, True)
            if(foundCommand != None):            
                toPrint = foundCommand.Description()
                if(foundCommand.Additional() != None):
                    toPrint += " : " + foundCommand.Additional()
                foundAliases = foundCommand.Aliases()
                arrayToPrint = [0,toPrint]
                if(len(foundAliases)==0):
                    arrayToPrint.append(29)
                else:
                    arrayToPrint.extend([28,foundAliases])
                foundParams = foundCommand.Parameters()
                if(len(foundParams)==0):
                    arrayToPrint.extend([31,0,2])
                else:
                    arrayToPrint.extend([30,foundParams,0,2])
                console.PrintList(arrayToPrint, 0.02, ">")     
                         
            else:
                console.out(5)
                
    def ShowPasswords(self, params):
        checkItem = 0        
        searchGroup = "NULL"
        if(len(params) > 0 and not str.isdigit(params[0])):
            searchGroup = params[0]    
            checkItem = 1
            
        titleList = File.GetPasswordTitles(self.GetFileEncryptionKey(), searchGroup)   
        
        if(titleList != None and len(titleList) != 0):
            pageNumber = 1
            pages = math.ceil(len(titleList) / 10)
            #Split titlelist into groups of 10, call by page number (must be int)
            if(len(params) > checkItem and str.isdigit(params[checkItem])):                
                pageNumber = int(params[checkItem])
            if(pageNumber > pages):
                console.outs([36,2])    
            else:
                #Get (up to) 10 results from the requested page
                firstIndex = (pageNumber - 1) * 10
                lastIndex = pageNumber * 10
                if(lastIndex > len(titleList)):
                    showPass = titleList[firstIndex:]
                else:
                    showPass = titleList[firstIndex:lastIndex]
                page = "Viewing page " + str(pageNumber) + " out of " + str(pages) + "."
                displayMessage = 34
                if(searchGroup != "NULL"):
                    displayMessage = "The group '" + searchGroup + "' contains the following:"
                console.PrintList([0, displayMessage, showPass, 2, page,0,2],0.02, ">", [4])            
        else:
            if(searchGroup == "NULL"):
                console.outs([2,35,0,2])
            else:
                console.PrintList([2,"No stored passwords found in the '" + searchGroup + "' group.",0,2], 0.02)
        
    def ViewGroups(self, params):
        #Show and return groups available
        groups = File.GetPasswordGroups(self.GetFileEncryptionKey())
        console.PrintList([0,33, groups, 2, 0], 0.02, ">", [4])        
        
    def AddPass(self, params):
        #Check if password title is already taken
        userTitle = params[0]

        passTitles = File.GetPasswordTitles(self.GetFileEncryptionKey())
        if(passTitles == None or userTitle.lower() not in (name.lower() for name in passTitles)): #Prevent passwords under the same name
            #password doesn't exist, can create
            if(len(params)==3):
                state = File.AmmendPasswordFile(params[0], params[1], self.GetFileEncryptionKey(), params[2])
            elif(len(params)==4):
                state = File.AmmendPasswordFile(params[0], params[1], self.GetFileEncryptionKey(), params[2], params[3])
            elif(len(params)==5):
                state = File.AmmendPasswordFile(params[0], params[1], self.GetFileEncryptionKey(), params[2], params[3], params[4])
            else:
                state = File.AmmendPasswordFile(params[0], params[1], self.GetFileEncryptionKey())
            if(state):
                console.out(38)
            else:
                console.out(39)
        else:
            #password with title already exists
            console.out(40)      
        self.toClear = True
        
    def EditPass(self, params): 
        #Similar to add pass, but overrites existing password
        userTitle = params[0]
        foundIndex = File.GetPasswordTitle(userTitle, self.GetFileEncryptionKey())
        if(foundIndex >= 0):        
            #password exists, therefore can overrite
            #First check if user used identifiers i.e. 'EditPass passwordTitle group=NewGroup'
            if(len(params) > 1 and '=' in params[1]):
                passw = ""
                usern = ""
                group = ""
                extra = ""
                #Does contain identifier
                for param in params:
                    #Need to check for all parameters
                    if("=" in param):
                        #Only consider value with = in parameter passed
                        splitParam = param.split("=")
                        if(splitParam[0].lower() == "pass" or splitParam[0].lower() == "passw" or splitParam[0].lower() == "password"):
                            passw = splitParam[1]
                        elif(splitParam[0].lower() == "user"):
                            usern = splitParam[1]
                        elif(splitParam[0].lower() == "group" or splitParam[0].lower() == "grp"):
                            group = splitParam[1]
                        elif(splitParam[0].lower() == "extra" or splitParam[0].lower() == "ext" or splitParam[0].lower() == "additional" or splitParam[0].lower() == "add"):
                            extra = splitParam[1]
                if(passw != "" or usern != "" or group != "" or extra != ""):
                    #Update file                    
                    state = File.AmmendPasswordFile(params[0], passw, self.GetFileEncryptionKey(), usern, extra, group, foundIndex)
                else:
                    state = False
            else:   
                if(len(params)==3):
                    state = File.AmmendPasswordFile(params[0], params[1], self.GetFileEncryptionKey(), params[2], "null","null", foundIndex)
                elif(len(params)==4):
                    state = File.AmmendPasswordFile(params[0], params[1], self.GetFileEncryptionKey(), params[2], params[3],"null", foundIndex)
                elif(len(params)==5):
                    state = File.AmmendPasswordFile(params[0], params[1], self.GetFileEncryptionKey(), params[2], params[3],params[4], foundIndex)    
                elif(len(params)==2):
                    state = File.AmmendPasswordFile(params[0], params[1], self.GetFileEncryptionKey(), "null", "null","null", foundIndex)            
            if(state):
                console.out(41)
            else:
                console.out(42)
        else:
            #password doesn't exist
            console.outs([43,2])  
    
    def EditTitle(self, params):
        oldTitle = params[0]
        newTitle = params[1]
        indexOfTitle = File.GetPasswordTitle(oldTitle, self.GetFileEncryptionKey())
        state = File.RenamePassTitle(newTitle, indexOfTitle, self.GetFileEncryptionKey())
        if(state):
            console.out(41)
        else:
            console.out(42)
        
    def GetPass(self, params):
        #Get the password from titleName
        titleIndex = File.GetPasswordTitle(params[0], self.GetFileEncryptionKey())
        if(titleIndex >= 0):
            console.out(47)
            console.Wait(0.1)
            console.PrintList(File.GetPassFromFile(titleIndex, self.GetFileEncryptionKey()), 0.03, ">")
            console.out(2)
            self.toClear = True
        else:
            console.outs([43,2])  
     
    def DelPass(self, params):
        console.out(7)
        confirm = input("") #Double check user wishes to delete password
        if(confirm == "Y" or confirm == "y"): 
            #First check if password exists
            userTitle = params[0]
            foundIndex = File.GetPasswordTitle(userTitle, self.GetFileEncryptionKey())
            if(foundIndex >= 0):
                #password exists, therefore can overrite
                state = File.DeletePassword(foundIndex, self.GetFileEncryptionKey())
                if(state):
                    console.out(45)
                else:
                    console.out(46)
            else:
                #password doesn't exist
                console.outs([43,2])
     
    def GenPass(self, params):
        wait = True
        #Generate password
        while(wait):
            generatedPassword = enc.GeneratePassword(params)
            console.out(48)
            console.SlowPrint(generatedPassword, 0.03, ">")
            console.out(49)
            inputVal = input("")
            if(inputVal.lower()=="n" or inputVal.lower()=="no"):
                wait = False
        #Give option to save password
        
        console.out(50)
        inputVal = input("")
        if(inputVal.lower()=="y" or inputVal.lower()=="yes"):
            titleSelected = False
            passTitles = File.GetPasswordTitles(self.GetFileEncryptionKey())
            while(not titleSelected):
                console.out(51) #Get user to enter a title
                inputVal = input("")
                if(inputVal.lower() == "c"):
                    return None #Quit routine
                if(passTitles == None or inputVal not in passTitles):
                    titleSelected = True            
            
            state = File.AmmendPasswordFile(inputVal, generatedPassword, self.GetFileEncryptionKey())
            if(state):
                console.PrintList([38, "Use 'EditPass' to add more information to this stored password"], 0.02)
            else:
                console.out(39)    
            
        console.out(2)
    
    def Requirements(self, params):
        console.out(0)
        possibleRequirements=[
        "len=20, define length of password",
        "num=False, should the password contain numbers", 
        "spec=True, should the password contain special characters",
        "upp=False, should the password contain uppercase characters?",
        "low=False, should the password contain lowercase characters?"]
        console.out(52)
        console.PrintList(possibleRequirements,0.02,">")        
        #console.SlowPrint("Use 'help requirements'",0.03)  
        console.outs([0,2])   

    def Backup(self, params):
        #Backup/Restore encrypted files to new path
        newPath = File.GetBackupPath()
        #Now verify backup or restore option

    def Backup(self, params):
        #Backup/Restore encrypted files to new path
        
        #Determine if backup or restore requested
        backup = IsRequestBackup(params)
        if(backup == None):
            console.out(61)
            return None
        
        #Now need to determine file location
        backupPath = DetermineBackupPath(params)
        if(backupPath == None): #Check if user aborted backup
            return None
            
        #Backup files
        if(backup):
            returnList = File.PerformBackup(backupPath)
            if(len(returnList) == 0):
                console.out(65)            
        else:
            returnList = File.PerformRestore(backupPath)
            if(len(returnList) == 0):
                console.out(66)
        if(len(returnList) > 0 and returnList[0] != "FAIL"):
            console.outs([67,68])
            for failedCopy in returnList:
                failedCopy = failedCopy.replace("\\", "/") #Clean up file path string
                console.SlowPrint(failedCopy, 0.02, ">")
        console.out(2)
            
def IsRequestBackup(params):
    if(len(params)<=0):
        requestString = None
    else:
        requestString = params[0]
        
    if(requestString == None):
        #ask user for option
        console.out(60)
        requestString = input("") 
    backup = requestString
    if(backup.lower() == "backup" or backup.lower() == "back" or backup.lower() == "b"):
        #Backup file
        return True
    elif(backup.lower() == "restore" or backup.lower() == "rest" or backup.lower() == "r"):
        #Restore file
        #Double check user wishes to restore
        console.out(64)
        check = input("")
        if(check.lower()=="y" or check.lower()=="yes"):
            return False
        else:
            console.out(14)
            return None
        return False
    else:
        return None

def DetermineBackupPath(params):   
    configPath = File.GetBackupPath()     
    #First determine if user has provided input
    if(len(params) >= 2):
        #user did provide input
        return params[1]
    else:
        #Not input, take from file
        if(configPath != ""):
            #Config file contains address, confirm from user
            console.PrintList(["Backup path="+configPath,63],0.02)
            response = input("")
            if(response.lower() == "y" or response.lower() == "yes"):
                return configPath
            elif(response.lower() == "n" or response.lower() == "no"):
                pass
            elif(response.lower() == "exit"):
                return None
        #Get input from user for backup path
        isValidPath = False
        while(not isValidPath):
            console.out(62)
            userInput = input("")
            if(File.DoesFolderExist(userInput)):
                return userInput
            elif(userInput.lower() == "exit"):
                return None
            else:
                console.out(-3)
                
