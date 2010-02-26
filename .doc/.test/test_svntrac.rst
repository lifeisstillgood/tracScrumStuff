=========================
Working with SVN and trac
=========================

Yes, I know Trac is supposed to have amazing SVN integration, and it does, 
its just that, well, I wanted more. 


Freeze_helper
=============

Designed to help migrate from an unstable trunk to an RC branch, but can do any branch in any direction, it supplies and runs the correct merge commands, for given tickets ::

   echo "### `date +%F%H%M` StartMerge: 4447 (22010,22004)" >> $LOGFILE
   svnmerge.py merge -r 22010,22004 | tee -a $LOGFILE

OK, the gathering data is quite useful.  I pull from svn log the ticket link (ie in the commit message the developer enters #1234) and then from trac I pull the ticket status' and combine the two to tell me which changesets need to be merged from where to where

