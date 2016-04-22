# -*- coding: utf-8 -*-
"""
Created on Mon Feb 8 10:13:05 2016

@author: Stella Psomadaki

Adapted from: https://github.com/NLeSC/pointcloud-benchmark/blob/master/python/pointcloud/oracle/AbstractLoader.py
Author: Oscar Martinez Rubi
Apache License
Version 2.0, January 2004
"""

import pointcloud.general as general
import pointcloud.oracleTools as ora
import os
import numpy as np
from CommonOracle import Oracle

class Loader(Oracle):
    def __init__(self, configuration):
        Oracle.__init__(self, configuration)

    def createUser(self):
        """Configures a new database user and grants the required priviledges."""
        connectionSuper = self.getConnection(True)
        cursorSuper = connectionSuper.cursor()
        ora.createUser(cursorSuper, self.user, self.password, self.tableSpace, self.tempTableSpace)
        connectionSuper.close()
    
    def createLASDirectory(self, lasDirVariableName, parentFolder):
        """Creates a new Oracle directory by connecting to the superuser."""
        connectionSuper = self.getConnection(True)
        cursorSuper = connectionSuper.cursor()
        ora.createDirectory(cursorSuper, lasDirVariableName, parentFolder, self.userName)
        connectionSuper.close()
    
    def getHeapColumns(self):
        heapCols = []
        for i in range(len(self.cols)):
            heapCols.append(self.getDBColumn(i)[0] + ' ' + general.DM_FLAT[self.cols[i]])
        return heapCols
    
    def heapCols(self):
        heapCols = []
        for i in range(len(self.cols)):
            heapCols.append(self.getDBColumn(i)[0])
        return heapCols
        
    def getTableSpaceString(self, tableSpace):
        if tableSpace != None and tableSpace != '':
            return " TABLESPACE " + tableSpace + " "
        else: 
            return ""
    
    def sqlldr(self, tableName):
        commonFile = 'loader'
        controlFile = commonFile + '.ctl'
        badFile = commonFile + '.bad'
        logFile = commonFile + '.log'
        
        ctfile = open(controlFile,'w')
        sqlldrCols = []
        for i in range(len(self.cols)):
            column = self.cols[i]
            if column not in general.DM_SQLLDR:
                raise Exception('Wrong column! ' + column)
            sqlldrCols.append(self.getDBColumn(i)[0] + ' ' + general.DM_SQLLDR[column][0] + ' external(' + str(general.DM_SQLLDR[column][1]) + ')')
        
        ctfile.write("""load data
append into table """ + tableName + """
fields terminated by ','
(
""" + (',\n'.join(sqlldrCols)) + """
)""")
        
        ctfile.close()
        sqlLoaderCommand = "sqlldr " + self.getConnectString() + " direct=true control=" + controlFile + ' data=\\"-\\" bad=' + badFile + " log=" + logFile
        return sqlLoaderCommand
        
    def createFlatTable(self, cursor, tableName, tableSpace):
        """ Creates a empty flat table"""
        ora.dropTable(cursor, tableName, True)
        
        ora.mogrifyExecute(cursor,"""
CREATE TABLE """ + tableName + """ (""" + (',\n'.join(self.getHeapColumns())) + """) """ + self.getTableSpaceString(tableSpace) + """ pctfree 0 nologging""")

    def createExternalTable(self, cursor, txtFiles, tableName, txtDirVariableName, numProcesses):
        ora.dropTable(cursor, tableName, True)
        ora.mogrifyExecute(cursor, """
CREATE TABLE """ + tableName + """ (""" + (',\n'.join(self.getHeapColumns())) + """)
ORGANIZATION EXTERNAL
(
TYPE oracle_loader
DEFAULT DIRECTORY """ + txtDirVariableName + """
ACCESS PARAMETERS (
    RECORDS DELIMITED BY NEWLINE
    FIELDS TERMINATED BY ', ')
LOCATION ('""" + txtFiles + """')
)
""" + self.getParallelString(numProcesses) + """ REJECT LIMIT 0""")     
        
    def createIOTTable(self, cursor, iotTableName, tableName, tableSpace, numProcesses):
        """ Create Index-Organized-Table and populate it from tableName Table"""
        ora.dropTable(cursor, iotTableName, True)
        
        cls = [', '.join(i[0] for i in self.columns)]
        
        ora.mogrifyExecute(cursor, """
CREATE TABLE """ + iotTableName + """
(""" + (', '.join(cls)) + """, 
    CONSTRAINT """ + iotTableName + """_PK PRIMARY KEY (""" + self.index + """))
    ORGANIZATION INDEX""" + self.getTableSpaceString(tableSpace) + """
    PCTFREE 0 NOLOGGING
""" + self.getParallelString(numProcesses) + """
AS
    SELECT """ + (', '.join(self.heapCols())) + """ FROM """ + tableName)
    
    def addIOTUnionAll(self, cursor):
        temp_iot = self.iotTableName + '_2'
        ora.renameTable(cursor, self.iotTableName, temp_iot)
        ora.renameConstraint(cursor, temp_iot, self.iotTableName + '_PK', temp_iot + '_PK')
        ora.renameIndex(cursor, self.iotTableName + '_PK', temp_iot + '_PK')
        
        cls = [', '.join(i[0] for i in self.columns)]
        
        ora.mogrifyExecute(cursor, """
CREATE TABLE """ + self.iotTableName + """
(""" + (', '.join(cls)) + """, 
    CONSTRAINT """ + self.iotTableName + """_PK PRIMARY KEY (""" + self.index + """))
    ORGANIZATION INDEX""" + self.getTableSpaceString(self.tableSpace) + """
    PCTFREE 0 NOLOGGING
""" + self.getParallelString(self.numProcesses) + """AS
SELECT """ + (', '.join(self.heapCols())) + """ FROM """ + self.tableName + """
UNION ALL
SELECT """  + (', '.join(cls)) + ' FROM ' + temp_iot)

        ora.dropTable(cursor, temp_iot)

    def computeStatistics(self, cursor):
        ora.mogrifyExecute(cursor, "ANALYZE TABLE " + self.iotTableName + "  compute system statistics for table")
        ora.mogrifyExecute(cursor,"""
BEGIN
    dbms_stats.gather_table_stats('""" + self.user + """','""" + self.iotTableName + """',NULL,NULL,FALSE,'FOR ALL COLUMNS SIZE AUTO',8,'ALL');
END;""")


    def extLoaderPrep(self, connection, configuration):
        cursor = connection.cursor()

        if self.init:
            ora.createMetaTable(cursor, self.metaTable, True)

        command = """python -m pointcloud.mortonConverter {0}""".format(configuration)
        os.system(command)
        self.createExternalTable(cursor, '*.txt', self.tableName, self.ORCLdirectory, self.numProcesses)
    
    def extLoaderLoading(self, connection):
        cursor = connection.cursor()
        if self.init:
            self.createIOTTable(cursor, self.iotTableName, self.tableName, self.tableSpace, self.numProcesses)
        else:
            ora.appendData(connection, cursor, self.iotTableName, self.tableName)
        ora.dropTable(cursor, self.tableName, check = False)
    
    def sqlldrPrep(self, connection, configuration):
        cursor = connection.cursor()
        
        self.createFlatTable(cursor, self.tableName, self.tableSpace)
        if self.init:
            ora.createMetaTable(cursor, self.metaTable, True)

        commnandsqlldr = self.sqlldr(self.tableName)
        command = """python -m pointcloud.mortonConverter {0} | """.format(configuration) + commnandsqlldr
        os.system(command)
        
    def sqlldrLoading(self, connection):
        cursor = connection.cursor()
        if self.init:
            self.createIOTTable(cursor, self.iotTableName, self.tableName, self.tableSpace, self.numProcesses)
        else:
            if self.update == 'dump':
                ora.appendData(connection, cursor, self.iotTableName, self.tableName)
            elif self.update == 'union':
                self.addIOTUnionAll(cursor)
            elif self.update == 'resort':
                self.rebuildIOT(connection)
        ora.dropTable(cursor, self.tableName)
           
    def rebuildIOT(self, connection):
        cursor = connection.cursor()
        ora.appendData(connection, cursor, self.tableName, self.iotTableName)
        ora.dropTable(cursor, self.iotTableName, check = False)
        self.createIOTTable(cursor, self.iotTableName, self.tableName, self.tableSpace, self.numProcesses)

    def sizeIOT(self):
        connection = self.getConnection()
        cursor = connection.cursor()
        size_total = ora.getSizeTable(cursor, self.iotTableName)    
        number_total = ora.getNumPoints(connection, cursor, self.iotTableName)
        connection.close()
        return size_total, number_total
        
    def round2resolution(array, predicate):
        return np.round(array - np.mod(predicate + array, predicate), 0)