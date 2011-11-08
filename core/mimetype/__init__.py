
import mimetypes


mimeTypeNames = {
                 'application/vnd.ms-excel':'Excel Datei',
                 'application/excel': "Excel Datei",
                 'application/x-excel': "Excel Datei",
                 'application/x-msexcel': "Excel Datei",
                 'text/x-comma-separated-values': 'CSV Datei',
                 'text/csv': 'CSV Datei',
                 'text/xml': 'XML Datei',
                 'application/x-dbase': 'dBASE Datei',
                 'application/dbase': 'dBASE Datei',
                 'application/dbf': 'dBASE Datei',
                 'application/x-dbf': 'dBASE Datei',
                 'zz-application/zz-winassoc-dbf': 'dBASE Datei'
                 }

class MimeType(object):
    '''
    classdocs
    '''

    def __init__(self,identifier,suffixes=None):
        '''
        Constructor
        '''
        self.identifier = identifier
        if suffixes is None:
            self.__suffixes = []
        else:
            self.__suffixes = suffixes

    def setMediaType(self,type):
        if type in ('text','image','video','audio','application','multipart','message','model','example'):
            self.__mediaType = type
            return
        raise TypeError("MediaType %s is not known" % type)
    
    def getMediaType(self):
        return self.__mediaType
        pass
    
    def delMediaType(self):
        raise RuntimeError('You cannot delete the mediaType')
        pass

    mediaType = property(getMediaType, setMediaType, delMediaType, "mediaType's docstring")
    
    def setSubType(self,type):
        self.__subType = type
        pass
    
    def getSubType(self):
        return self.__subType
        pass
    
    def delSubType(self):
        raise RuntimeError('You cannot delete the subType')
    
    subType = property(getSubType, setSubType, delSubType, "subType's docstring")
    
    def setSuffixes(self,suffixes):
        self.__suffixes = suffixes
    
    def getSuffixes(self):
        return self.__suffixes
    
    def delSuffixes(self):
        self.__suffixes = []
        
    def addSuffix(self,suffix):
        self.__suffixes.append(suffix)
    
    suffixes = property(getSuffixes,setSuffixes,delSuffixes,'suffixes docstring')
    
    def getIdentifier(self):
        return "%s/%s" % (self.mediaType,self.subType)
    
    def setIdentifier(self,identifier):
        splittedId = identifier.split('/')
        self.setMediaType(splittedId[0])
        self.setSubType(splittedId[1])
        return
    
    def delIdentifier(self):
        raise RuntimeError('You cannot delete the identifier')
        return
    
    identifier = property(getIdentifier, setIdentifier,delIdentifier,"identifiers DocString");
    
    def __str__(self):
        return self.getIdentifier()

class MimeTypeDB(object):
    
    mimetypesByIdentifier = {}
    mimeTypesBySuffix = {}
    mimeTypesObject = None
    
    
    
    @staticmethod
    def get(identifier=None,suffix=None):
        if (identifier == None) and (suffix == None):
            raise SyntaxError("User either identifier or suffix, but not none of em")
        if not len(MimeTypeDB.mimeTypesBySuffix):
            MimeTypeDB.loadMimeTypes()
        if identifier:    
            return MimeTypeDB.mimetypesByIdentifier[identifier]
        if suffix:
            return MimeTypeDB.mimeTypesBySuffix[suffix]
        
    @staticmethod
    def loadMimeTypes():
        MimeTypes = MimeTypeDB.getMimeTypeObject()
        for infos in MimeTypes.types_map:
            for suffix in infos:
#                if isinstance(infos[suffix],str ):
#                    print "%s %s" % (suffix,infos[suffix])
#                    print type(infos[suffix])
                if not MimeTypeDB.mimetypesByIdentifier.has_key(infos[suffix]):
                    MimeTypeDB.mimetypesByIdentifier[infos[suffix]] = MimeType(infos[suffix])
                     
                MimeTypeDB.mimetypesByIdentifier[infos[suffix]].addSuffix(suffix)
                MimeTypeDB.mimeTypesBySuffix[suffix] = MimeTypeDB.mimetypesByIdentifier[infos[suffix]]
                    
#            print "%s" % suffix
#            print "%s %s" % (suffix, MimeTypes.types_map[suffix])
#            MimeTypeDB.mimetypesByIdentifier[]
            
    @staticmethod
    def getMimeTypeObject():
        if MimeTypeDB.mimeTypesObject == None:
            MimeTypeDB.mimeTypesObject = mimetypes.MimeTypes()
        return MimeTypeDB.mimeTypesObject