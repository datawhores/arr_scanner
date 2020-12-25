
#! /usr/bin/env python3
"""NOTE: READ DOCUMENTATION BEFORE USAGE.
Usage:
    ahd_cross.py radarr [--txt=<txtlocation> --config <config> --delete --fd <binary_fd> --fdignore <ignore_list_fd>]
    [--root <root>... --ignore <sub_folders_to_ignore>...]

    ahd_cross.py sonarr [--txt=<txtlocation> --config <config> --delete --fd <binary_fd> --fdignore <ignore_list_fd> ]
    [--root <root>... --ignore <sub_folders_to_ignore>...]

Options:
 -h --help     Show this screen.
--txt <txtlocation>  txt file with all the file names(required for all commands)
--fd <binary_fd> fd is a program to scan for files, use this if you don't have fd in path,(optional)   [default: fd]
--fdignore <gitignore_style_ignorefile> fd .fdignore file used by fd tto find which folders to ignore, on linux it defaults to the home directory.
--root <normal_root(s)> Scan this directory.
--config ; -x <config> commandline overwrites config
 ahd_cross.py scan scan tv or movie folders root folder(s) create a list of directories. 'txt file creator'. Need at least 1 root.
--ignore ; -i <sub_folders_to_ignore>  folder will be ignored for scan (optional)
  """

import os
from docopt import docopt
import configparser
config = configparser.ConfigParser(allow_no_value=True)
import sys
from shutil import which
import subprocess


def search_tv(arguments,ignorefile):
  workingdir=os.getcwd()
  if arguments['--root']==[] or arguments['--root']==None or len(arguments['--root'])==0:
      return
  folders=open(arguments['--txt'],"a+")
  print("Adding TV Folders to",arguments['--txt'])
  if type(arguments['--root'])==str:
      arguments['--root']=arguments['--root'].split(",")
  list=arguments['--root']
  for root in list:
      if root=="":
          continue
      if os.path.isdir(root)==False:
          print(root," is not valid directory")
          continue
      t=subprocess.run([arguments['--fd'],'Season\s[0-9][0-9]$','-t','d','.',root,'--max-depth','2','--min-depth','2','--ignore-file',ignorefile],stdout=folders)
  print("Done")
def search_movies(arguments,ignorefile):
    workingdir=os.getcwd()
    if arguments['--root']==[] or arguments['--root']==None or len(arguments['--root'])==0:
        return
    folders=open(arguments['--txt'],"a+")
    print("Adding Movies Folders to", arguments['--txt'])
    if type(arguments['--root'])==str:
        arguments['--root']=arguments['--root'].split(",")
    list=arguments['--root']
    for root in list:
        if root=="":
          continue
        if os.path.isdir(root)==False:
          print(root," is not valid directory")
          continue
    #old scanning method
    #subprocess.run([arguments['--fd'],'\)$','-t','d','--full-path',root,'--ignore-file',ignorefile],stdout=folders)
        t=subprocess.run([arguments['--fd'],'-e','.mkv','-t','f','.',root,'--max-depth','2','--ignore-file',ignorefile],stdout=folders)
    print("Done")

def setup_txt(arguments):
    file=arguments['--txt']
    try:
        open(file,"a+").close()
    except:
        print("No txt file")
        quit()


def setup_binaries(arguments):
    fdignore=arguments['--fdignore']
    workingdir=os.path.dirname(os.path.abspath(__file__))
    if fdignore==None:
        try:
            arguments['--fdignore']=os.path.join(workingdir,".fdignore")
        except:
            print("Error setting fdignore")
            exit()
    t=open(arguments['--fdignore'], 'w')
    t.close()

    if arguments['--fd']==None and sys.platform=="linux":
        if len(which('fd'))>0:
            arguments['--fd']=which('fd')
        else:
            fd=os.path.join(workingdir,"bin","fd")
            arguments['--fd']=fd

    if arguments['--fd']==None and sys.platform=="win32":
        if len(which('fd.exe'))>0:
            arguments['--fd']=which('fd')
        else:
            fd=os.path.join(workingdir,"bin","fd.exe")
            arguments['--fd']=fd
def set_ignored(arguments):
    ignore=arguments.get("--fdignore")
    if ignore==None or ignore==[] or ignore=="" or len(ignore)==0:
       return
    if type(arguments['--ignore'])==str:
        arguments['--ignore']=arguments['--ignore'].split(",")
    ignorelist=arguments['--ignore']
    if len(ignorelist)==0:
        return
    open(ignore,"w+").close()
    ignore=open(ignore,"a+")
    for element in ignorelist:
        if element=="":
            continue
        ignore.write(element)
        ignore.write('\n')

def duperemove(txt):
    print("Removing Duplicate lines from ",txt)
    if txt==None:
        return
    input=open(txt,"r")
    lines_seen = set() # holds lines already seen
    for line in input:
        if line not in lines_seen: # not a duplicate
            lines_seen.add(line)
    input.close()
    outfile = open(txt, "w")
    for line in lines_seen:
        outfile.write(line)
    outfile.close()

def updateargs(arguments):
    configpath=arguments.get('--config')
    if configpath==None:
        print("No config Found")
        return arguments
    if os.path.isfile(configpath)==False:
        print("Could Not Read Config Path")
        return arguments
    try:
        configpath=arguments.get('--config')
        config.read(configpath)
    except:
        print("Could Not Read Config Path")
        return arguments
    if arguments['--txt']==None:
        arguments['--txt']=config['general']['txt']
    if arguments['--root']==[] or  arguments['--root']==None:
        arguments['--root']=config['scan']['root']
    if arguments['--ignore']==[] or arguments['--ignore']==None:
        arguments['--ignore']=config['scan']['ignore']
    return arguments


if __name__ == '__main__':
    arguments = docopt(__doc__, version='ahd_cross_seed_scan 1.2')
    if arguments['radarr']:
        updateargs(arguments)
        setup_txt(arguments)
        setup_binaries(arguments)
        set_ignored(arguments)
        duperemove(arguments['--fdignore'])
        search_movies(arguments,arguments['--fdignore'])
        duperemove(arguments['--txt'])

    if arguments['sonarr']:
        updateargs(arguments)
        setup_txt(arguments)
        setup_binaries(arguments)
        set_ignored(arguments)
        duperemove(arguments['--fdignore'])
        search_tv(arguments,arguments['--fdignore'])
        duperemove(arguments['--txt'])
