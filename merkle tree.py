import hashlib
import random


class treenode:#节点
    def __init__(self,hashd,l=None,r=None,h=0):
        self.hashd=hashd#哈希值
        self.l=l#左子节点和右子节点
        self.r=r
        self.h=h#树的高度

        
def hash(sign,string):#计算哈希值
    temp=sign+string
    out = hashlib.sha256(temp.encode("utf-8")).hexdigest()
    return out
        

def calc(lst):#将数据转换为哈希值列表
    temp=[]
    for i in range(len(lst)):
        temp.append(treenode(hash("0x00",lst[i])))
    return temp


def rhigh(n):#求树的高度
    temp=1
    i=0
    while 1:
        if n<=temp:
            return i
        temp=temp*2
        i=i+1


def tree(lst):#计算完全树
    temp=[]
    if len(lst)==1:#只有一个叶子节点时，直接将此节点作为根节点
        return lst[0]
    for i in range(0,len(lst),2):
        temp.append(treenode(hash("0x01",lst[i].hashd+lst[i+1].hashd),lst[i],lst[i+1],lst[i].h+1))
    return tree(temp)

        
    
def creattree(lst,standard,h=1):#构建树
    temp=[]
    n=len(lst)
    if len(lst)==1:#列表中只有一个节点时，此节点为根节点，并返回根节点
        return lst[0]
    for i in range(0,(2*n-2**standard),2):#计算最下一层叶子节点的父节点
        temp.append(treenode(hash("0x01",lst[i].hashd+lst[i+1].hashd),lst[i],lst[i+1],h))
    for i in range((2*n-2**standard),n):#不在最下一层的叶子节点直接存入列表
        temp.append(lst[i])
    return tree(temp)


def path(root, x):#审计路径
    lst=[]
    temp= root
    a= root.h- 1
    while a>= 0:#高度为小于0时停止向下访问子节点
        if x<= 2**a:#判断当前数据位置在左子节点
            lst.append(temp.r.hashd)#储存在审计路径另一方向节点的hash值
            lst.append(0)#储存审计路径的方向
            temp=temp.l
            a=temp.h- 1
        else:#判断当前数据位置在右子节点
            x=x-2**a
            lst.append(temp.l.hashd)
            lst.append(1)
            temp=temp.r
            a=temp.h- 1
    return lst


def exchange(data,pdata,j):#确定数据的级联顺序
    if j==0:
        temp=data+pdata
    if j==1:
        temp=pdata+data
    return temp


def audit(root,x,data):#审计
    lst=[]
    lst=path(root,x)#得到数据的审计路径
    lst.reverse()#将列表逆序
    hashdata=hash("0x00",data)
    for i in range(0,len(lst),2):#计算根节点哈希值
        hashdata=hash("0x01",exchange(hashdata,lst[i+1],lst[i]))
    if hashdata==root.hashd:
        print("此数据包含在内")
    else:
        print("此数据不包含在内")
        
    

data=[]
for i in range(0,100000):
    data.append(str(random.randint(0,10000000000)))
l=calc(data)
standard=rhigh(len(l))
root=creattree(l,standard,1)
print(root.hashd)
x=random.randint(0,100000)
audit(root,x+1,data[x])#随机选取一个数据
audit(root,x+1,str(random.randint(0,10000000000)))#从数据列表中取出数据




    
