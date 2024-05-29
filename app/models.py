import hashlib, base64

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