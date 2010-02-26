


### simple config files - as python!!!


TRUNK_REPO = '/root/samlearning.com/REPO3/trunk'
RC_REPO = '/root/samlearning.com/REPO3/branches/rc/2'

BASH_HEADER="""#!/bin/sh

wait_after_ci()
{
echo Did Commit work? Y to cont, all other fail:
read instr
case $instr in

 y|Y)
 echo Running Next merge ...
 ;;

 *)
 echo Ending...
 exit 1
 ;;
esac
}

wait_after_merge()
{
echo Did Merge work? Y to cont, all other fail:
read instr
case $instr in 

 y|Y)
 echo Proceeding to check in ...
 ;; 

 *)
 echo Ending...
 exit 1
 ;;
esac
}

LOGFILE=/tmp/merge.log

"""
