#! /usr/bin/env python
## Author: Luca Pescatore, modified by Matthieu Marinangeli
## Mail: pluca@cern.ch
## Description: script to submit jobs (mostly done for lxplus but for local submissions works anywhere)
## N.B.: Needs an environment variable "JOBDIR" which is the location to put jobs outputs

import os, sys
from string import *
import re
from argparse import ArgumentParser
import subprocess as sub
import random
from datetime import datetime
import time
import getpass
from Utilities import red
from random import randint


now = datetime.now()
random.seed(now.day)

jobdir = os.getenv("JOBDIR")

if jobdir is None :
    jobdir = os.getenv("HOME")+"/jobs"
    os.system("mkdir -p "+jobdir)

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self
        
        default = {"subdir":  "",
                   "run":     -1,
                   "basedir": jobdir,
                   "jobname": "",
                   "setup":   "",
                   "clean":   True,
                   "interactive": False,
                   "shell":   "",
                   "unique":  False,
                   "local":   False,
                   "noscript": False,
                   "m_cpu":     4000,
                   "m_time":    20,
                   "exclude": 0,
                   "nodes2exclude": [],
                   "infiles": "",
                   "express":  False, 
                   "options": {}}
                   
        for d in list(default.keys()):
            if d not in self.__dict__.keys():
                self[d] = default[d]
        
def IsSlurm():
    
    # Check if there is a slurm batch system
    
    try:
        P = sub.Popen(["squeue"], stdout=sub.PIPE)
        _, _ = P.communicate()
    except OSError:
        return False
    else:
        return True
        
        
def PrepareSlurmJob( options, Dirname ):
    
    #prepare slurm batch job submission
    
    def GetSlurmNodes():
        
        cmd = sub.Popen(['sinfo','-N'], stdout=sub.PIPE)
        cmd_out, _ = cmd.communicate()    
        output = cmd_out.split("\n")
        output.remove(output[0])
        
        list_nodes = []
        for o in output:
            if "batch" in o:
                list_nodes.append( o.split(" ")[0] )
                
        return list_nodes

    oldrun = open(Dirname+"/run.sh")
    oldrunstr = oldrun.read()
    oldrun.close()

    fo = open(Dirname+"/run.sh","w")
    fo.write("#!/bin/bash -fx\n")                       
    fo.write("#SBATCH -o " + Dirname + "/out\n")
    fo.write("#SBATCH -e " + Dirname + "/err\n")
    fo.write("#SBATCH -J " + options.subdir + options.jobname + "\n")
    fo.write("#SBATCH --mem-per-cpu "+str(options.m_cpu)+"\n")
#    fo.write("#SBATCH --mem 5000\n")
    fo.write("#SBATCH -n 1\n")
    fo.write("#SBATCH -p batch\n")
    fo.write("#SBATCH -t {0}:00:00\n".format(options.m_time))
    
    if options.express:
       fo.write("#SBATCH --qos=express\n")
    
    exclude = options.exclude
    nodestoexclude = options.nodes2exclude
    
    if exclude != 0 or len(nodestoexclude) > 0:        
        now = datetime.now()
        random.seed(now.day)
        
        nodes = GetSlurmNodes()
        random.shuffle(nodes)
        
        n2exclude = int(exclude) + len(nodestoexclude)
        
        #### check if nodes exit
        exists = all(n in nodes for n in nodestoexclude)
        
        if not exists:
            _nodestoexclude = []
            for n in nodestoexclude:
                if not n in nodes:
                    warnings.warn( red(" WARNING: node {0} does not exist. \
                                It will be removed!".format(n)), stacklevel = 2 )
                else:
                    _nodestoexclude.append(n)
            nodestoexclude = _nodestoexclude
            
        for n in nodestoexclude:
            nodes.remove(n)

        nodes = nodes[0:(n2exclude - len(nodestoexclude))]
        nodes += nodestoexclude
        
        nodes2exclude = ""
        for n in nodes:
            if n == nodes[-1]: nodes2exclude += n
            else: nodes2exclude += n +","
                
        fo.write("#SBATCH --exclude={0}\n\n\n".format(nodes2exclude))
    
    fo.write(oldrunstr)
    fo.close()
    
    command = "sbatch "+Dirname+"/run.sh"
    return command
        
def sendcommand(command, sendoptions):
    
    SUBMIT = False
    while SUBMIT is False:
        SUBMIT = subcondition(sendoptions)
        if not SUBMIT:
            time.sleep(randint(0, 5) * 60)
    
    if sys.version_info[0] > 2:
        out = sub.check_output( command, shell = True, encoding='utf8')
    else:
        out = sub.check_output( command, shell = True)

    return out
    
def subcondition(options):
    
    user = getpass.getuser()
        
    #additionnal submission conditions for SLURM batch system 
                        
    Njobs_user     = int( os.popen( "echo $(squeue  | grep -c '{0}')".format(user)           ).read() )
    Npendjobs_user = int( os.popen( "echo $(squeue -u {0} | grep -c 'PD')".format(user)      ).read() )
    
    now = datetime.now()
    hour = now.hour
    
    #conditions
    jobs_user     = options.get('nuserjobs', 2999) <= Njobs_user        
    pendjobs_user = options.get('npendingjobs', 2999) <= Npendjobs_user
            
    if jobs_user:
        print( red("You have already submitted {0} jobs. Wait for submission!".format(Njobs_user)) )
        Submission = False
    elif pendjobs_user:
        print( red("You have already {0} jobs pending. Wait for submission!".format(Npendjobs_user)) )
        Submission = False
    elif not (jobs_user and pendjobs_user):
        Submission = True
                
    return Submission
    
def main(opts):
    
    if type(opts) == dict:
        opts = AttrDict(opts)

    exe, execname = None, None
    commands = opts.command.split(' ')

    if(len(commands) < 1) : print("Not enough arguments")
    elif "." in commands[0] : 
        execname = commands[0].replace('./','')
        args = commands[1:]
    elif "lb-run" in commands[0]:
        if "-c" in commands[1]:
            endcommand = 5
        else:
            endcommand = 3
        exe = " ".join(commands[0:endcommand])
        execname = commands[endcommand]
        args = commands[endcommand+1:]
    elif len(commands) > 1 : 
        execname = commands[1]
        exe      = commands[0]
        args = commands[2:]
        
        if not "." in execname:
            execname  = ""
            args = commands[1:]
            
    else : sys.exit()
    if(opts.jobname == "") :
        jobname = re.sub(r'\..*',"", execname.replace('./',''))
   
    ########################################################################################
    ## Make the needed folders and copy the executable and everything else needed in them
    ########################################################################################
    
    subdirname = opts.basedir
    if opts.subdir != "" :
        subdirname += "/"+opts.subdir
    dirname = subdirname+"/"+opts.jobname

    if opts.run > -1 :
        dirname += "_"+str(opts.run)

    if os.path.exists(dirname) and opts.clean :
        os.system("rm -fr " + dirname+"/*")
    os.system("mkdir -p " + dirname)

    if(opts.unique) : copyto = subdirname
    else : copyto = dirname
    
    if not execname == "":
        os.system("cp " + execname + " " + copyto )
    if '/'  in execname :
        execname = execname.split("/")[-1]
    
    for arg in opts.infiles.split() :
        os.system("cp " + arg + " " + copyto )
        if opts.unique :
            os.system("ln -s {f1} {f2}".format(f1=copyto+'/'+arg,f2=dirname+'/'+arg))
            
    ########################################################################################
    ## Create the run.sh file containing the information about how the executable is run
    ########################################################################################

    os.system( "cd " + dirname )
    runfile = open(dirname+"/run.sh","w")
    if opts.shell != "" :                   ### Settings    
        runfile.write(opts.shell + "\n")
    runfile.write( "cd " + dirname + "\n")
    if opts.setup != "" :
        runfile.write(opts.setup + "\n")
    if exe is None and not opts.noscript:   ### Ensure executable
        runfile.write("chmod 755 " + copyto + "/" +execname +'\n')

    if  execname == "":
        pathexec = ""
    else:
        pathexec = copyto+"/"+execname
        
    if exe is None:
        runfile.write( '{dir} {args}'.format(dir=pathexec,args=' '.join(args)) + "\n")
    else :
        runfile.write( '{exe} {dir} {args}'.format(exe=exe,dir=pathexec,args=' '.join(args)) + "\n")

    if opts.local or opts.interactive :     ### Output
        runfile.write( " >& " + dirname + "/out " )
    runfile.close()
    os.system( "chmod 755 " + dirname + "/run.sh" )
    
    ########################################################################################
    ## Run executable in local or batch mode
    ########################################################################################
    
    if(opts.subdir != "") :
        opts.subdir=(re.sub("^.*/","",opts.subdir)+"_")
    
    if opts.local :                           ## Local
        print("Running local")
        command  = "cd " + dirname
        command += dirname + "/run.sh &"
                        
    elif IsSlurm():
        command = PrepareSlurmJob(opts, dirname)
        out = sendcommand(command, opts.options)
        ID = int( out.split(" ")[-1] )
        print( "Submitted batch job {0}".format(ID) )
        return ID
     
    else :
        print("Can run in batch mode on a slurm batch system only. Go there or run with '--local'")
     
if __name__ == "__main__" :
        
    parser = ArgumentParser()
    parser.add_argument("-d", default="", dest="subdir", 
        help="Folder of the job, notice that the job is created anyway in a folder called as the jobname, so this is intended to group jobs")
    parser.add_argument("-r", default=-1, dest="run", help="Add run number")
    parser.add_argument("-D", default=jobdir, dest="basedir",
        help="This option bypasses the JOBDIR environment variable and creates the job's folder in the specified folder")
    parser.add_argument("-n", default="", dest="jobname", 
        help="Give a name to the job. The job will be also created in a folder with its name (default is the executable name)")
    parser.add_argument("--bash", dest="shell", default = "", action="store_const", const = "#!/usr/bin/env bash",
        help="Initialize a new bash shell before launching" )
    parser.add_argument("--tcsh", dest="shell", default = "", action="store_const", const = "#!/usr/bin/env tcsh",
        help="Initialize a new tcsh shell before launching" )
    parser.add_argument("-q", dest="queue", default = "8nh", help="Choose bach queue (default 8nh)" )
    parser.add_argument("-s", dest="setup", default = "", help="Add a setup line to the launching script" )
    parser.add_argument("--noClean", dest="clean", action="store_false",
        help="If the job folder already exists by default it cleans it up. This option bypasses the cleaning up" )
    parser.add_argument("--interactive", dest="interactive", action="store_true",
        help="Submits on lxplus without using the batch system" )
    parser.add_argument("--uexe", dest="unique", action="store_true",
        help="Copy the executable only once in the top folder (and not in each job folders)" )
    parser.add_argument("--local", dest="local",  action="store_true",
        help="Launch the jobs locally (and not in the batch system)" )
    parser.add_argument("--noscript", dest="noscript",  action="store_true",
        help="Does not put the automatic ./ in front of the executable" )
    parser.add_argument("-m", dest="mail", default = "", action="store_const", const = "-u "+os.environ["USER"]+"@cern.ch",
        help="When job finished sends a mail to USER@cern.ch" )
    parser.add_argument("-cpu", default=4000, dest="m_cpu", type=int,
        help="Memory per cpu (Slurm).")
    parser.add_argument("-time", default=20, dest="m_time", type=int,
        help="Maximum time of the job in hours (Slurm).")
    parser.add_argument("-exclude", default=0, dest="exclude", type=int,
        help="Number of nodes to exclude (Slurm).")
    parser.add_argument("-nodes2exclude", default=[], dest="nodes2exclude", type=str,
        help="Nodes to exclude (Slurm).", nargs="+")
    parser.add_argument("-in", dest="infiles", default = "", help="Files to copy over")
    parser.add_argument("--express", dest="express",  action="store_true",
        help="Run the jobs on express queue line" )
    parser.add_argument("command", help="Command to launch")
    opts = parser.parse_args()
    

    main(opts)


