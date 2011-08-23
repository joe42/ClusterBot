from clusterbot.jabberbot import JabberBot, botcmd
import clusterbot.commands 
import clusterbot.commandmodules
from ssh import *; 
import xmpp
import pkgutil, sys

class ClusterBot(JabberBot):
	"""A Jabber service to monitor clusters.
	
	* Has a standing ssh connection to the headnode of a cluster to send commands via the ssh module.
	* Allows for whitelisting by Jabber ids.
	* Supports runtime loading of new command modules (see :meth:`importnewcommands`).
	
	"""
	def __init__(self, jabberID, jabberPW, headnodeIP, headnodeUser, headnodePW, debug=False): 
		super( ClusterBot, self ).__init__(jabberID, jabberPW, debug=debug);
		self.pluginCommands = {};
		self.headnodeIP = headnodeIP;
		self.headnodeUser = headnodeUser;
		self.headnodePW = headnodePW; 
		self.__jabberID = jabberID
		self.__whitelist = None
		self.__pid = None
		self._tty = None
		if None in [jabberID, jabberPW]:
			self.log.warning("Arguments do not supply enough information to connect to the xmpp server.")
			return;
		if None in [self.headnodeIP, self.headnodeUser, self.headnodePW]:
			self.log.warning("Arguments do not supply enough information to establish an ssh connection to the headnode.")
			return;
		self.log.info("Logging in..."); 
		(self.__pid, self._tty) = rlogin(self.headnodeIP, self.headnodeUser, self.headnodePW);

	@botcmd
	def reconnect(self, mess, args):
		"""Connects the bot via ssh to the headnode of the cluster.
		This is useful in case the ssh connection timed out.
		"""
		if not self.__connectionEstablished():
			if None in [self.headnodeIP, self.headnodeUser, self.headnodePW]:
				self.log.warning("Arguments do not supply enough information to establish an ssh connection to the headnode.")
				return;
			self.log.info("Logging in..."); 
			(self.__pid, self._tty) = rlogin(self.headnodeIP, self.headnodeUser, self.headnodePW);
	
	def __connectionEstablished(self):
		"""Sends a simple command to the headnode to see if the connection is established.
		:returns: True if the command was executed successfully and False otherwise. 
		"""
		try:
			ranycmd(self._tty, 'echo connection established');
		except TimeOutError:
			return False;
		return True;

	def quit(self):
		"""Overwrites :meth:`clusterbot.jabberbot.JabberBot.quit`."""
		super( ClusterBot, self ).quit();
		if not self._tty is None:
			rlogout(self._tty);
			os.waitpid(self.__pid, 0); 
		self.log.info("Logged out...");

	@botcmd
	def serverinfo(self, mess, args):
		"""Serverinfo"""
		return "Clusterbot server for cluster monitoring and management through xmpp.";

	@botcmd
	def ls(self, mess, args):
		"""Works like ls on Linux.""" 
		return reduce((lambda x,y: x+"\n"+y),rlistdir(self._tty, ".")); 

	@botcmd
	def cat(self, mess, args): 
		"""Works like cat on Linux."""
		return reduce((lambda x,y: x+"\n"+y),rcatfile(self._tty, mess));

	@botcmd
	def echo(self, mess, args): 
		"""Repeats everything like a parrot."""
		return str(args);

	@botcmd
	def whoami(self, mess, args): 
		"""Tells your username."""
		return str(self.get_sender_username(mess));

	@botcmd
	def getjid(self, mess, args): 
		"""Tells your jabber id."""
		return str(mess.getFrom())

	@botcmd
	def get(self, mess, args): 
		"""Gets a few system parameters, but at the moment only get temp is allowed to view system temperatures."""
		return reduce((lambda x,y: x+"\n"+y),rsensors(self._tty, mess)); 

	@botcmd(hidden=True)
	def holla(self, mess, args):
		""""""
		return 'Holla die Waldfee!'

	@botcmd(hidden=True)
	def hello(self, mess, args):
		""""""
		return 'Hello there! If you are new to clusterbot service type help for a list of commands.'
	
	def set_whitelist(self, whitelist):
		"""Sets the whitelist for allowed Jabber IDs.
		Without setting a custom whitelist, every Jabber ID is allowed.
		:param whitelist: List of Strings with Jabber IDs to allow
		"""
		self.__whitelist = whitelist
		self.__whitelist.append(self.__jabberID)#don't ignore messages from self
			
	def is_authentication_successful(self, jid):
		if self.__whitelist == None:
			return True
		for id in self.__whitelist:
			if jid.bareMatch(id):
				return  True
				break
		return False
	
	def callback_message(self, conn, presence):
		"""Overwrites callback_message to disallow subscription of users not listed in allowedJIDS."""
		jid = presence.getFrom();
		authenticationSuccessful = self.is_authentication_successful(jid)
		if not authenticationSuccessful or jid is None: #jid is None if message comes from server
			return;
		else:
			super( ClusterBot, self ).callback_message(conn, presence); 
			
	@botcmd
	def broadcast( self, message, users=None):
		"""Broadcasts the message to a list of users given as jabber ids."""
		if users == None:
			users = self.users;
		for user in users:
			self.send( user, message)
	
	@botcmd
	def importnewcommands(self, mess, args):
		"""Loads new command modules from the package clusterbot.commandmodules"""
		pkgpath = os.path.dirname(clusterbot.commandmodules.__file__);
		for newCommandName in [name for _, name, _ in pkgutil.iter_modules([pkgpath])]:
			__import__("clusterbot.commandmodules."+newCommandName);
			newmodule = sys.modules["clusterbot.commandmodules."+newCommandName];
			newCommand = newmodule.returnInstance(self._tty,args);
			try:
				getattr(newCommand, 'executeCommand');
			except AttributeError:
				self.log.error("The extension %s does not provide the Command interface with the executeCommand(self,mess,args) method!" % newCommandName);
				continue;
			try:
				getattr(newmodule, 'returnInstance');
			except AttributeError,TypeError:
				self.log.error("The command %s does not provide the returnInstance(_tty, args) function!" % newCommand.getName());
				continue;
			if newCommand.getName() in self.commands or newCommand.getName() in self.pluginCommands:
				self.log.error("The command %s already exists, please rename your extension!" % newCommand.getName());
				continue;
			self.pluginCommands[newCommand.getName()] = newCommand;
		return "Alright, use the listcommands command to get an overview on the imported modules.";


	@botcmd
	def listcommands( self, mess, args):
		"""Lists plugged in commands."""
		ret = "";
		for names in self.pluginCommands:
			ret += "Name: "+names+"\n";
			ret += "Desc: "+self.pluginCommands[names].getDescription()+"\n";
		
		return ret;

	def unknown_command(self, mess, cmd, args):
		"""Overwrites :meth:`clusterbot.jabberbot.JabberBot.unknown_command`.
		Handles plugin commands.
		"""
		if cmd in self.pluginCommands:
			try:
				return self.pluginCommands[cmd].executeCommand(mess, args);
			except TimeOutError:
				return "A timeout occurred during command execution."
			except:
				return "An error occurred during command execution."
		else:
			return None;


