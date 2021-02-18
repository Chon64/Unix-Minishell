#!/usr/bin/env python3

import os, sys, re

#Sets PS1 to $$$
os.environ["PS1"] = "$$$"

#Checks for and removes characters to prepare for command execution
def format_string(list):
    for i in list:
        if '' in list:
            list.remove('')
        if ' ' in list:
            list.remove(' ')
        if '>' in list:
            list.remove('>')
            list = list[:-1]
    return list

#Given a file directory number and an output, will redirect correspondingly
def redirect_output(fd_num, out_file):
    try:
        os.close(fd_num)
        os.open(out_file, os.O_CREAT | os.O_WRONLY)
        os.set_inheritable(fd_num, True)
        return
    except:
        os.write(2, "Failed to redirect output")
        sys.exit(1)

#Stores parent PID
pid = os.getpid()

while 1: #Main shell loop
    user_in = input(os.environ["PS1"] + " ")
  
    #Exits if user chooses
    if user_in == "exit":
        break

    #Check for &
    if '&' in user_in:
        command_list = user_in.split('&')
    else:
        command_list = [user_in]
    
    #Attempts to run all commands in the command_list
    for command in command_list:
        
        #Creates Child process
        rc = os.fork()
            
        if rc < 0: #Fork Fails
            os.write(2, ("Fork failed, returning %d\n" % rc).encode())
            sys.exit(1)
        
        elif rc == 0: #Child process
            #Split single command and its args
            split_line = command.split(" ")             
            
            #Checks for output redirect
            if '>' in split_line:
                #This part done in multiple steps for clarity
                output_file_index = split_line.index('>')
                output_file = split_line[output_file_index + 1]
                redirect_output(1, output_file)
            
            #Removes '', ' ', '>' and output file in list to prepare for execution
            split_line = format_string(split_line)
            
            #Check for cd command
            if split_line[0] == 'cd' and len(split_line) < 2: #No directory specified
                pass
            elif split_line[0] == 'cd':
                try:
                    os.chdir(split_line[1])
                except:
                    os.write(2, "Directory path not valid")
                    pass
            else:#Runs command if not cd
                #Try directories in PATH
                for dir in re.split(":", os.environ['PATH']):
                    program = "%s/%s" % (dir, split_line[0])
                    try:
                        os.execve(program, split_line, os.environ) # try to exec program
                        redirect_output(1, sys.stdout)
                    except FileNotFoundError:             # ...expected
                        pass                              # ...fail quietly
                os.write(2, ("Error: Command not found: %s\n" % split_line[0]).encode())
                sys.exit(1)                 # terminate with error

        else: #Parent process
            childPidCode = os.wait()