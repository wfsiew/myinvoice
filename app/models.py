import hashlib, base64

class DataManager:
    
    access_token = None
    access_token_pwc = None

class Document:
    
    def __init__(self, data):
        self.data = data
        
    @property
    def hashData(self):
        s = self.data.encode('utf-8')
        return hashlib.sha256(s).hexdigest()
    
    @property
    def b64Data(self):
        s = self.data.encode('utf-8')
        c = base64.b64encode(s)
        return c.decode('utf-8')
    
    def getDoc(self, inv: str):
        return {
            'format': 'XML',
            'document': self.b64Data,
            'documentHash': self.hashData,
            'codeNumber': f'codenum{inv}'
        }