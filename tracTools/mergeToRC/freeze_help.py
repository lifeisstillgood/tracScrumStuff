#!/usr/local/bin/python


"""

usage:  python -i get_logs_as.py /tmp/svnlog.log


This is a QD version that needs to be made less Quick and less Dirty
It is intended to look at a Trunk and RC branch of SVN, and look at a bug tracker (Trac)
and determine

i) which changesets are applicable to a given ticket number
   (initially by looking for #1234 indicators in commit messages.
    I also want an ability to add a commit message that will tell me
    that a different commit belongs to a ticket ie Orphan:<changeset>:<ticketid>
    )

ii) identify the status of each ticket, and choose only those which are needed to be merged (readytoRC and also closed for mistakes?)

iii) output commands needed to merge (using svnmerge) 

iv) a seperate script? to merge control - ie run the commands, detect failures etc.



TODO

* orphan changeset handling



"""
import mikadoSvnLib as svnlib
import sys
import dblib
import pprint
import subprocess
import re

from mikadosoftware import log

import mikadoconfig as config


class MikadoSVNMergeError(Exception):
    ''' '''
    pass

class MikadoCmdLineError(Exception):
    ''' '''
    pass



def runcmd(cmdlist):
    '''given a cmd in list form, execute it in subprocess.Popen

    Designed for handling svnmerge issues '''

    p = subprocess.Popen(cmdlist, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        output, err = p.communicate()
    except Exception, e:
        raise MikadoCmdLineError(str(e))

    if err:
        raise MikadoSVNMergeError(err)
    else:
        return output


def get_current_revision(repo):
    """ 
    >>> get_current_revision(repo)
    1234

    """
    cmd = ["svn", "info", repo]

    o = runcmd(cmd)
    rx = re.compile("Revision: (\d*)")
    m = rx.search(o)
    return int(m.group(1))
    
def show_tickets(tktlist):
    ''' '''

    tktlist = [t for t in tktlist if t.ticket_id not in (0,None)]
    all_tkts = sorted([str(t.ticket_id) for t in tktlist])
    chgsets = []
    for t in tktlist:
        unapplied = set(t.known_changesets) - set(t.known_changesets_applied)
        chgsets.extend(unapplied)
    all_unapplied_chgsets = sorted(chgsets)


    print "We are looking at branch %s revision %s"

    print "There are %s tkts in this list, with %s unapplied changesets" % (len(all_tkts), len(all_unapplied_chgsets))


    
    print "++++++++ tkt ids:"
    print ", ".join(all_tkts)

    print "++++++++ all outstanding changesets:"
    print ", ".join([str(c) for c in all_unapplied_chgsets])

#    tmpl = "svnmerge.py merge -n -r %s -S /trunk" 
#    for c in chgsets:
#        print tmpl % c



if __name__ == '__main__':

    ### 

    mylog = log.getlogger("mikadosoftware.trac")    

    
#    trunk_repo = '/root/samlearning.com/REPO3/trunk'
#    rc_repo = '/root/samlearning.com/REPO3/branches/rc/2'

    trunk_repo = config.TRUNK_REPO
    rc_repo = config.RC_REPO

    local_trunk_rev = get_current_revision(trunk_repo)
    local_rc_rev = get_current_revision(rc_repo)

    rev = local_trunk_rev
    print "rev:", rev


    logtxt = svnlib.svn_log_fetch(trunk_repo, rev)
    logmsgs = svnlib.svn_log_parse(logtxt)
    print "logmsgs contains %s messages." % len(logmsgs)


    ##logs to tickets
    t2c = svnlib.log_to_tkts(logmsgs)
   
    ### changesets in trunk
    chgsets_in_trunk = []
    for t in t2c:
        chgsets_in_trunk.extend(t2c[t].known_changesets)
    

    ## changesets in rc
    changesets_applied_in_rc = svnlib.svnmerge_integrated_parse(
                                    svnlib.get_svnmerge_msg(rc_repo, rev=rev))

    print len(changesets_applied_in_rc['/trunk']), 'change sets applied in rc'

    ### mark in ticket if a chageset is applied
    for t in t2c:
        for chgset in t2c[t].known_changesets:
            if int(chgset) in changesets_applied_in_rc['/trunk']:
                t2c[t].known_changesets_applied.append(int(chgset))

    ## diff
    chgsets_waiting = set(chgsets_in_trunk) - set(changesets_applied_in_rc['/trunk'])

    ## which are in untested state.
    print 'getting status'
    conn = dblib.get_conn()
    SQL = """SELECT id, status, component FROM ticket; """ 

    cursor = conn.cursor()
    cursor.execute(SQL)
    rs = cursor.fetchall()

    for row in rs:
        dbid = int(row[0])
        dbstatus =  row[1]
        dbcomponent = row[2]
        if dbid in t2c.keys(): #if there is a tkt that has got a changeset. it could be a task
            t2c[dbid].tktstatus = dbstatus
            t2c[dbid].tktcomponent = dbcomponent
            


    print 'elimiate those applied' 
    haschgsets_waiting = []
    for t in t2c:
        if t2c[t].ticket_applied == False:
            haschgsets_waiting.append(t2c[t])
    
    
    tkts_go_live = []
    tkts_not_go_live = []
    orphan_tkts = []

    for tkt in haschgsets_waiting:
        if tkt.ticket_id in (0, None): 
            orphan_tkts.append(tkt)

        if tkt.tktstatus.lower() in ("readyforrc",):  #why closed - helps me spot if someone adds changeset to a closed ticket
            tkts_go_live.append(tkt)

        else:
            tkts_not_go_live.append(tkt)

#write something to spot orphan changesets ...



##########

    print "{{{"

    print "Branch: %s, those copied up from %s, from 0 to rev %s" % (rc_repo, trunk_repo, rev)
    print "total tkts:", len(t2c)
    print "tkts closed/tested/inapp but not applied ", len(tkts_go_live)
    print "tkts with chgset waitng, but not closed", len(tkts_not_go_live)
    orphan_chgsets = []
    orphan_chgsets.extend([o.known_changesets for o in orphan_tkts])
    print "Orphan changesets: ", len(orphan_chgsets)
 

    for t in tkts_go_live:
        print t.ticket_id, ":",  t.known_changesets_not_applied 

    print "}}}"
    tmpl = '''[[TicketQuery(id=%s&col=id&col=summary&col=priority&col=status, table)]]'''
    print tmpl % "|".join([str(t.ticket_id) for t in tkts_go_live])

    print "###################"
    

    fo = open("run_merge.sh", 'w')
    s = config.BASH_HEADER

    for t in tkts_go_live:

        chgsets_as_string = ','.join(
             [str(i) for i in t.known_changesets_not_applied])

        s += "\n ###################\n" 
        s += """echo "### `date +%%F%%H%%M` StartMerge: %s (%s)" >> $LOGFILE\n""" % ( 
              t.ticket_id, chgsets_as_string)
                           

        s +=  "svnmerge.py merge -r %s | tee -a $LOGFILE" % chgsets_as_string

        s += "\nwait_after_merge\n"

        s += """echo moverctest \#%s >> svnmerge-commit-message.txt
svn commit -F svnmerge-commit-message.txt""" % t.ticket_id

        s +=  "\nwait_after_ci\n"
        
    fo.write(s)
    fo.close()


#    conn = dblib.get_conn()
#    SQL = """SELECT id from ticket where status ; """ #
#
#    cursor = conn.cursor()
#    cursor.execute(SQL)
#    rs = cursor.fetchall()#

#    for row in rs:
                             
    #print 'em
#    print 'live' 
#    show_tickets(tkts_go_live)
#    print 'no live'
#    show_tickets(tkts_not_go_live)
#    print 'orphan'
#    show_tickets(orphan_tkts)
#    print 'orphan+live'
#    x = orphan_tkts.extend(tkts_go_live)
#    print len(x), "<<<<"
#    show_tickets(x)

  
