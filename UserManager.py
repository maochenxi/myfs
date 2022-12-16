import os
import tempfile

from myfs import *
from typing import List, Tuple, Dict

BLOCK_SIZE = 1*1024


class UserManager:
    def __init__(self, username, password,group):
        self.user_group_dict = {}
        self.username = username
        self.group = group
        self.password = password
        self.cwd = '/'
        # 用户当前所处目录的块地址
        self.Node = 1

    # 移动文件到其他目录
    def copy(self,filename,dirname):
        cur = read(self.Node)
        next = cur.dir_dict[filename]
        data = read(next)
        if(not self.check(data.permission,1)):
            print("用户组没有写权限!")
            return ""
        c = read(1)
        dirsplitlist = dirname.split('/')
        for dir in dirsplitlist:
            # 要插入dir的块地址
            next = c.dir_dict[dir]
            # 要插入路径的DirNode结构图
            c= read(next)
        copyFiletoDir(self.username,self.group,data,c)


    # 复制文件到其他目录
    def copy(self,filename,dirname):
        cur = read(self.Node)
        next = cur.dir_dict[filename]
        data = read(next)
        if(not self.check(data.permission,1)):
            print("用户组没有写权限!")
            return ""
        c = read(1)
        dirsplitlist = dirname.split('/')
        for dir in dirsplitlist:
            # 要插入dir的块地址
            next = c.dir_dict[dir]
            # 要插入路径的DirNode结构图
            c= read(next)
        copyFiletoDir(self.username,self.group,data,c)
        self.Remove(filename)
        
    
    # 修改文件的权限
    def chmod(self,filename,type,permission):
        cur = read(self.Node)
        next = cur.dir_dict[filename]
        data = read(next)
        if(not(self.username==data.permission.username or self.username == 'root')):
            print("没有权限修改")
            pass
        if(not self.check(data.permission,1)):
            print("用户组没有写权限!")
            return ""
        if(type=="cur"):
            data.permission.permission_cur = permission
        elif(type=="group"):
            data.permission.permission_group = permission
        else:
            data.permission.permission_other = int(permission)
        write(next,pickle.dumps(data))

    # 修改文件用户组
    def chgrp(self,filename,group):
        cur = read(self.Node)
        next = cur.dir_dict[filename]
        data = read(next)
        if(not(self.username==data.permission.username or self.username == 'root')):
            print("没有权限修改")
            pass
        if(not self.check(data.permission,1)):
            print("用户组没有写权限!")
            return ""
        data.permission.group = group
        write(next,pickle.dumps(data))

    # 修改文件所属的用户
    def chown(self,filename,username):
        
        cur = read(self.Node)
        next = cur.dir_dict[filename]
        data = read(next)
        if(not(self.username==data.permission.username or self.username == 'root')):
            print("没有权限修改")
            pass
        if(not self.check(data.permission,1)):
            print("用户组没有写权限!")
            return ""
        data.permission.username = username
        write(next,pickle.dumps(data))

    def Remove(self, filename):
        # 获得当前目录的块地址，然后读入目录信息
        cur = read(self.Node)
        # pprint(cur.__dict__)
        # print(cur.dir_dict[filename])
        # next是要remove的文件或目录的首块地址
        # try:
        next = cur.dir_dict[filename]
        data = read(next)
        if(not self.check(data.permission,1)):
            print("用户组没有写权限!")
            return ""
        # except:
        #     return
        # 获取所有存储该目录或文件的所有块地址，并删除该文件或目录
        removeDirNode(next)
        del cur.dir_dict[filename]
        write(self.Node,pickle.dumps(cur))


    def Edit_file(self, filename):
        cur = read(self.Node)
        try:
            next = cur.dir_dict[filename]
        except:
            return
        # next是文件的地址
        #Todo 先判断是否有锁，有写锁就打开失败
        # 实现读写互斥、写写互斥
        data = read(next)
        if(not self.check(data.permission,1)):
            print("用户组没有写权限!")
            return ""
        if(data.lock_write==1):
            print("有其他用户在写，写写互斥，写入失败！")
            return ""
        #Todo 先上写锁，然后写入，再开始下面操作
        # 没有用户在读写，可以进行写入操作，写入之前先上锁
        data.lock_write = 1
        write(next, pickle.dumps(data))

        
        tmp = tempfile.mktemp()
        with open(tmp, "w") as f:
            f.write(data.content)
        # print(tmp)
        os.system(f"alacritty  -e nvim {tmp}")
        with open(tmp, "r") as f:
            print(f.read())
            f.seek(0)
            data.content = f.read()
        print(data.content)
        data.lock_write=0
        write(next, pickle.dumps(data))
        os.remove(tmp)

    def Rename(self, src: str, dst: str):
        cur = read(self.Node)
        try:
            next = cur.dir_dict[src]
        except:
            return
        data = read(next)
        if(not self.check(data.permission,1)):
            print("用户组没有写权限!")
            return ""
        del cur.dir_dict[src]
        cur.dir_dict[dst] = next
        write(self.Node,pickle.dumps(cur))
        
        data.dirname = dst
        write(next,pickle.dumps(data))

    def Create_Dir(self, dir, type='d'):
        '''只支持当前目录下创建'''
        mkdir(self.username, dir, self.Node, type,self.group)

    def Ls_File(self, node: int) -> Dict[str, int]:
        list_file = read(node)
        files = list_file.dir_dict
        # permissions = [read(list_file.dir_dict[i]).permission for i in files]
        return files

    def Change_Dir(self, dir: str) -> str:
        print("cur cwd is",self.cwd)
        print("cur Node is",self.Node)
        #Todo 完成上一级目录指针 dir_list['..] = idx
        # 空的路径回到根目录
        if dir == '':
            self.cwd = '/'
            self.Node = 1
            return 0
            #return self.cwd
        # assert len(dir)>0
        # /结尾，把 / 去掉
        if dir.endswith('/') and len(dir) > 1:
            dir = dir[:-1]
        # 如果以..开头，就是返回上一级目录
        if(dir.startswith('..')):
            cur_node = read(self.Node)
            self.Node = cur_node.prevdir
            print("pre node is ",self.Node)
            x = self.cwd.split('/')
            self.cwd = '/'+'/'.join(x[:-1])
            if(dir=='../' or dir == '..'):
                return 0
            dir = dir[3:]
        if dir=='':
            return 0
        # 以 / 开头，如果只有/，就是回到根目录，如果不仅有/，就一层一层进入到达指定路径
        if dir.startswith('/'):
            if dir != '/':
                dirlist = dir.split('/')[1:]
                cur_node = 1
                # next_node = None
                for i in dirlist:
                    cur_node = read(cur_node)
                    # print(cur_node.dir_dict)
                    cur_node = cur_node.dir_dict[i]
                self.Node = cur_node
                self.cwd = dir
                #return self.cwd
            else:
                self.Node = 1
                self.cwd = '/'
                #return self.cwd
        else:
            dirlist = dir.split('/')
            cur_node = self.Node
            # next_node = None
            for i in dirlist:
                cur_node = read(cur_node)
                cur_node = cur_node.dir_dict[i]
            self.Node = cur_node
            if self.cwd!='/':
                self.cwd = self.cwd + '/' + dir
            else:
                self.cwd = self.cwd+dir
        

    def cat(self, filename: str):
        #判断是否有读写互斥锁
        cur = read(self.Node)
        try:
            next = cur.dir_dict[filename]
        except:
            return
        data = read(next)
        # 判断是否有读的权限
        if(not self.check(data.permission,0)):
            print("用户组没有读权限!")
            return ""
        if(data.lock_write==1):
            print("有其他用户在写，读写互斥，读取失败！")
            return ""
        return data.content

    def check(self,permission: Permission,wr):
        if(self.username=='root'):
            return 1
        if(permission.username == self.username):
            per = permission.permission_cur
            #print(per)
        elif(permission.group==self.group):
            per = permission.permission_group
        else:
            per = permission.permission_other
        # 如果是写操作
        if(wr==1):
            if(per in [2,3,6,7]):
                return 1
            else:
                return 0
        elif(wr==0):
            if(per in [4,5,6,7]):
                return 1
            else:
                return 0
        else:
            if(per in [1,3,5,7]):
                return 1
            else:
                return 0