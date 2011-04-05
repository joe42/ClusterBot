'''
Created on 07.02.2011

@author: joe
'''
from checkbox.variables import kwargs
1. Remove REMOVE Tags                           X
2. Enable passwort via command line.       X
3. Enable Debugging.                                   X
Zeit: 30 Min
1. SVN Checkin                                              
2. Online stellen                                             
3. Reconnect on SSH Timeout                     X
4. ClusterBot auftrennen in CommandBot, ClusterBot und WhitelistingBot
5. Vererbungshierarchie kollabieren
6. Fix command queue                                X
7. Test passwordless login                          X
Zeit: 60 Min
1. opensession auf den standard account beschränken, sonst alle keys nutzbar -
Zeit:19:00..
Zeit:120 Min
1. Dokumentation für den XMLCommandParser erstellen X
2. Dokumentation für den XMLEventParser erstellen X
2. Dokumentation für den ClassBuilder erstellen X
Zeit:60 Min
Zeit:120 Min
Zeit:40 Min
1. XMLParser modularer gestalten und dokumentieren
2. Verschiedene Commands implementieren
3. Command Priorität implementieren
4. Verschiedene Events implementieren
5. Events und Commands per client argumente configurierbar machen:
argumente in eine dict konvertieren und an createInstance übergeben. 
dazu muss lediglich noch ein kommando createevent NAME ALIAS (param=value;)* hinzugefügt werden
6. Commands mit regulären ausdrücken finden
7. Command-queueing ermöglichen um mehrere commandos hintereinander auszuführen  
8. End2End verschlüsselung

1. GUI


class A1(object):
    def __init__(self, *args, **kwargs):
        self.a(*args,**kwargs)
    def a(self, val):
        print val

class A2(object):
    def __init__(self):
        print "hi a2"
    def a(self):
        print a.im_class

class B(A1,A2):
    def b(self):
        print "b"


B()

.a()
B().a.im_class
 
class myDecorator(object):
    def __init__(self, f):
        print "inside myDecorator.__init__()"
        f() # Prove that function definition has completed
    
    def __call__(self):
        print "inside myDecorator.__call__()"

@myDecorator
def aFunction():
    print "inside aFunction()"

print "Finished decorating aFunction()"
aFunction()
 

 
 
testconfig,myxmlreadertest
    Replaced

jabber -> Jabber
clusterbot -> ClusterBot