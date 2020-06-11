#This is the command info class for Pass Locker 
#---------------------------------------------
#Author: Adam Thornes
#OS: Rasperian
#Date: 07/01/2019
#File Version: v1.0.0
#---------------------------------------------

class Command:
    def __init__(self, title, function, parameters, description, aliases=[], additional=""):
        self.title = title
        self.function = function
        self.parameters = parameters
        self.description = description
        self.aliases = aliases
        self.additional = additional
    
    #Useful commands
    def Run(self, fullCommand):
        self.function(fullCommand)
       
    #Return any command information  
    def Title(self, lowercase = False):
        if(lowercase):
            return self.title.lower()
        return self.title
        
    def Parameters(self):
        return self.parameters
    
    def Description(self):
        return self.description
        
    def Aliases(self):
        if(self.aliases == None):
            return []        
        return self.aliases
    
    def Additional(self):
        return self.additional

def GetCommandFromTitle(Title, CommandList, Alias = False):
    #Check if command is found from title, return command class if true
    #Optional search for alias too
    for command in CommandList:
        if(Title.lower() == command.Title(True)):
            return command
        if(Alias):
            if(CheckCommandForAlias(Title.lower(), command)):
                return command
    return None
    
def CheckCommandForAlias(Alias, Command):
    #Returns true if command matches given alias
    for alias in Command.Aliases():
        if(Alias.lower() == alias.lower()):
            return True
    return False