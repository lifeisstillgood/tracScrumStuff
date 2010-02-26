#!/usr/local/bin/python


"""
:author:

simple tools to try and improve mergeing with svnmerge

"""


#reviewing output

def parse_svn_output(output):
    ''' 

    >>> txt = """### 2010-02-011031 StartMerge: 3213 (21885,21934,21935,21936, 21947)
    ... property 'svnmerge-integrated' deleted from '.'.
    ... 
    ... --- Merging r21885 into '.':
    ... A    application/core/model/ImportDataRemoveQueuePeer.php
    ... A    application/core/model/map/ImportDataRemoveQueueMapBuilder.php
    ... A    application/core/model/om/BaseImportDataRemoveQueue.php
    ... U    application/core/model/om/BaseSchool.php
    ... A    application/core/model/om/BaseImportDataRemoveQueuePeer.php
    ... A    application/core/model/ImportDataRemoveQueue.php
    ... U    config/mysql/SamLearning-classmap.php.multidb
    ... U    config/mysql/SamLearning-classmap.php
    ... U    src/sql/install/snapshot_innodb_FK_delete_singleDB.sql
    ... U    src/sql/install/snapshot_innodb_FK_add_singleDB.sql
    ... U    src/sql/install/snapshot_innodb.sql
    ... U    src/sql/install/snapshot_innodb_FK_delete.sql
    ... U    src/sql/install/snapshot.sql
    ... U    src/sql/install/snapshot_innodb_singleDB.sql
    ... U    src/sql/install/snapshot_innodb_FK_add.sql
    ... A    src/sql/versions/2010-01-26_12_00_00-dataCenter-Added_student_import_data_remove_queue_table.sql
    ... 
    ... --- Merging r21934 through r21936 into '.':
    ... U    application/platform/controller/DocumentController.php
    ... U    application/core/model/ImportDataRemoveQueuePeer.php
    ... U    application/core/model/ImportDataRemoveQueue.php
    ... U    application/core/system/ImportData.php
    ... G    application/core/system/Util.php
    ... A    bin/platform/cleanupUploadedStudentDataFiles.php
    ... U    bin/platform/startImportPersonData.php
    ... 
    ... --- Merging r21947 into '.':
    ... G    application/platform/controller/DocumentController.php
    ... 
    ... property 'svnmerge-integrated' set on '.'
    >>> pass  
 
    '''

    pass
