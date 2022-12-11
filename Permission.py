READ = 4
WRITE = 2
EXEC = 1


class Permission:
    def __init__(self, dirname: str, username: str, time: str, type: str, cur: int, group: int, other: int):
        self.dirname = dirname
        # READ | WRITE | EXEC
        self.permission_cur = cur
        self.permission_group = group
        self.permission_other = other
        self.username = username
        self.time = time
        # self.next = -1
        # -:文件，d:目录
        self.type = type
