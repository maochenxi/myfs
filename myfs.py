import pickle
from datetime import datetime
from pprint import pprint

from DirNode import DirNode
from Permission import Permission
# from mkfs import *
BLOCK_SIZE = 1 * 1024
nodes = []
free_nodes = []
count = 0
f = open('./Node', 'rb')

data = f.read(BLOCK_SIZE)
while data != b'':
    if data[0] == 0:
        free_nodes.append(count)
    else:
        nodes.append(data)
    data = f.read(BLOCK_SIZE)
    count += 1

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



def write(BLOCK_IDX, data):
    global free_nodes
    cur = BLOCK_IDX
    if len(data) <= BLOCK_SIZE - 4:
        edit_block(BLOCK_IDX * BLOCK_SIZE, b'\x01' + data.ljust(BLOCK_SIZE - 4, b'\x00') + b'\x00' * 3)
        return
    l = []
    d = []
    while len(data) > BLOCK_SIZE - 4:
        if len(free_nodes) == 0:
            raise NotEnoughSpace('not enough space to write')
        # nodes[cur] = b'\x01' + data[BLOCK_SIZE - 4].ljust(BLOCK_SIZE - 4, b'\x00') + free_nodes[0].to_bytes(3, 'little')
        l.append(cur)
        d.append(b'\x01' + data[:BLOCK_SIZE - 4].ljust(BLOCK_SIZE - 4, b'\x00') + free_nodes[0].to_bytes(3, 'little'))
        data = data[BLOCK_SIZE - 4:]
        cur = free_nodes[0]
        free_nodes = free_nodes[1:]
    if len(data)!=0:
        if len(free_nodes) == 0:
            raise NotEnoughSpace('not enough space to write')
        l.append(cur)
        d.append(b'\x01'+data.ljust(BLOCK_SIZE - 1, b'\x00'))
        free_nodes = free_nodes[1:]
    for i, j in zip(l, d):
        edit_block(BLOCK_SIZE * i, j)


def read(BLOCK_IDX) -> DirNode:
    data = b''
    with open('./Node', 'rb') as f:
        f.seek(BLOCK_IDX * BLOCK_SIZE)
        data += f.read(BLOCK_SIZE)[1:]
        while data[-3:] != b'\x00\x00\x00':
            point = data[-3:]
            data = data[:-3]
            f.seek(BLOCK_SIZE*int.from_bytes(point,'little'))
            data += f.read(BLOCK_SIZE)[1:]
    return pickle.loads(data.strip(b'\x00'))


def mkdir(user, dirname, BLOCK_IDX,type):
    global free_nodes
    if len(free_nodes) == 0:
        raise NotEnoughSpace('not enough space to write')
    # global free_nodes
    dirnode = read(BLOCK_IDX)
    # create dir node
    dir = DirNode(dirname)
    dir.permission = Permission(dirname, user, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), type, 7, 4, 4)
    # print(free_nodes[0], b'\x01' + pickle.dumps(dir).ljust(BLOCK_SIZE - 4, b'\x00') + b'\x00' * 3)
    write(free_nodes[0], pickle.dumps(dir))
    # update parent node
    # print(dir.__dict__)
    dirnode.dir_dict[dirname]=free_nodes[0]
    free_nodes = free_nodes[1:]
    # print(BLOCK_IDX, b'\x01' + pickle.dumps(dirnode).ljust(BLOCK_SIZE - 4, b'\x00') + b'\x00' * 3)
    # print(dirnode.__dict__)
    write(BLOCK_IDX, pickle.dumps(dirnode))


class NotEnoughSpace(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


if __name__ == '__main__':
    print(count)
    print(free_nodes[0])
    # mkdir('root', 'passwd', 1)
    pprint(read(3).__dict__)
    # pprint(read(2)['root'].__dict__)
