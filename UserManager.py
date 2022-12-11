import os
import tempfile

from myfs import *
from typing import List, Tuple, Dict


class UserManager:
    def __init__(self, username, password):
        self.user_group_dict = {}
        self.username = username
        self.password = password
        self.cwd = '/'
        self.Node = 1

    def Remove(self, filename):
        pass

    def Edit_file(self, filename):
        #Todo 先判断是否有锁，有写锁就打开失败

        cur = read(self.Node)
        #Todo 先上写锁，然后写入，再开始下面操作
        cur.lock_read=1

        try:
            next = cur.dir_dict[filename]
        except:
            return
        data = read(next)
        tmp = tempfile.mktemp()
        with open(tmp, "w") as f:
            f.write(data.content)
        print(tmp)
        os.system(f"alacritty  -e nvim {tmp}")
        with open(tmp, "r") as f:
            print(f.read())
            f.seek(0)
            data.content = f.read()
        print(data.content)
        write(next, pickle.dumps(data))
        os.remove(tmp)

    def Rename(self, src: str, dst: str):
        cur = read(self.Node)
        try:
            next = cur.dir_dict[src]
        except:
            return
        del cur.dir_dict[src]
        cur.dir_dict[dst] = next
        write(self.Node,pickle.dumps(cur))
        data = read(next)
        data.dirname = dst
        write(next,pickle.dumps(data))

    def Create_Dir(self, dir, type='d'):
        '''只支持当前目录下创建'''
        print(dir)
        mkdir(self.username, dir, self.Node, type)

    def Ls_File(self, node: int) -> Dict[str, int]:
        list_file = read(node)
        files = list_file.dir_dict
        # permissions = [read(list_file.dir_dict[i]).permission for i in files]
        return files

    def Change_Dir(self, dir: str) -> str:
        if dir == '':
            self.cwd = '/'
            self.Node = 2
            return self.cwd
        # assert len(dir)>0
        if dir.endswith('/') and len(dir) > 1:
            dir = dir[:-1]
        if dir.startswith('/'):
            if dir != '/':
                dirlist = dir.split('/')[1:]
                cur_node = 1
                # next_node = None
                for i in dirlist:
                    cur_node = read(cur_node)
                    print(cur_node.dir_dict)
                    cur_node = cur_node.dir_dict[i]
                self.Node = cur_node
                self.cwd = dir
                return self.cwd
            else:
                self.Node = 1
                self.cwd = '/'
                return self.cwd
        else:
            dirlist = dir.split('/')
            cur_node = self.Node
            # next_node = None
            for i in dirlist:
                cur_node = read(cur_node)
                cur_node = cur_node.dir_dict[i]
            self.Node = cur_node
            self.cwd = self.cwd + '/' + dir

    def cat(self, filename: str):
        #判断是否有读写互斥锁
        cur = read(self.Node)
        try:
            next = cur.dir_dict[filename]
        except:
            return
        data = read(next)
        return data.content
