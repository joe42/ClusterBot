#!/usr/bin/python
"""
This module allows execution of commands via ssh, and scp.

*nix only because of ptys
"""

# Author: Rebecca Breu (rebecca@rbreu.de)

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


# TODO:
# * Special characters/encodings?
# * Let expect search for Regexps?
# * specify ssh port
# * what if someone uses keys?


import pty;
import os;
import select;
import errno;
import copy;
import re;

INIT_PROMPTS = ["> ", "# ", "$ "];
PROMPT = ["__very__unique__prompt__"]
PASSWDS = ["password: ", "Password: ", "passphrase:", "Passphrase:"];
CONTINUE = ["(yes/no)?", "(y/n)?"];

LANG = "en_US.UTF-8";
TIMEOUT = 10;

LS_INDICATORS = ["*", "@", "/", "="];

#Hope that this are all possible errors that can occur in the
#remote shell:
ERRORS = [os.strerror(i) for i in errno.errorcode.keys()] + \
         ["Name or service not known",
          "Temporary failure in name resolution",
          "does not exist",
          "not found",
          "Directory not empty",
          "cannot remove directory",
          "Not owner",
          "invalid mode",
          "invalid argument"
          ];


######################################################################
#Exceptions:
class Error(Exception):
    """
    Base class for exceptions in this module.

    strerror -- message
    """

    def __init__(self, strerror=""):
        self.strerror = strerror;

    def __str__(self):
        return self.strerror;


class ROSError(Error):
    """
    Exception raised when the execution of a remote command failed.

    strerror -- message
    filename -- filename
    """
    def __init__(self, strerror="", filename=""):
        self.strerror = strerror;
        self.filename = filename;

    def __str__(self):
        return "%s: %s" % (self.strerror, self.filename)


class ConnectError(Error):
    """
    Exception raised when connection to given host fails.

    strerror -- message
    host -- host to connect to 
    """

    def __init__(self, strerror="", host=""):
        self.strerror = strerror;
        self.host = host;

    def __str__(self):
        return "%s: %s" % (self.strerror, self.host)


class UIDError(Error):
    """
    Exception raised when authentication of the user fails.

    strerror -- message
    user -- login name
    """

    def __init__(self, strerror="", user=""):
        self.strerror = strerror;
        self.user = user;

    def __str__(self):
        return "%s: %s" % (self.strerror, self.user)


class TimeOutError(Error):
    """
    Exception raised when read() times out.

    strerror -- message
    read -- string read so far
    """

    def __init__(self, strerror, read):
        self.strerror = strerror;
        self.read = read;

    def __str__(self):
        return "%s: %s" % (self.strerror, self.read)


######################################################################
def expect(tty, exp_strings, ignore="", timeout=TIMEOUT, raise_timeout=True,
           raise_os=True):
    """
    Read from file descriptor 'tty' until one of the strings in 
    'exp_strings' is found or the attempt to read times out.

    tty -- file descriptor
    exp_strings -- list of strings
    ignore -- string of characters which are ignored while reading
    timeout -- timeout applied when trying to read one(!) character
    prompts -- list of prompts expected at the end ot the output,
               shouldn't be set if connetcion was established with
               rlogin
    raise_timeout -- If True, a TimeOutError is raised when a read times
                    out. Otherwise, the string read so far is returned.
    raise_os -- If True, an OSError is raised when encountering promblems
                with the file descriptor tty (e.g. child died). Otherwise,
                the string read so far is returned.
    """

    string = "";
    while True:
        [read, write, error] = select.select([tty], [], [], timeout);
        if tty in read:
            try:
                char = os.read(tty, 1);
                if not char in ignore:
                    string += char;

            except OSError:
                if raise_os:
                    raise;
                else:
                    return string;

            for exp_string in exp_strings:
                if string.find(exp_string) >= 0:
                    return string;
        else:
            if raise_timeout:
                raise TimeOutError("Timeout while reading", repr(string));
            else:
                return string;


######################################################################
def readline(tty, timeout=TIMEOUT, raise_timeout=True, raise_os=True):
    """
    Read a line from the file descriptor 'tty'. Return value is the line
    without the line seperator on success, otherwise a TimeOutError
    is raised.

    Line separators are \r, \n and \r\n.
    
    tty -- file descriptor
    timeout -- timeout applied when trying to read one(!) character
    raise_timeout -- If True, a TimeOutError is raised when a read times
                    out. Otherwise, the string read so far is returned.
    raise_os -- If True, an OSError is raised when encountering promblems
                with the file descriptor tty (e.g. child died). Otherwise,
                the string read so far is returned.
    """

    #I chose to accapt \r, \n AND \r\n as line seperators (instead of
    #os.linesep only), because I obsererved that a bash via ssh with
    #Linux both on the remote and local host returned \r\n as
    #seperator. (Why?)

    string = expect(tty, ["\r", "\n", "\r\n"], "", timeout, raise_timeout,
                    raise_os);

    return string.rstrip();


######################################################################
def execute(tty, command, timeout=TIMEOUT, prompts=PROMPT, rm_esc_seq=True):
    """
    Execute command in the remote shell and return it's output.
    Raise an Exception on timeout and on recognized error messages.
    
    tty -- file descriptor of the conrolling pseudoterminal of the
           remote shell
    command -- command to be executed
    timeout -- timeout applied when trying to read one(!) character
    prompts -- list of prompts expected at the end ot the output,
               shouldn't be set if connetcion was established with
               rlogin
    rm_esc_seq -- if True, remove graphical escape sequences from output
    """

    #Send command:
    os.write(tty, command + os.linesep);
    #Read the echo of the command: (When command is long, echo has additional
    #" \r" or similar in it)
    repr(expect(tty, [command.replace(" ", "")], " \r\n", timeout));
    #Read the output of the command:
    output = expect(tty, prompts, timeout=timeout);

    #Strip the prompt from the output:
    for prompt in prompts:
        output = output.replace(prompt, "");

    #Remove escape sequences if necessary:
    #Escape secuences are: \033[NN;NN;NNm
    if rm_esc_seq:
        output = re.sub("(\033)\\[.*?m", "", output);

    return output.strip();


######################################################################
def _set_env(tty, timeout=TIMEOUT, prompt=PROMPT, init_prompts=INIT_PROMPTS):
    """
    Set prompt to something unique and language to English. rlogin
    calls this function, afterwards it shouldn't be needed again.
    """

    #tcsh and csh:
    execute(tty, "setenv prompt=" + PROMPT[0], timeout, prompt + init_prompts);
    #sh, bash, ash, zsh, ksh:
    execute(tty, "export PS1=" + PROMPT[0], timeout, prompt + init_prompts);

    #tcsh and csh:
    execute(tty, "setenv LANG=" + LANG, timeout, prompt);
    #sh, bash, ash, zsh, ksh:
    execute(tty, "export LANG=" + LANG, timeout, prompt);


######################################################################
def find_prompt(tty, timeout=TIMEOUT, prompts=PROMPT, max_tries=10):
    """
    'expect'-ing the prompt can go wrong if the pompt searched for is
    not unique and can be found in normal output. find_prompt implements
    a safer way to identify the prompt.

    If logging in via rlogin, there should be no need to call this function
    manually (unless something gets totally weird.)
    """

    #Send a command whose output is easy to find:
    os.write(tty, "echo __find__a__prompt__" + os.linesep);
    #Now search for echo and output:
    expect(tty, ["__find__a__prompt__"], timeout=timeout);
    expect(tty, ["__find__a__prompt__"], timeout=timeout);
    #From here the real prompt should be easy to find:
    expect(tty, prompts, timeout=timeout);


######################################################################
def rlogin(host, user, passwd, timeout=TIMEOUT, init_prompts=INIT_PROMPTS,
           passwds=PASSWDS, errors=ERRORS, continues=CONTINUE):
    """
    Performs a login on the remote host via ssh. Return value is the tuple
    (pid, tty), which contains the pid of the ssh-process and a file descriptor
    which represents a pseudo terminal controlling the remote shell.

    Internals: To make working with the tty more sane, rlogin changes the shell
    prompt and the LANG environment variable.

    host -- hostname or IP adress
    user -- login name
    passwd -- password
    timeout -- timeout applied when trying to read one(!) character
    init_prompts -- list of shell prompts which are expected at the end of
                    the login procedure
    passwds -- list of password prompts which are expected 
    errors -- list of error messages which are expected 
    continues -- list of \"Are you sure want to continue\" prompts which are
                 expected 
    """

    [pid, tty] = pty.fork();
    if pid == 0:
        ssh_environ = copy.copy(os.environ);
        ssh_environ["LANG"] = LANG;
        os.execle("/usr/bin/ssh", "ssh", user + "@" + host, ssh_environ);

    else:
        #Wait for password prompt, error message or shell prompt
        output = expect(tty, passwds + errors + continues + init_prompts,
                        timeout=timeout);

        for err in errors:
            if output.find(err) >= 0:
                #An error occured:
                raise ConnectError(err, host);

        for cont in continues:
            if output.find(cont) >= 0:
                #Always accept unknown RSAs:
                os.write(tty, "yes" + os.linesep);
                output = expect(tty, passwds + errors + init_prompts,
                                timeout=timeout);

        for pwdprompt in passwds:
            if output.find(pwdprompt) >= 0:
                #provide password:
                os.write(tty, passwd + os.linesep);

                #Wait for shell prompt or second password prompt:
                output = expect(tty, passwds + init_prompts, timeout=timeout);

                for pwdprompt in passwds:
                    if output.find(pwdprompt) >= 0:
                        #Authentication went wrong if we get a second
                        #password prompt:
                        raise UIDError("User authentication failed", user);

                break;

        #Now we are logged in, customize the session:
        find_prompt(tty, timeout, init_prompts);
        _set_env(tty, timeout, PROMPT, init_prompts);
        return (pid, tty);


######################################################################
def scp(passwd, src, dest, timeout=TIMEOUT, passwds=PASSWDS, errors=ERRORS,
        continues=CONTINUE):
    """
    On success, returns output of scp.
    
    passwd -- password
    src -- source file of the form [[user@]host:]file
    dest -- destination file of the form [[user@]host:]file
    timeout -- timeout applied when trying to read one(!) character
    passwds -- list of password prompts which are expected
    errors -- list of error messages which are expected
    continues -- list of \"Are you sure want to conitnue\" prompts which are
                 expected
    """

    [pid, tty] = pty.fork();
    if pid == 0:
        ssh_environ = copy.copy(os.environ);
        ssh_environ["LANG"] = LANG;
        os.execle("/usr/bin/scp", "scp", src, dest, ssh_environ);

    else:
        #Wait for password prompt or error message:
        output = expect(tty, passwds + errors + continues, timeout=timeout);

        for error in errors:
            if error in output:
                #An error occured:
                raise ConnectError(error, "");

        for cont in continues:
            if cont in output:
                #Always accept unknown RSAs:
                os.write(tty, "yes" + os.linesep);
                output = expect(tty, passwds, timeout=timeout);

        #provide password:
        os.write(tty, passwd + os.linesep);

        #Wait for second password prompt or death of child:
        output = expect(tty, passwds, timeout=timeout, raise_os=False);

        for err in errors:
            if err in output:
                raise ROSError(err, src + ", " + dest);
        for pwd in passwds:
            if pwd in output:
                raise UIDError("User authentication failed");

        return output.strip();


######################################################################
def rlogout(tty, timeout=TIMEOUT):
    """
    End remote session.
    """

    os.write(tty, "exit" + os.linesep);
    expect(tty, ["closed."], timeout=timeout);


######################################################################
def rpwd(tty, timeout=TIMEOUT):
    """
    Get working directory of the remote shell.
    """
    return execute(tty, "pwd", timeout);


######################################################################
def rlistdir(tty, rdir, timeout=TIMEOUT, indicators=LS_INDICATORS):
    """
    Like os.listdir.

    tty -- file descriptor
    rdir -- remote direcory
    timeout -- timeout applied when trying to read one(!) character
    indicators -- list of special characters which are to be removed
                  from the end of the filenenames, like \"*\" or \"@\"
                  (some implementations of ls use those to indicate
                  executable files or soft links)
    """

    output = execute(tty, "ls -A1 --quoting-style=escape " + rdir, timeout);

    for err in ERRORS:
        if output.find(err) >= 0:
            raise ROSError(err, rdir);

    #On some systems, ls quotes special chars (space, "\")
    output = output.replace("\\ ", " ");
    output = output.replace("\\\\", "\\");

    output = output.splitlines();

    ls_list = [];

    for entry in output:
        for char in indicators:
            if entry.endswith(char):
                ls_list.append(entry[:-1]);
                break;
        else:
            ls_list.append(entry);

    return ls_list;

#############################pdsh -a sensors#########################################
def rcatfile(tty, rfile, timeout=TIMEOUT, indicators=LS_INDICATORS):
    """
    Like ">>cat rfile".

    tty -- file descriptor
    rfile -- remote file
    timeout -- timeout applied when trying to read one(!) character
    indicators -- list of special characters which are to be removed
                  from the end of the filenenames, like \"*\" or \"@\"
                  (some implementations of ls use those to indicate
                  executable files or soft links)
    """

    output = execute(tty, "cat " + rfile, timeout);

    for err in ERRORS:
        if output.find(err) >= 0:
            raise ROSError(err, rfile);

    #On some systems, ls quotes special chars (space, "\")
    #output = output.replace("\\ ", " ");
    #output = output.replace("\\\\", "\\");

    output = output.splitlines();

    ls_list = [];

    for entry in output:
        for char in indicators:
            if entry.endswith(char):
                ls_list.append(entry[:-1]);
                break;
        else:
            ls_list.append(entry);

    return ls_list;

#############################pdsh -a sensors#########################################
def ranycmd(tty, cmd, timeout=TIMEOUT):
    """
    Execute any kind of shell command.

    :param tty: file descriptor
    :param cmd: shell command as string
    :param timeout: timeout applied when trying to read one(!) character 
    """

    output = execute(tty, str(cmd), timeout);

    for err in ERRORS:
        if output.find(err) >= 0:
            raise ROSError(err, rfile);

    #On some systems, ls quotes special chars (space, "\")
    #output = output.replace("\\ ", " ");
    #output = output.replace("\\\\", "\\");

    output = output.splitlines();

    return output;

######################################################################
def rsensors(tty, hostlist, timeout=TIMEOUT, indicators=LS_INDICATORS):
    """
    Like sensors.

    tty -- file descriptor
    hostlist -- list of hosts to execute sensors on
    timeout -- timeout applied when trying to read one(!) character
    indicators -- list of special characters which are to be removed
                  from the end of the filenenames, like \"*\" or \"@\"
                  (some implementations of ls use those to indicate
                  executable files or soft links)
    """

    output = execute(tty, "pdsh -a sensors ", timeout);

    for err in ERRORS:
        if output.find(err) >= 0:
            raise ROSError(err, "");

    #On some systems, ls quotes special chars (space, "\")
    #output = output.replace("\\ ", " ");
    #output = output.replace("\\\\", "\\");

    output = output.splitlines();

    ls_list = [];

    for entry in output:
        for char in indicators:
            if entry.endswith(char):
                ls_list.append(entry[:-1]);
                break;
        else:
            ls_list.append(entry);

    return ls_list;


######################################################################
def rabspath(tty, dirfile, timeout=TIMEOUT):
    """
    Like os.abspath.
    """

    if dirfile.startswith("/"):
        #dirfile is already absolute path
        return os.path.normpath(dirfile);
    else:
        abspath = rpwd(tty, timeout) + "/" + dirfile;
        return os.path.normpath(abspath);


######################################################################
def risdir(tty, dirfile, timeout=TIMEOUT):
    """
    Like os.path.isdir.
    """

    sh_cmd = "if ( test -d " + dirfile + " ) then echo \"is directory\";" + \
               "else echo \"not directory\"; fi";

    output = execute(tty, sh_cmd, timeout);

    #if "is directory" in output:
    if output.find("is directory") >= 0:
        return True;
    else:
        return False;


######################################################################
def risfile(tty, dirfile, timeout=TIMEOUT):
    """
    Like os.path.isfile.
    """

    sh_cmd = "if ( test -f " + dirfile + " ) then echo \"is file\";" + \
               "else echo \"not file\"; fi";

    output = execute(tty, sh_cmd, timeout);

    #if "is file" in output:
    if output.find("is file") >= 0:
        return True;
    else:
        return False;


######################################################################
def rremove(tty, rfile, timeout=TIMEOUT):
    """
    Like os.remove.
    """

    QUESTION = "? ";

    output = execute(tty, "rm " + rfile, timeout, PROMPT + [QUESTION]);

    #if question in output:
    if output.find(QUESTION) >= 0:
        #Always delete write protected files:
        os.write(tty, "yes" + os.linesep);
        output = expect(tty, PROMPT, timeout=timeout);

    for err in ERRORS:
        if output.find(err) >= 0:
            raise ROSError(err, rfile);


######################################################################
def rmkdir(tty, rdir, timeout=TIMEOUT, mode=755):
    """
    Like os.mkdir.
    """

    mkdir_cmd = "mkdir -m " + str(mode) + " " + rdir;
    output = execute(tty, mkdir_cmd, timeout);

    for err in ERRORS:
        if output.find(err) >= 0:
            raise ROSError(err, rdir);


######################################################################
def rrmdir(tty, rdir, timeout=TIMEOUT):
    """
    Like os.rmdir.
    """

    output = execute(tty, "rmdir " + rdir, timeout);

    for err in ERRORS:
        if output.find(err) >= 0:
            raise ROSError(err, rdir);


######################################################################
def rrename(tty, src, dest, timeout=TIMEOUT):
    """
    Like os.remove.
    """

    output = execute(tty, "mv " + src + " " + dest, timeout);

    for err in ERRORS:
        if output.find(err) >= 0:
            raise ROSError(err, src + ", " + dest);


######################################################################
def rchmod(tty, dirfile, mode, timeout=TIMEOUT):
    """
    Like os.chmod, only that 'mode' is given as numeric value like in
    the Unix command chmod. (For example, to set read, write and execute
    permissions for the user and read permissions for the group and others,
    use 744.)
    """

    output = execute(tty, "chmod " + str(mode) + " " + dirfile, timeout);

    for err in ERRORS:
        if output.find(err) >= 0:
            raise ROSError(err, dirfile);


######################################################################
class rfile:


    def __init__(self, passwd, rfile, mode="r", bufsize=-1, timeout=TIMEOUT,
                 passwds=PASSWDS, errors=ERRORS, continues=CONTINUE):
        """
        Open remote file.

        If mode is not 'w', the file is copied via scp to
        the localhost and then opened. If mode is 'w', a new file is opened.

        passwd -- password
        rfile -- remote file of the form [[user@]host:]file
        mode -- File open mode. See builtin open() for more information.
        bufsize --  The file's desired buffer size. See builtin open() for more
                    information.
        timeout -- timeout applied when trying to read one(!) character
        passwds -- list of password prompts which are expected
        errors -- list of error messages which are expected
        continues -- list of \"Are you sure want to conitnue\" prompts which
                     are expected

        """

        self.passwd = passwd;
        self.rfile = rfile;
        self.timeout = timeout;
        self.passwds = passwds;
        self.errors = errors;
        self.continues = continues;

        #Copy remote file to a temporary local file:
        tmp_filename = os.tempnam();

        if "w" not in mode:
            scp(passwd, rfile, tmp_filename, timeout, passwds, errors,
                continues);

        self.lfile = open(tmp_filename, mode, bufsize);


    def close(self):
        """
        Close the file.

        If the file was opened for writing, the modified local file will be
        copied back to it's origin via scp.
        """

        self.lfile.close();

        if "r" not in self.lfile.mode:
            scp(self.passwd, self.lfile.name, self.rfile, self.timeout,
                self.passwds, self.errors, self.continues);

        os.remove(self.lfile.name);


    def __getattr__(self, name):
        """
        Access to attributes of self.lfile.
        """

        if name in ["fileno", "flush", "next", "read", "readline",
                    "readlines", "xreadlines", "seek", "tell", "truncate",
                    "write", "writelines", "encoding", "mode", "name",
                    "newlines", "softspace"]:
            return getattr(self.lfile, name)
        else:
            raise AttributeError(name)