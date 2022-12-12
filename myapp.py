import os
import tempfile

from textual import log, events
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Header, Footer, Input, TreeNode, Tree, Label

from UserManager import *
# importing required libraries
import mysql.connector
dataBase = mysql.connector.connect(
                    host ="localhost",
                    user ="root",
                    passwd ="mcx",
                    database = "filesystem"
                )
class Name(Widget):
    """Generates a greeting."""
    who = reactive("")

    def render(self) -> str:
        return f"{self.who}"

def judge(per: int) -> str:
    if per==7:
        return 'rwx'
    elif per ==6:
        return 'rw-'
    elif per == 5:
        return 'r-x'
    elif per==4:
        return 'r--'
    elif per==2:
        return '-w-'
    elif per==1:
        return '--x'
        
class Session(App):
    CSS_PATH = "refresh01.css"
    # input line
    input = Input(value='$ ')
    uname = Input(placeholder="username")
    pwd = Input(placeholder="pwd")
    comp = Vertical(uname, pwd, Name())
    # status and infomartion
    login = False  # if login
    username = None
    password = None
    group = None
    shell = ''  # shell name
    # User Class for Filesystem
    user = None

    # input.
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Container(self.comp, id="sh")

    def on_input_changed(self, event: input.Changed):
        self.shell = self.input.value
        # log("input shell is ", self.shell)

    def _on_key(self, event: events.Key) -> None:
        log(self.SCREENS)
        if event.key == 'enter':
            if not self.login:
                #db
                print(dataBase)
                cursorObject = dataBase.cursor()
                # query = "SELECT username, password,group FROM user where username = "+self.uname.value
                cursorObject.execute('''SELECT * FROM user where username = %s''',(self.uname.value,))
  
                # table created
                # cursorObject.execute(query)
                myresult = cursorObject.fetchall()
                self.username = self.uname.value
                pw = self.pwd.value
                self.password = myresult[0][1]
                if(pw == self.password):
                    print("密码正确，登录成功！")
                else:
                    self.pwd.value = ''
                self.group = myresult[0][2]
                # Todo select password from database
                if self.password != pw:
                    self.query_one(Name).who = "密码错误"
                else:
                    self.login = True
                    self.query_one("#sh").remove()
                    self.comp.remove()
                    self.mount(self.input)
                    self.input.styles.dock = "bottom"
                    self.user = UserManager(self.username, self.password, self.group)
                    dataBase.close()
            else:
                self.shell = self.shell[2:]
                if self.shell.strip(' ') == 'ls':
                    # res = self.user.Ls_File()
                    try:
                        tree = self.query_one("Tree")
                        tree.remove()
                    except:
                        pass
                    node = Tree(label="dir", data=None)
                    node.auto_expand=True
                    def construct_tree(node:TreeNode,dir:int):
                        res = self.user.Ls_File(dir)
                        for i, k in res.items():
                            j = read(k).permission
                            cur = node.add(f'{i} {j.username} {j.group} {j.time} {judge(j.permission_group)} {judge(j.permission_group)} {judge(j.permission_other)}',allow_expand=j.type=='d',expand=True)
                            if j.type=='d':
                                construct_tree(cur,k)
                    self.mount(node)
                    construct_tree(node.root,self.user.Node)
                    node.expand=True
                elif self.shell.startswith('edit'):
                    filename = self.shell.strip().split(' ')[-1]
                    self.user.Edit_file(filename)

                elif self.shell.startswith('cat'):
                    data = self.user.cat(self.shell.strip().split(' ')[-1])
                    self.mount(Label(data))

                elif self.shell.startswith('rm'):
                    # pass
                    self.user.Remove(self.shell.strip().split(' ')[-1])

                elif self.shell.startswith('rename'):
                    if len(self.shell.strip().split(' '))==3:
                        self.user.Rename(self.shell.strip().split(' ')[-2],self.shell.strip().split(' ')[-1])

                elif self.shell.startswith('mkdir'):
                    if len(self.shell.split(' ')) == 2:
                        self.user.Create_Dir(self.shell.split(' ')[-1])

                elif self.shell.startswith('touch'):
                    if len(self.shell.split(' ')) == 2:
                        self.user.Create_Dir(self.shell.split(' ')[-1],type='-')

                elif self.shell.startswith('cd'):
                    l = self.shell.split(' ')
                    if len(l) == 2:
                        self.user.Change_Dir(l[-1])
                    elif len(l) == 1:
                        self.user.Change_Dir('')
                # 修改文件拥有者、用户组或other的权限 chmod filename cur/group/other permission
                elif self.shell.startswith('chmod'):
                    if len(self.shell.split(' ')) == 4:
                        self.user.chmod(self.shell.split(' ')[-3],self.shell.split(' ')[-2],self.shell.split(' ')[-1])
                # 修改文件的用户组 chgrp filename usergroup
                elif self.shell.startswith('chgrp'):
                    if len(self.shell.split(' ')) == 3:
                        self.user.chgrp(self.shell.split(' ')[-2],self.shell.split(' ')[-1])

                # 修改该文件所属的用户 chown filename username  
                elif self.shell.startswith('chown'):
                    if len(self.shell.split(' ')) == 3:
                        self.user.chown(self.shell.split(' ')[-2],self.shell.split(' ')[-1])

                self.input.value = '$ '


if __name__ == "__main__":
    app = Session()
    app.run()
