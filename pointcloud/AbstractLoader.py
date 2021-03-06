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
from CommonOracle import Oracle

class Loader(Oracle):
    def __init__(self, configuration):
        Oracle.__init__(self, configuration)
        
    def createUser(self):
        """
        Configures a new database user and grants the required priviledges.
        """
        connectionSuper = self.getConnection(True)
        cursorSuper = connectionSuper.cursor()
        ora.createUser(cursorSuper, self.user, self.password, self.tableSpaceIOT, self.tempTableSpace)
        connectionSuper.close()
    
    def createLASDirectory(self, lasDirVariableName, parentFolder):
        """
        Creates a new Oracle directory by connecting to the superuser.
        """
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
    
    def sqlldr(self, tableName):
        """
        Generates the control file for the sqlldr and composes the sqlloader
        command.
        """
        controlFile = tableName + '.ctl'
        badFile = tableName + '.bad'
        logFile = tableName + '.log'
        
        ctfile = open(controlFile,'w')
        sqlldrCols = []
        for i in range(len(self.cols)):
            column = self.cols[i]
            if column not in general.DM_SQLLDR:
                raise Exception('Wrong column! ' + column)
#            sqlldrCols.append(self.getDBColumn(i)[0] + ' ' + general.DM_SQLLDR[column][0] + ' external(' + str(general.DM_SQLLDR[column][1]) + ')')
            sqlldrCols.append(self.getDBColumn(i)[0] + ' ' + general.DM_SQLLDR[column][0] + ' external')
            
        
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
        """
        Creates a empty flat table
        """
        ora.dropTable(cursor, tableName, True)

        ora.mogrifyExecute(cursor,"""
CREATE TABLE """ + tableName + """ (
""" + (',\n'.join(self.getHeapColumns())) + """) 
""" + ora.getTableSpaceString(tableSpace) + """ 
pctfree 0 nologging""")

    def createExternalTable(self, cursor, txtFiles, tableName, txtDirVariableName, numProcesses):
        """
        Creates an external table by accecssing the files in the specified directory.        
        """
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
""" + ora.getParallelString(numProcesses) + """ REJECT LIMIT 0""")     
        
    def createIOTTable(self, cursor, iotTableName, tableName, tableSpace, numProcesses):
        """
        Creates an Index-Organized-Table and populates it from the heap table data.
        """
        ora.dropTable(cursor, iotTableName, True)
        
        cls = [', '.join(i[0] for i in self.columns)]
                 
        ora.mogrifyExecute(cursor, """
CREATE TABLE """ + iotTableName + """
(""" + (', '.join(cls)) + """, 
    CONSTRAINT """ + iotTableName + """_PK PRIMARY KEY (""" + self.index + """))
    ORGANIZATION INDEX
    """ + ora.getTableSpaceString(tableSpace) + """
    PCTFREE 0 NOLOGGING
""" + ora.getParallelString(numProcesses) + """
    AS
        SELECT """ + (', '.join(self.heapCols())) + """ FROM """ + tableName)
        
    def addIOTUnionAll(self, cursor):
        """
        Inserting additional data to the table by UNIONing the current IOT with 
        the heap table.
        """
        temp_iot = self.iotTableName + '_2'
        ora.renameTable(cursor, self.iotTableName, temp_iot)
        ora.renameConstraint(cursor, temp_iot, self.iotTableName + '_PK', temp_iot + '_PK')
        ora.renameIndex(cursor, self.iotTableName + '_PK', temp_iot + '_PK')
        
        cls = [', '.join(i[0] for i in self.columns)]
              
        ora.mogrifyExecute(cursor, """
CREATE TABLE """ + self.iotTableName + """
(""" + (', '.join(cls)) + ", CONSTRAINT """ + self.iotTableName + "_PK PRIMARY KEY("+ self.index + """))
    ORGANIZATION INDEX""" + ora.getTableSpaceString(self.tableSpaceIOT) + """
    PCTFREE 0 NOLOGGING
    """ + ora.getParallelString(self.numProcesses) + """
    AS
        SELECT """ + (', '.join(self.heapCols())) + """ FROM """ + self.tableName + """
        UNION ALL
        SELECT """  + (', '.join(cls)) + ' FROM ' + temp_iot)

        ora.dropTable(cursor, temp_iot)

    def computeStatistics(self, cursor):
        """
        Gather optimiser statistics.
        """
        ora.computeStatistics(cursor, self.iotTableName, self.user)


    def extLoaderPrep(self, connection, configuration):
        """
        Prepare the data for the use of external tables.
        """
        cursor = connection.cursor()

        if self.init or self.reload:
            ora.createMetaTable(cursor, self.metaTable, True)

        command = """python -m pointcloud.mortonConverter {0}""".format(configuration)
        os.system(command)
        self.createExternalTable(cursor, '*.txt', self.tableName, self.ORCLdirectory, self.numProcesses)
    
    def extLoaderLoading(self, connection):
        """
        Load the data using External Tables.
        """
        cursor = connection.cursor()
        if self.init or self.reload:
            self.createIOTTable(cursor, self.iotTableName, self.tableName, self.tableSpaceIOT, self.numProcesses)
        else:
            ora.appendData(connection, cursor, self.iotTableName, self.tableName)
        ora.dropTable(cursor, self.tableName, check = False)
    
    def sqlldrPrep(self, connection, configuration):
        """
        Initialise the sqlldr loading procedure. Load data into the heap table.
        """
        cursor = connection.cursor()
        
        self.createFlatTable(cursor, self.tableName, self.tableSpaceHeap)
        if self.init or self.reload:
            ora.createMetaTable(cursor, self.metaTable, True)

        commnandsqlldr = self.sqlldr(self.tableName)
        command = """python -m pointcloud.mortonConverter {0} | """.format(configuration) + commnandsqlldr
        
        os.system(command)
        
    def sqlldrLoading(self, connection):
        """
        Create the IOT or update according to the specified update method (dump, 
        union, resort)"""
        cursor = connection.cursor()
        if self.init or self.reload:
            self.createIOTTable(cursor, self.iotTableName, self.tableName, self.tableSpaceIOT, self.numProcesses)
        else:
            if self.update == 'dump':
                ora.appendData(connection, cursor, self.iotTableName, self.tableName)
            elif self.update == 'union':
                self.addIOTUnionAll(cursor)
            elif self.update == 'resort':
                self.rebuildIOT(connection)
        ora.dropTable(cursor, self.tableName)
           
    def rebuildIOT(self, connection):
        """
        Rebuilt the index organised table by resorting the new and the old data.
        """
        cursor = connection.cursor()
        ora.appendData(connection, cursor, self.tableName, self.iotTableName)
        ora.dropTable(cursor, self.iotTableName, check = False)
        self.createIOTTable(cursor, self.iotTableName, self.tableName, self.tableSpaceIOT, self.numProcesses)

    def sizeIOT(self):
        """
        Returns the size of table in MB and the number of rows present in the database.
        """
        connection = self.getConnection()
        cursor = connection.cursor()
        size_total = ora.getSizeTable(cursor, self.iotTableName + '_pk')    
        number_total = ora.getNumPoints(connection, cursor, self.iotTableName)
        connection.close()
        return size_total, number_total
        
    def reloadPrep(self):
        connection = self.getConnection()
        cursor = connection.cursor()
        
        cursor.execute('SELECT table_name FROM all_tables WHERE table_name = :1',[(self.iotTableName).upper(),])
        length = len(cursor.fetchall())
        if length:
            cursor.execute('DROP TABLE {0} PURGE'.format((self.iotTableName).upper()))
        
        cursor.execute('SELECT table_name FROM all_tables WHERE table_name = :1',[(self.metaTable).upper(),])
        length = len(cursor.fetchall())
        if length:
            cursor.execute('DROP TABLE {0} PURGE'.format((self.metaTable).upper()))
         