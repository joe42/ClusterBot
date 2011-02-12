import thread 
import select
import time
from clusterbot import ssh
import os

"""An interactive shell for Python.
Send a command as strings with :meth:`sendcmd`. 
The reply follows in an asynchronous manner and is passed as an argument to the outputCallback defined as a parameter to :meth:`__init__`. 
"""
class MyConsole():
    SESSION_END = "end";
    def __init__(self, outputCallback, host, user, pwd = ""):
        """ Establishes a connection to the __host with the credentials given.
        :param __outputCallback: A function called with the console output as a string parameter."""
        self.__outputCallback = outputCallback;
        self.__host = host;
        self.__user = user;
        self.__pwd = pwd;
        self.__cmd = "";
        self.__timeOfLastFlush = 0
        self.__cmdAccessLock = thread.allocate_lock();
        self.__pid = None;
        self.__tty = None;
        self.setTerminated(True); 
        self.reconnect();
        
    def reconnect(self):
        if self.__hasTerminated:
            try:
                (self.__pid,self.__tty)=ssh.rlogin(self.__host, self.__user, self.__pwd)
                self.setTerminated(False);
            except:
                self.setTerminated(True);
                raise
            thread.start_new_thread(self.__readtty, ())
            
    
    def sendcmd(self, command):
        """Send a command to the console.
        .. note::

            BUG: This issue can be improved upon, but cannot be solved by a locking and synchronization mechanism, 
            since there is no guarantee that a command is followed by a reply.

        The command sending and execution is not atomic. 
        It might happen that several commands are sent and the corresponding output comes unordered at any time.
        To make things worse, the most recent command string is used to strip the echo of the ssh response from the output.
        So if the output is a reply to a previous command and contains the most recent command string, the response is stripped by the first occurrence of this string.
        On the other hand the reply might still contain the ssh echo of the command, if another command was issued before the reply could be processed.  

        """
        if len(command.strip(" \n\r")) == 0:
            return;
        self.__cmdAccessLock.acquire();
        #inside of lock, since self.__cmd is used to filter the commands echo from the output
        os.write(self.__tty,command+os.linesep);         
        self.__cmd = command;
        self.__cmdAccessLock.release();
        
    def hasTerminated(self):
        """:returns: True iff the shell session is terminated (this is also true if the session has never been established)."""
        return self.__hasTerminated;
    
    def setTerminated(self, terminate=True):
        """Sets the :attr:`__hasTerminated`. If *terminate* is True, the shell session is terminated."""
        if  terminate and not self.__hasTerminated:
            self.__hasTerminated = True;
            self.__outputCallback("Session will be terminated.");
            ssh.rlogout(self.__tty);
            os.waitpid(self.__pid, 0); 
            self.__outputCallback("Session was terminated by user.");
        self.__hasTerminated = terminate;
        
    def __getSecondsSinceLastFlush(self):
        """Gets the number of seconds that passed since the last call of  :meth:`__outputCallback`"""
        return time.time() - self.__timeOfLastFlush
     
    def __readtty(self):
        def isSessionEnd(string):
            """:returns: True iff the command contains SESSION_END."""
            return string.find(self.SESSION_END) >= 0
        def flush(string, buffered = True):
            """Responsible for output."""
            if buffered and not enoughTimePassed():
                return;
            self.__timeOfLastFlush = time.time();
            string = string.replace("__very__unique__prompt__", "");
            self.__cmdAccessLock.acquire();
            if self.__cmd != "" and string.find(self.__cmd) >= 0:
                string = string.replace(self.__cmd, ""); # remove the echo of the command from output
                self.__cmd = ""
            self.__cmdAccessLock.release();
            if len(string.strip(" \n\r")) != 0:
                self.__outputCallback(string);
        def enoughTimePassed():
            return self.__getSecondsSinceLastFlush() >= 1;
        
        string = ""; 
        char = '';
        while True:
            [read, write, error] = select.select([self.__tty], [], [], 1); #wait for possible IO operation
            if self.__tty in read:
                try:
                    char = os.read(self.__tty, 1);
                    string += char;
                except OSError:
                    flush(string, buffered = False); 
                    string = ""
                if isSessionEnd(string):
                    self.setTerminated(True);
                if self.hasTerminated():
                    return;
            else:
                flush(string); 
                string = ""
                """Console might be terminated from outside by a call to :meth:`setTerminated`."""
                if self.hasTerminated():
                    return;
    
     

