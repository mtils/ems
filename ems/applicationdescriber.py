# coding=UTF-8
'''
Created on 31.01.2010

@author: michi
'''
import types
class ApplicationDescriber:
    @staticmethod
    def getFriendlyName(identifier,value):
        if isinstance(identifier, types.StringType) or isinstance(identifier, types.UnicodeType):
            stringIdentifier = identifier
        else:
            stringIdentifier = "%s.%s" % (type(identifier).__module__,type(identifier).__name__)
        
        if stringIdentifier == 'application.ui.settings.Connection.Connection':
            if value == 'databasefile':
                return 'Datenbankdatei'
            if value == 'database':
                return 'Datenbank'
            if value == 'driverbackend':
                return 'Treibertyp'
            if value == 'hostname':
                return 'Serveradresse'
            if value == 'authtype':
                return 'Authentifizierung'
            if value == 'username':
                return 'Benutzername'
            if value == 'password':
                return 'Passwort'
            if value == 'odbc-msqlserver':
                return 'SQL Server (ODBC)'
            if value == 'odbc-msqlclient':
                return 'SQL Native CLient (ODBC)'
            if value == 'ntauth':
                return 'NT Authentifizierung'
            if value == 'sql':
                return 'SQL Authentifizierung'
            
        if stringIdentifier == 'db.adapter.backend':
            if value == 'mssql':
                return 'Microsoft SQL Server'
            if value == 'sqlite':
                return 'SQLITE Datenbank'
        return value