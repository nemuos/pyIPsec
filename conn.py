class connection(dict):
    def __init__(self, name):
        self.name = name
        self.data = {}
    
    def __setitem__(self, key, item):
        self.data[key] = item

    def __getitem__(self, key):
        return self.data[key]

    def __delitem__(self, key):
        self.data.pop(key, None)

    def __str__(self):
        desc = 'conn : %s\n' % self.name
        desc = desc + str(self.data)
        return desc
