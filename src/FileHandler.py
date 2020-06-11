#This is the file handler for Pass Locker 
#---------------------------------------------
#Author: Adam Thornes
#OS: Rasperian
#Date: 07/01/2019
#File Version: v3.3.2
#---------------------------------------------

import sys, os, string

import Encryptor #Handles all encryption algorithms and checking
import DisplayHandler as console
from shutil import copy2
seperator = "<$*\"g>" 
sep2 = "%2hb&1"
userpassSep = "~83*£0"
#Filepaths (default) ---
winPath = "C:/Users/ad199/Documents/Programming/Python/PassLocker/PyLocker/datafiles"
piPath = "/home/pi/passlocker"
backupPath = ""
securityPath = "E:/PSLKS"
workingPath = os.getcwd()
backupFolder = "/set"
#Filenames --------------------
exSecFile = "/SFFPSL.psl"   #Note - this file will NOT be backed up
settingsFile = "/settings.psl"
accountFile = "/user.psl"
securityFile = "/activesession.psl"
passFile = "/locker.psl"
testFile = "/affirmation.psl"
# -----------------------------

def UpdateFilePath(newPath):
    #Select the correct path based on OS
    if sys.platform == "win32": 
        global winPath
        winPath = newPath
    else:
        global piPath
        piPath = newPath
        
def UpdateSecurityPath(newPath):
    #Select the correct path based on OS
    global securityPath
    securityPath = newPath    

def UpdateBackupPath(newPath):
    #Select the correct path based on OS
    global backupPath
    backupPath = newPath        
    
def GetBackupPath():
    #Select the correct path based on OS
    global backupPath
    return backupPath     
    
def SplitString(toSplit, strSep):   
    #Performs a string split (since python's str split() didn't want to work)
    sepLength = len(strSep)
    holdString = "" #Used to hold a temp string while looking for the seperator
    foundLen = 0
    onReturn = 0
    returningTuple = [""]
    for c in toSplit:
        if(c==strSep[foundLen]):
            foundLen +=1
            holdString += c
        else:
            returningTuple[onReturn] += c + holdString
            holdString = ""
            foundLen = 0        
        if(foundLen==sepLength):            
            #Must have found seperator and need to split to next string
            onReturn += 1
            holdString = ""
            foundLen = 0
            returningTuple.append("")        
    return returningTuple

def ReadSettingsFile():
    fullSettingsPath = workingPath + settingsFile
    #First check if settings file exists
    if(DoesProgramFileExist(settingsFile, workingPath)):
        #File does exist, need to read file  
        with open(fullSettingsPath, "r") as setFile:
            contents = setFile.readlines()
        #Now return settings
        return contents     
    else:
        #File does not exist therefore need to create one
        #Since this is the first file function to be called, the directory may need to be made also
        if(not os.path.exists(GetFileLocation())):
            #If the folder is not there, create one
            os.makedirs(GetFileLocation())
        #Now create settings file
        fileContents = [
        "#Settings file, (recommend editing within the program):\n"
        ,"sffpsl=SETUP\n"
        ,"fileloc=" + GetFileLocation() + "\n",
        "quickwrite=False\n",
        "backuppath=DEFAULT\n"]
        #Now save data in file
        setFile = open(fullSettingsPath, "w+")
        for cont in fileContents:
            setFile.write(cont)
        setFile.close()
        return fileContents #Return default settings

def UpdateSettingsFile(setting, newVal):  
    setting = setting.lower() #Setting are stored in lowercase    
    storedSettings = ReadSettingsFile()
    
    newSettings = []
    foundSetting = False
    for i in range(0,len(storedSettings)):       
        splitSetting = storedSettings[i].split("=")
        if(setting == splitSetting[0]):     
            newVal = newVal.replace("\\", "/")
            newSettings.append(setting+"="+newVal)
            foundSetting = True
        else:
            newSettings.append(storedSettings[i][:-1])
            
    if(foundSetting):
        #Now write it back to file
        setFile = open(workingPath + settingsFile, "w+")
        for cont in newSettings:
            setFile.write(cont + "\n")
        setFile.close()
        return True
    else:
        return False

def CreateSFFPSL(FilePath):
    global securityPath
    securityPath = FilePath
    
    newKey = Encryptor.GenerateSecurityKey()

    fillKey = Encryptor.GenerateSALT(64,True)
    toSave = ""
    for idx, val in enumerate(newKey):
        toGrab = 2*idx
        toSave += val + fillKey[toGrab] + fillKey[toGrab + 1]
    
    toSave = Encryptor.AESEncrypt(toSave, sep2)
    
    #Now write to file
    SFFPSLFile = open(securityPath + exSecFile, "w+")    
    SFFPSLFile.write(toSave + "\n")
    SFFPSLFile.close()
    
    UpdateSecurityKey(newKey)
    UpdateSecurityPath(FilePath)
    
def CreateTestFile():   
    if(not DoesProgramFileExist(testFile, workingPath)):
        #If test file doesn't exist, create one
        toWrite = Encryptor.AESEncrypt("PASS", Encryptor.GetKey())
        checkFile = open(workingPath + testFile, "w+")        
        checkFile.write(toWrite + "\n")
        checkFile.close()
        
def CheckTestFile():
    if(not DoesProgramFileExist(testFile, workingPath)):
        #file doesn't exist, cannot perform check
        return False
    else:
        with open(workingPath + testFile) as f:
            checkFound = f.readline()
        passCheck = Encryptor.AESDecrypt(checkFound, Encryptor.GetKey())
        if(passCheck == "PASS"):
            return True
    return False
    
def ReadSFFPSL(): 
    try:
        if(not DoesProgramFileExist(exSecFile, securityPath)):
            return False    
        with open(securityPath + exSecFile) as f:
            keyFound = f.readline()
        keyFound = Encryptor.AESDecrypt(keyFound, sep2)
        extractKey = ""
        for i in range(len(keyFound)):
            if(i % 3 == 0):
                extractKey += keyFound[i]
        
        UpdateSecurityKey(extractKey)
        return True
    except:
        return False
        
def UpdateSecurityKey(key):    
    Encryptor.UpdateSecurityKey(key)
        
def GetFileLocation():
    #Get the file location for storing data
    if sys.platform == "win32": 
        return winPath
    else:
        return piPath
        
def DoesProgramFileExist(path, fileLoc=GetFileLocation()):
    #Check if program file exists in the directory, returns true or false    
    checkFile = fileLoc + path    
    exists = os.path.isfile(checkFile)    
    if(exists):
        return True
    else:
        return False
        
def DoesFolderExist(path):
    if(os.path.exists(path)):
        return True
    else:
        return False

def DoesAccountExist():
    #Check if there is an account set up for the password locker    
    return DoesProgramFileExist(accountFile)
    
def CreateUserAccount(username, encryptedPass, salt):
    #Account does not already exist, therefore need to create account
    accountString = salt + seperator + encryptedPass + seperator + username
    #Must encrypt data via AES using unique identifying password (It's actually just the username - Doesn't need to be overly secure)
    encAccString = Encryptor.AESEncrypt(accountString, username)
    
    #Now save data in file
    accFile = open((GetFileLocation() + accountFile), "w+")
    accFile.write(encAccString)
    accFile.close()
    
def GetUserAccount(passKey):
    accFile = open((GetFileLocation() + accountFile), "r")
    if(accFile.mode == 'r'):
        encAccString = accFile.read()
        toReturn = ""        
        try:
            #Decrypt file and split based on seperator
            accountString = Encryptor.AESDecrypt(encAccString, passKey)   
            accFile.close()
            return SplitString(accountString, seperator)              
        except:
            #Failed to decrypt            
            pass
        accFile.close()
        return None
    accFile.close()
    return None
    
def CreateSecurityFile(EncrpytedPassKey, AESKey):
    if(DoesProgramFileExist(securityFile)):
        os.remove(GetFileLocation() + securityFile) #Old file is useless, remove it if it exists
    #Now build file contents
    fileContents=["#Active Session, DO NOT EDIT", Encryptor.AESEncrypt("Security_Session_Key", Encryptor.GenerateSALT())]
    encKey = Encryptor.AESEncrypt(EncrpytedPassKey, AESKey) #Again, doesn't need to be overly secure
    fileContents.append(encKey)
    
    sessionFile = open((GetFileLocation() + securityFile), "w+")
    for x in fileContents:
        sessionFile.write(x + "\n")
    sessionFile.close()    

def ReadSecurityFile(AESKey):
    if(not DoesProgramFileExist(securityFile)):
        return None #This should never happen (only with tampering)
    try:    
        with open((GetFileLocation() + securityFile), "r") as f:
            lines = f.readlines()
        return Encryptor.AESDecrypt(lines[2], AESKey)
    except:
        return None
        
def AmmendPasswordFile(passTitle, password, encryptionKey, inputUsername="null", inputExtra="null", inputGroup="null", lineNum = -1): 
    AESEncryptionKey = Encryptor.BindKey(Encryptor.GetKey(), encryptionKey)
    #Returns successful runs, 
    if(not DoesProgramFileExist(passFile)):
        #Will create the file if it doesn't exist
        toWrite = ["#Locker.psl"]
        encryptedLineWrite = Encryptor.EncryptFile(toWrite, AESEncryptionKey)
        with open((GetFileLocation() + passFile), "w+") as pF:
            pF.write(encryptedLineWrite) 
            
    #Get Current File
    with open((GetFileLocation() + passFile), "r") as f:
        data = f.readline()
    fileContent = Encryptor.DecryptFile(data, AESEncryptionKey)
                
    #lineNum = -1 denotes a new password to be added
    if(lineNum >= 0 and lineNum < len(fileContent) and (password == "" or inputUsername == "" or inputGroup == "" or inputExtra == "")):        
        #Check what values = '' and overrite with stored data        
        #First seperate fileContent by sep2
        sep2Content = SplitString(fileContent[lineNum],sep2)
        #Now update group values
        if(inputGroup == ""):
            inputGroup = sep2Content[0]
        #Now get user/pass segment
        userPassSeg = Encryptor.AESDecrypt(sep2Content[2], AESEncryptionKey).split(userpassSep)        
        if(password == ""):
            password = userPassSeg[0]        
        if(inputUsername == ""):                        
            inputUsername = userPassSeg[1]     
        if(inputExtra == ""):
            inputExtra = userPassSeg[2]
            print(inputExtra)
      
    lineWrite = inputGroup + sep2 + Encryptor.AESEncrypt(passTitle, AESEncryptionKey) + sep2 + Encryptor.AESEncrypt(password + userpassSep + inputUsername + userpassSep + inputExtra, AESEncryptionKey) 
    
    #Ammend file contents
    if(lineNum == -1):
        fileContent.append(lineWrite)
    elif(lineNum >= 0):
        if(lineNum > len(fileContent)):
            return False
        fileContent[lineNum] = lineWrite    
    else:
        raise ValueError("Invalid edit number, use '-1' to add new password")
    
    #Write back to file
    writeFileString = Encryptor.EncryptFile(fileContent, AESEncryptionKey)
    with open((GetFileLocation() + passFile), "w") as f:  
        f.write(writeFileString)
    
    return True
    
def RenamePassTitle(newPassTitle, lineNum, encryptionKey):
    AESEncryptionKey = Encryptor.BindKey(Encryptor.GetKey(), encryptionKey)
    if(not DoesProgramFileExist(passFile)):
        return False
        
    #Get Current File
    with open((GetFileLocation() + passFile), "r") as f:
        data = f.readline()
    fileContent = Encryptor.DecryptFile(data, AESEncryptionKey)
    
    if(lineNum < 0 or lineNum >= len(fileContent)):
        return False
    
    #Get password locker line
    fullLine = SplitString(fileContent[lineNum],sep2)
    
    lineToWrite = fullLine[0] + sep2 + Encryptor.AESEncrypt(newPassTitle, AESEncryptionKey) + sep2 + fullLine[2]
    
    #Write back to file
    fileContent[lineNum] = lineToWrite  
    
    writeFileString = Encryptor.EncryptFile(fileContent, AESEncryptionKey)    
    with open((GetFileLocation() + passFile), "w") as f:  
        f.write(writeFileString)
    
    return True
        
def GetPassFromFile(index, encryptionKey):
    AESEncryptionKey = Encryptor.BindKey(Encryptor.GetKey(), encryptionKey)
    if(not DoesProgramFileExist(passFile)):
        return None    
    with open((GetFileLocation() + passFile), "r") as f:
        dataSet = f.readline()    
    #Decrypt file
    data = Encryptor.DecryptFile(dataSet, AESEncryptionKey)
    
    sepData = SplitString(data[index],sep2)
    
    foundPass = Encryptor.AESDecrypt(sepData[2],AESEncryptionKey)
    splitData = foundPass.split(userpassSep)
    
    toReturn = []
    if(splitData[1].lower() != "null"):
        toReturn.append("USER: " + splitData[1])        
    toReturn.append("PASS: " + splitData[0])
    if(splitData[2].lower() != "null"):
        toReturn.append("Additional: " + splitData[2])
    #Add group to return
    if(sepData[0].lower() != "null"):
        toReturn.append("")
        toReturn.append("In group: " + sepData[0])
    return toReturn
        
def GetPasswordTitles(encryptionKey, byGroup="NULL"):
    AESEncryptionKey = Encryptor.BindKey(Encryptor.GetKey(), encryptionKey)
    if(not DoesProgramFileExist(passFile)):
        return None
    with open((GetFileLocation() + passFile), "r") as f:
        encDataSet = f.readline()
    titles = []     
    dataSet = Encryptor.DecryptFile(encDataSet, AESEncryptionKey)
    for data in dataSet:
        if(data != "" and data[0] != "#"):
            splitData = SplitString(data,sep2)
            title = splitData[1]
            if(byGroup != "NULL"):
                if(splitData[0].lower() == byGroup.lower()):
                    titles.append(Encryptor.AESDecrypt(title,AESEncryptionKey))
            else: 
                titles.append(Encryptor.AESDecrypt(title,AESEncryptionKey))
    return titles
    
def GetPasswordTitle(searchTerm, encryptionKey):
    AESEncryptionKey = Encryptor.BindKey(Encryptor.GetKey(), encryptionKey)
    if(not DoesProgramFileExist(passFile)):
        return None
    with open((GetFileLocation() + passFile), "r") as f:
        encDataSet = f.readline()
    dataSet = Encryptor.DecryptFile(encDataSet, AESEncryptionKey)   
    for idx, data in enumerate(dataSet):
        if(data != "" and data[0] != "#"):
            title = SplitString(data, sep2)[1]
            foundTitle = Encryptor.AESDecrypt(title,AESEncryptionKey).lower()            
            if(searchTerm.lower() == foundTitle):
                return idx            
    return -1
    
def GetPasswordGroups(encryptionKey):
    AESEncryptionKey = Encryptor.BindKey(Encryptor.GetKey(), encryptionKey)
    if(not DoesProgramFileExist(passFile)):
        return None    
    with open((GetFileLocation() + passFile), "r") as f:
        dataSet = f.readline()    
    #Decrypt file
    data = Encryptor.DecryptFile(dataSet, AESEncryptionKey)
    groups= []
    for i in range(0,len(data)):
        foundGroup = SplitString(data[i],sep2)[0]
        if(foundGroup[0] != "#" and foundGroup.lower() != "null"):
            groups.append(foundGroup)
    return groups    
    
    
def DeletePassword(passIndex, encryptionKey):
    AESEncryptionKey = Encryptor.BindKey(Encryptor.GetKey(), encryptionKey)
    #Read all from file
    if(not DoesProgramFileExist(passFile)):
        return None
    with open((GetFileLocation() + passFile), "r") as f:
        encDataSet = f.readline()
    data = Encryptor.DecryptFile(encDataSet, AESEncryptionKey)
    #Remove unwanted password
    del data[passIndex]
    try:
    #Re-write file 
        encDataSet = Encryptor.EncryptFile(data, AESEncryptionKey)
        with open((GetFileLocation() + passFile), "w") as f:            
            f.write(encDataSet)
        return True
    except:
        return False
        
def PerformBackup(fileLocation):
    #Backup all files (copy settings and test file to sub-folder and provide README.txt)
    if(not DoesFolderExist(fileLocation)): #Ensure folder exists (should never occur)
        raise ValueError("Invalid file location")
    try:
        secondaryFolder = fileLocation + backupFolder 
        #Create secondary folder
        if(not os.path.exists(secondaryFolder)):            
            os.makedirs(secondaryFolder)
        
        toCopy = [
        [GetFileLocation(),accountFile,fileLocation],
        [GetFileLocation(),passFile,fileLocation],
        [workingPath,settingsFile,secondaryFolder],
        [workingPath,testFile,secondaryFolder]
        ]
        failed=[] #Keep track of any files that failed to copy
        readmeFailedText = "the following failes failed to copy: "
        for copyArray in toCopy:
            val = CopyFile(copyArray[0],copyArray[1],copyArray[2])
            if(val != ""):
                failed.append(val)
                readmeFailedText += "\n'" + val + "' "
        
        #Now provide readme file
        readmeText = ["Backup succesful, all files have been copied", "\nDo not edit files, nor rename them. This will cause the restore function to fail", "", "Find settings and affirmation files in the set subfolder" ]
        if(readmeFailedText != ""):
            readmeText[0] = "Backup successful, however " + readmeFailedText
        
        with open((fileLocation + "/readme.txt"), "w") as f:       
            for readText in readmeText:
                f.write(readText + "\n")
        return failed        
    except Exception:
        raise
        return ["ERROR"]  
        
def PerformRestore(fileLocation):
    #Restore all files from backup location (NOTE - will overrite current files)
    if(not DoesFolderExist(fileLocation)): #Ensure folder exists (should never occur)
        raise ValueError("Invalid file location")    
    try:
        secondaryFolder = fileLocation + backupFolder     
        failed = []
        toCopy = [
        [fileLocation,accountFile,GetFileLocation()],
        [fileLocation,passFile,GetFileLocation()],
        [secondaryFolder,settingsFile,workingPath],
        [secondaryFolder,testFile,workingPath]
        ]
        for copyArray in toCopy:
            val = CopyFile(copyArray[0],copyArray[1],copyArray[2])
            if(val != ""):
                failed.append(val)
        return failed
    except Exception:
        raise
        return ["ERROR"]   
        
def CopyFile(copyDirectory, copyFile, folderDest):
    #First determine if file to copy exists
    if(DoesProgramFileExist(copyFile, copyDirectory)):        
        #File exists therefore can copy
        copy2(copyDirectory + copyFile, folderDest)
        return ""
    return (copyDirectory + copyFile)