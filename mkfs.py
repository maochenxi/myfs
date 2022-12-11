from DirNode import DirNode
from Permission import Permission
from UserManager import UserManager
from myfs import *

import pickle
from datetime import *

BLOCK_SIZE = 1 * 1024
def init():
    # 初始化文件系统的开头，1作为开头和结尾，中间都是0
    f = open('./Node', 'wb')
    f.write(b'\x01')
    for i in range(0, 20*1024-2):
        f.write(b'\x00')
    f.write(b'\x01')

def edit_block(start,data):
    with open("./Node","rb") as f:
        pre = f.read(start)
        f.seek(start+BLOCK_SIZE)
        last = f.read()
    with open('./Node','wb') as f:
        f.write(pre)
        f.write(data)
        f.write(last)


def init_root():
    # 初始化根目录的DirNode类
    rootDirName = '/'
    rootUserName = 'root'
    # 时间类型转为字符串类型
    initRootTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rootDirNode = DirNode(rootDirName)
    rootDirNode.permission = Permission(rootDirName, rootUserName, initRootTime, 'd', 7, 4, 4,"root")
    edit_block(BLOCK_SIZE, b'\x01'+pickle.dumps(rootDirNode).ljust(BLOCK_SIZE-1,b'\x00'))

    # user_dict = {}
    # rootUser = UserManager(rootUserName, '111')
    # user_dict[rootUserName] = rootUser
    # edit_block(2*BLOCK_SIZE, b'\x01'+pickle.dumps(user_dict))

if __name__=='__main__':
    init()
    init_root()
# with open('./Node', 'ab+') as f:
#     f.seek(BLOCK_SIZE+1)
#     res = f.read(BLOCK_SIZE-1)
#     # print(res)
#     res = res.rstrip(b'\x00')
#     print(pickle.loads(res))
#     f.read(1)
#     print(pickle.loads(f.read(BLOCK_SIZE - 1)))
