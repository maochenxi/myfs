READ = 4
WRITE = 2
EXEC = 1


class Permission:
    def __init__(self, dirname: str, username: str, time: str, type: str, cur: int, group_per: int, other: int, group: int):
        self.dirname = dirname
        # READ | WRITE | EXEC:1 2 3 4 5 6 7
        self.permission_cur = cur
        self.permission_group = group_per
        self.permission_other = other
        self.group = group
        self.username = username
        self.time = time
        # self.next = -1
        # -:文件，d:目录
        self.type = type
