#!/bin/sh

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


 ###################
echo "### `date +%F%H%M` StartMerge: 4447 (22010,22004)" >> $LOGFILE
svnmerge.py merge -r 22010,22004 | tee -a $LOGFILE
wait_after_merge
echo moverctest \#4447 >> svnmerge-commit-message.txt
svn commit -F svnmerge-commit-message.txt
wait_after_ci

 ###################
echo "### `date +%F%H%M` StartMerge: 4658 (22006)" >> $LOGFILE
svnmerge.py merge -r 22006 | tee -a $LOGFILE
wait_after_merge
echo moverctest \#4658 >> svnmerge-commit-message.txt
svn commit -F svnmerge-commit-message.txt
wait_after_ci
