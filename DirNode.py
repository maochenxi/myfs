class DirNode:
    def __init__(self, dirname: str):
        self.dirname = dirname
        self.permission = None
        self.dir_dict = {}
        self.next = None
        self.length = 0
        self.lock_read = 0
        self.lock_write = 0
        self.content = ''
