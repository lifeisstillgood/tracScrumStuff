#!/usr/local/bin/python
#! -*- coding: utf-8 -*-

"""
Tools to handle subversion in sam during transition

Author: pbrian



svnmerge is a bit simpler now I understand what it does
It keeps a record of the changesets merged into a branch at each revision by
using the svn property called svnmerge-integrated


Minimum viable product:
- able to take two branches, that have been managed with svnmerge, and a ticketing system that puts 
  ticket ids, and help manage a release branch - tell you what changesets should go in based in ticket status
  and what tickets are partially uploaded.

process

- take two branches, get the map of ticket: [changeset] for both
- for the release branch (under svnmerge) get the changesets that were applied from trunk (or another branch)
- explain what tickets were merged in (fully or partially)
- and given a start changeset, need a timeline of logins and so timeline of checkins to the release branch.
  that is harder...No.  Timeline of fixes to trunk is OK - 

- determine which changesets should come in given a ticket.


capabilities
------------
I should be able to gather these automatically
 <trunkbranchLogFile> <rcbranchLogFile> <svnmerge-integratedlogfile> 



use cases
---------


- WHat changesets have been added to RC branch.

  ::

    svnhelper.py <trunkbranchLogFile> <rcbranchLogFile> <svnmerge-integratedlogfile> 

- what tickets are assoc with those changesets
- given a changeset, what has been added, since and what tickets have been added as well
- given a ticket, what changesets are needed,
- given a ticket has it been applied
- given a file, what is the latest changeset in RC.

issues
------
- partial ticket commits (ie adding some changesets assoc with a ticket)
- orphan changesets (no ticket id)
- order of applying to branch.



I want to be able to identify which changesets have been added to which
branch, to tell which tkts have which changesets, and so given a tkt, know 
which changesets need to be extracted, turned into patches and then applied to testing / RC branches


Questions
---------
- Which patches have been applied to a branch
  Discover from grep log file for [xxx] 

- which tkts were fixed using those patches
  from trunk can tell which tkt had which changesets
  

- 
time cd branches/rc/1; svn log > /tmp/log_from_rc1; cd ../../trunk; svn log > /tmp/log_from_rc1


- get from trac dbase the list of tickets that are ready to go live
- get from svn log the list of tkts matched up to changesets
- apply those change sets to last good release

- test one ticket 
- move on.
- there needs to be co-ordination between dimitry / me



DataStructures
--------------
tkt_checkin : a dict that looks like {123: [12345,6789],
              

logParser : parse the svnlog





"""

import re
import subprocess

###
import subprocess
import os



class MikadoSVNMergeError(Exception):
    ''' '''
    pass

class MikadoCmdLineError(Exception):
    ''' '''
    pass

###

class SvnLibError(Exception):
    ''' '''
    pass

class SvnLogMsg(object):
    ''' '''
    def __init__(self, rev, msg):
        self.rev = int(rev)
        self.msg = msg

    def __repr__(self):
        firstline = self.msg.split("\n")[2]
        return "<%s:%s...>" % (self.rev, firstline[:10])

    @property
    def tracTickets(self):
        ''' Which tractickets are ref from this msg 

        >>> m = SvnLogMsg(1, "this is a test for trac ticket #1234 and ticket:5678")
        >>> m.tracTickets
        [1234, 5678]

        '''
        trac_ticket_list = [] 
        exprs = (re.compile('\#(\d+)'), re.compile('[Tt]icket:?(\d+)'))
        for regex in exprs:
            groups = regex.findall(self.msg)
            trac_ticket_list.extend([int(g) for g in groups])
        return trac_ticket_list
        

    @property
    def changesets(self):
        ''' Which SVN changesets are ref from this msg 

        >>> m = SvnLogMsg(1, "This is a test #1234 changeset [123456] [54321]")
        >>> m.changesets
        [123456, 54321]

        TODO - deal with [1234-1237] form

        '''
        regex = re.compile("\[(\d+)\]")
        groups = regex.findall(self.msg)
        return [int(g) for g in groups]

class ticket(object):
    def __init__(self, ticket_id):
        self.ticket_id = ticket_id
        self.known_changesets = []
        self.known_changesets_applied = []
        self.log_msgs = []
        self.tktstatus = 'unknown'
        self.tktcomponent = 'unknown'


    @property
    def ticket_applied(self):
        ''' '''
        if len(set(self.known_changesets)) - len(set(self.known_changesets_applied)) > 0: 
            return False
        else:
            return True
        
    @property
    def known_changesets_not_applied(self):
        '''returns a set -s hould it return a list '''
        x = set(self.known_changesets) - set(self.known_changesets_applied)
        return [i for i in x]

    def __repr__(self):
        if self.ticket_id:
            tid = int(self.ticket_id)
        else:
            tid = "None"
        s = "id:%s %s/%s chgsets, inRC:%s" % (tid, len(self.known_changesets_applied),
                                 len(self.known_changesets),
                                 self.ticket_applied)
        return s


##############
 
def logout(msg):
    f = open('foo.log','a')
    f.write(msg + "\n\n")
    f.close()

def get_svnmerge_msg(branch, rev=None):
    '''retrieve from a given branch, the svnmerge-integrated property for that rev

    cmd = svn propget -r 20864 svnmerge-integrated /root/samlearning.com/REPO/branches/rc/1

    process = subprocess.Popen(['python', 'test1.py'], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print process.communicate()

    >>> get_svnmerge_msg('/root/samlearning/REPO/branches/rc/1', 20702)
       
 
    branch is a full path to local svn repo working copy
    '''
    cmdlist = ['svn', 'propget', '-r', str(rev), 'svnmerge-integrated', branch]
    process = subprocess.Popen(cmdlist, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    o, e = process.communicate()

    return o


def svnmerge_integrated_parse(val):
    '''We can extract from a rev under svnmerge control a list like 
    /trunk:1-20413,20416-20424,20427...
    I want to expand that into an actual list of changesets.
    
    it tells us where on this branch, changesets came FROM

    >>> x = '/trunk:1-5,7-9,11'
    >>> svnmerge_integrated_parse(x)
    {'/trunk': [1, 2, 3, 4, 5, 7, 8, 9, 11]}

    '''
    out = {}
    ### I can get multiple lines for diff branches 
    branches = val.split("\n")
    branches = [b for b in branches if b != '']

    for branch in branches:
        full_list = []
        bname, chgsets = branch.split(":")
        for chgset in chgsets.split(","):
            if chgset.find("-") == -1:
                full_list.append(int(chgset))
            else:
                st, ed = chgset.split("-") 
                st = int(st); ed = int(ed)
                for i in range(st, ed+1):
                    full_list.append(i)
        out[bname] = full_list
    return out


def svn_log_fetch(branchPath, rev=0):
    """Given a full path to local branch, and a version number, retrieve the svnlog """
    ### set a range for revison.  Basically it is from 0:version, unless version is 0
    if rev == 0:
        cmdlist = ['svn', 'log', branchPath] # get everything
    else:
        cmdlist = ['svn', 'log', '-r', '0:%s' % str(rev), branchPath]

    ## TODO - extract this into some helper that also handles errors
    process = subprocess.Popen(cmdlist, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    o, e = process.communicate()    

    return o
    
 
def svn_log_parse(txt=None):
    '''Parse a svn log output 

    >>> x = """
    ... ------------------------------------------------------------------------
    ... r20663 | egosteva@intersog.com | 2009-11-19 11:35:58 +0000 (Thu, 19 Nov 2009) | 1 line
    ... 
    ... fix problem with not correct leaveDate data - see #3879
    ... ------------------------------------------------------------------------
    ... r20662 | gzhukovskiy@intersog.com | 2009-11-19 11:24:25 +0000 (Thu, 19 Nov 2009) | 1 line
    ... 
    ... a log message
    ... ------------------------------------------------------------------------"""
    >>> msgs = svn_log_parse('junk', x)
    >>> msgs[0].rev
    20663

'''
    msgs = []
    if not txt:
        raise SvnLibError("You need a log text to parse")

    #slightly horrible hack - needbetter regex
    regex = "-{36}\n(.*?)-{36}"
    r1 = re.compile(regex, re.DOTALL)
    matches = r1.findall(txt)
    for match in matches:
        log_msg_obj = extract_single_msg(match)
        msgs.append(log_msg_obj)

    return msgs

def extract_single_msg(msg):
    '''given a full single msg, parse it 


    >>> x = "r20663 | egosteva@intersog.com | 2009-11-19 11:35:58 +0000 (Thu, 19 Nov 2009) | 1 line"
    >>> extract_single_msg(x).rev
    20663

    '''
    regex = "^r(\d+) |"
    r1 = re.compile(regex)
    rev = r1.findall(msg)[0]
    logout("rev: " + rev)
    
    return SvnLogMsg(rev, msg)
        

def tkts_to_changesets(logmsgs):
    '''given a logmsgs list of objects extract tkts and changesets '''

    t2c = {}
    for lm in logmsgs:
        for tkt in lm.tracTickets:
            t2c.setdefault(tkt, []).append(lm.rev) #in this checkin, i checked in a #123
        if len(lm.tracTickets) == 0: # put changesets that have no ticket, into sep key
            t2c.setdefault(None, []).append(lm.rev)  
    return t2c


def log_to_tkts(logmsgs):
    '''given a logmsgs list of objects extract tkts and changesets '''

    t2c = {}
    t2c[None] = ticket(None)

    for lm in logmsgs:

        for tkt_id in lm.tracTickets:

            if tkt_id in t2c.keys():
                t2c[tkt_id].known_changesets.append(lm.rev)
                t2c[tkt_id].log_msgs.append(lm)

            else:
                tkt = ticket(tkt_id)
                tkt.known_changesets.append(lm.rev)
                tkt.log_msgs.append(lm)
                t2c[tkt_id] = tkt


        if len(lm.tracTickets) == 0: # put changesets that have no ticket, into sep key
            t2c[None].known_changesets.append(lm.rev)  
            t2c[None].log_msgs.append(lm)  


    return t2c


### Given a branch, and a version, what changesets have been applied?


### now get all applied changesets in rc1
### then for each appplied chgset look for a tkt in t2c
def rc_changesets_to_tkts(logfilepath, t2c, BRANCH_FROM_CHANGESET=0):
    '''

    This needs to be changed to use svn merge functionality
    
     '''
    logmsgs = svn_log_parse(logfilepath)

    all_applied_changesets = []
    for m in logmsgs:
        all_applied_changesets.extend(m.changesets)

    chgsets_sinceRCBranch = [chgset for chgset in all_applied_changesets if chgset > BRANCH_FROM_CHANGESET]
    s_all_applied_changesets = set(chgsets_sinceRCBranch)
    #now for each applied changeset, find a linked tkt
    appliedtkts = []
    for tkt in t2c:
        for changeset in t2c[tkt]:
            if changeset in s_all_applied_changesets:
                print "this changeset %s, indicates that tkt %s was applied" % (changeset, tkt) 
                appliedtkts.append(tkt)
    return (set(appliedtkts), s_all_applied_changesets)

def back_to_trunk(RCLogFile, BRANCH_FROM_CHANGESET=0):
    '''From RC log file, determine which changesets have #xxx so were directly checked in, so 
       need to be merged back to trunk. 
    
    It is probably a good idea to have a seperate tkt for each RC merge/stablisation.
    That way we can store all alterations to RC that were needed during merge to that tkt.

    BRANCH_FROM_CHANGESET = point at whcih the RC branch diverged.
    I do also want to do the last merge into ... I am starting to re-write svnmerge....

    '''
    t2c = tkts_to_changesets(RCLogFile)    
    merge_back = []
    for tkt in t2c:
        if tkt in (0, None): continue
        merge_back.extend(t2c[tkt])
    #send back chgsets as long as larger than the branch point
    return sorted([chgset for chgset in merge_back if chgset > BRANCH_FROM_CHANGESET])

###
def runcmd(cmdlist):
    '''given a cmd in list form, execute it in subprocess.Popen

    Designed for handling svnmerge issues '''

    print "Running ...", ' '.join(cmdlist)
    p = subprocess.Popen(cmdlist, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        output, err = p.communicate()
    except Exception, e:
        raise MikadoCmdLineError(str(e))

    if err:
        raise MikadoSVNMergeError(err)
    else:
        return output

def run_merge(sourcePath, destPath, changeset):
    '''Give a source (Trunk), a destination (RC Branch) and a revision number (ie a changeset)
   
    We do one changeset at a time, because it is easier - if we do 2 changesets at once, 
    if we suddenly have a conflict in file A and then another conflict in file A it is awkward
    (but not impossible)

    resolving:

    - log everything
    - in case of a merge (G) keep a universal diff and accept the merge (really a human MUST check it)
    - in case of a conflict (C), take the Right hand side (ie copy from trunk). 


    '''

    cmd = ['python', '/usr/local/bin/svnmerge.py', 'merge', '-r', '%s' % changeset, '--source', sourcePath, destPath]
    pwd = os.getcwd()

    successCI = ['svn', 'ci', destPath, '-F', os.path.join(pwd, 'svnmerge-commit-message.txt')]

    try:
        print "Running:", cmd
        output = runcmd(cmd)
        if output == '':
            print "No changes in this rev can be merged"
        else:
            #check if output has a Conflict
  
            print "Success ++++", output, "++++"
            print ' '.join(successCI)

    except MikadoSVNMergeError, e:
        print "WHoops - check for conflicts", e


if __name__ == '__main__':
    import doctest
    doctest.testmod()
