from random import randint
import math

def rotation_left(x, num):
    # 循环左移
    num %= 32
    left = (x << num) % (2 ** 32)
    right = (x >> (32 - num)) % (2 ** 32)
    result = left ^ right
    return result

def Int2Bin(x, k):
    x = str(bin(x)[2:])
    result = "0" * (k - len(x)) + x
    return result

class SM3:

    def __init__(self):
        # 常量初始化
        self.IV = [0x7380166F, 0x4914B2B9, 0x172442D7, 0xDA8A0600, 0xA96F30BC, 0x163138AA, 0xE38DEE4D, 0xB0FB0E4E]
        self.T = [0x79cc4519, 0x7a879d8a]
        self.maxu32 = 2 ** 32
        self.w1 = [0] * 68
        self.w2 = [0] * 64

    def ff(self, x, y, z, j):
        # 布尔函数FF
        result = 0
        if j < 16:
            result = x ^ y ^ z
        elif j >= 16:
            result = (x & y) | (x & z) | (y & z)
        return result

    def gg(self, x, y, z, j):
        # 布尔函数GG
        result = 0
        if j < 16:
            result = x ^ y ^ z
        elif j >= 16:
            result = (x & y) | (~x & z)
        return result

    def p(self, x, mode):
        result = 0
        # 置换函数P
        # 输入参数X的长度为32bit(=1个字)
        # 输入参数mode共两种取值：0和1
        if mode == 0:
            result = x ^ rotation_left(x, 9) ^ rotation_left(x, 17)
        elif mode == 1:
            result = x ^ rotation_left(x, 15) ^ rotation_left(x, 23)
        return result

    def sm3_fill(self, msg):
        length = len(msg)   
        l = length * 8     

        num = length // 64
        remain_byte = length % 64
        msg_remain_bin = ""
        msg_new_bytes = bytearray((num + 1) * 64)  ##填充后的消息长度，单位：byte

        # 将原数据存储至msg_new_bytes中
        for i in range(length):
            msg_new_bytes[i] = msg[i]

        # remain部分以二进制字符串形式存储
        remain_bit = remain_byte * 8     #单位：bit
        for i in range(remain_byte):
            msg_remain_bin += "{:08b}".format(msg[num * 64 + i])

        k = (448 - l - 1) % 512
        while k < 0:
            # k为满足 l + k + 1 = 448 % 512 的最小非负整数
            k += 512

        msg_remain_bin += "1" + "0" * k + Int2Bin(l, 64)

        for i in range(0, 64 - remain_byte):
            str = msg_remain_bin[i * 8 + remain_bit: (i + 1) * 8 + remain_bit]
            temp = length + i
            msg_new_bytes[temp] = int(str, 2) #将2进制字符串按byte为组转换为整数
        return msg_new_bytes

    def sm3_msg_extend(self, msg):
        # 扩展函数: 将512bit的数据msg扩展为132个字
        for i in range(0, 16):
            self.w1[i] = int.from_bytes(msg[i * 4:(i + 1) * 4], byteorder="big")

        for i in range(16, 68):
            self.w1[i] = self.p(self.w1[i-16] ^ self.w1[i-9] ^ rotation_left(self.w1[i-3], 15), 1) ^ rotation_left(self.w1[i-13], 7) ^ self.w1[i-6]

        for i in range(64):
            self.w2[i] = self.w1[i] ^ self.w1[i+4]



    def sm3_compress(self,msg):
        # 压缩函数

        self.sm3_msg_extend(msg)
        ss1 = 0

        A = self.IV[0]
        B = self.IV[1]
        C = self.IV[2]
        D = self.IV[3]
        E = self.IV[4]
        F = self.IV[5]
        G = self.IV[6]
        H = self.IV[7]

        for j in range(64):
            if j < 16:
                ss1 = rotation_left((rotation_left(A, 12) + E + rotation_left(self.T[0], j)) % self.maxu32, 7)
            elif j >= 16:
                ss1 = rotation_left((rotation_left(A, 12) + E + rotation_left(self.T[1], j)) % self.maxu32, 7)
            ss2 = ss1 ^ rotation_left(A, 12)
            tt1 = (self.ff(A, B, C, j) + D + ss2 + self.w2[j]) % self.maxu32
            tt2 = (self.gg(E, F, G, j) + H + ss1 + self.w1[j]) % self.maxu32
            D = C
            C = rotation_left(B, 9)
            B = A
            A = tt1
            H = G
            G = rotation_left(F, 19)
            F = E
            E = self.p(tt2, 0)

            # 测试IV的压缩中间值
            # print("j= %d：" % j, hex(A)[2:], hex(B)[2:], hex(C)[2:], hex(D)[2:], hex(E)[2:], hex(F)[2:], hex(G)[2:], hex(H)[2:])

        self.IV[0] ^= A
        self.IV[1] ^= B
        self.IV[2] ^= C
        self.IV[3] ^= D
        self.IV[4] ^= E
        self.IV[5] ^= F
        self.IV[6] ^= G
        self.IV[7] ^= H

    def sm3_update(self, msg):
        # 迭代函数
        msg_new = self.sm3_fill(msg)   # msg_new经过填充后一定是512的整数倍
        n = len(msg_new) // 64         # n是整数，n>=1

        for i in range(0, n):
            self.sm3_compress(msg_new[i * 64:(i + 1) * 64])

    def sm3_final(self):
        digest_str = ""
        for i in range(len(self.IV)):
            digest_str += hex(self.IV[i])[2:]

        return digest_str.upper()

    def hashFile(self, filename):
        with open(filename,'rb') as fp:
            contents = fp.read()
            self.sm3_update(bytearray(contents))
        return self.sm3_final()

def sm3h(data):
    if __name__ == "__main__":
        msg1 = bytearray(data.encode('utf-8'))
        test1 = SM3()
        test1.sm3_update(msg1)
        digest1 = test1.sm3_final()
        return digest1

def gcd(a,b):#求最大公因子
        while a!=0:
            a,b = b%a,a
        return b
    
def findM(a,m):#扩展欧几里得算法求模逆
    u1,u2,u3 = 1,0,a
    v1,v2,v3 = 0,1,m
    while v3!=0:
        q = u3//v3
        v1,v2,v3,u1,u2,u3 = (u1-q*v1),(u2-q*v2),(u3-q*v3),v1,v2,v3
    return u1%m

def addo(x1,y1,x2,y2,a,p):#椭圆曲线上的点的加法运算
    if x1==x2 and y1==p-y2:#当两个点互逆时返回False
        return False
    if x1!=x2:#当两个非互逆的不同点相加时的lamda值
        lamda=((y2-y1)*findM(x2-x1,p))%p
    else:
        lamda=(((3*x1*x1+a)%p)*findM(2*y1,p))%p#当两个相同点相加时的lamda值
    x3=(lamda*lamda-x1-x2)%p#根据公式计算x3,y3值
    y3=(lamda*(x1-x3)-y1)%p
    return x3,y3

def mpoint(x,y,k,a,p):#椭圆曲线上的倍点运算
    k=bin(k)[2:]
    m,n=x,y
    for i in range(1,len(k)):#代入addo函数循环两两相加
        m,n=addo(m, n, m, n, a, p)
        if k[i]=='1':
            m,n=addo(m, n, x, y, a, p)
    return m,n

def kdf(z,klen):#点到字符串的转换
    ct=1
    k=''
    for _ in range(math.ceil(klen/256)):
        k=k+sm3h(hex(int(z+'{:032b}'.format(ct),2))[2:])
        ct=ct+1
    k='0'*((256-(len(bin(int(k,16))[2:])%256))%256)+bin(int(k,16))[2:]
    return k[:klen]

p=0x8542D69E4C044F18E8B92435BF6FF7DE457283915C45517D722EDB8B08F1DFC3
a=0x787968B4FA32C3FD2417842E73BBFEFF2F3C848B6831D7E0EC65228B3937E498
b=0x63E4C6D3B23B0C849CF84241484BFE48F61D59A5B16BA06E6E12D1DA27C5249A
gx=0x421DEBD61B62EAB6746434EBC3CC315E32220B3BADD50BDC4C4E6C147FEDD43D
gy=0x0680512BCBB42C07D47349D2153B70C4E5D7FDFCBFA36EA1A85841B9E46E09A2
n=0x8542D69E4C044F18E8B92435BF6FF7DD297720630485628D5AE74EE7C32E79B7
dB=0x1649AB77A00637BD5E2EFE283FBF353534AA7F7CB89463F208DDBC2920BB0DA0
xB=0x435B39CCA8F3B508C1488AFC67BE491A0F7BA07E581A0E4849A5CF70628A7E0A
yB=0x75DDBA78F15FEECB4C7895E2C1CDF5FE01DEBB2CDBADF45399CCF77BBA076A42
dB=randint(1,n-1)
xB,yB=mpoint(gx,gy,dB,a,p)


def encrypt(m:str):#加密
    plen=len(hex(p)[2:])
    m='0'*((4-(len(bin(int(m.encode().hex(),16))[2:])%4))%4)+bin(int(m.encode().hex(),16))[2:]
    klen=len(m)
    while True:
        k=randint(1, n)#产生随机数
        while k==dB:
            k=randint(1, n)
        x2,y2=mpoint(xB, yB, k, a, p)#计算椭圆曲线点
        x2,y2='{:0256b}'.format(x2),'{:0256b}'.format(y2)
        t=kdf(x2+y2, klen)
        if int(t,2)!=0:#当t不是全0时跳出循环
            break
    x1,y1=mpoint(gx, gy, k, a, p)
    x1,y1=(plen-len(hex(x1)[2:]))*'0'+hex(x1)[2:],(plen-len(hex(y1)[2:]))*'0'+hex(y1)[2:]
    c1='04'+x1+y1
    c2=((klen//4)-len(hex(int(m,2)^int(t,2))[2:]))*'0'+hex(int(m,2)^int(t,2))[2:]
    c3=sm3h(hex(int(x2+m+y2,2))[2:])
    return c1,c2,c3


data='0x656E6372797074696F6E207374616E674616E646172646E207374616E64617264'
print(data)
c1,c2,c3=encrypt(data)
c=(c1+c2+c3).upper()
print('\nciphertext:')
for i in range(len(c)):
    print(c[i*8:(i+1)*8],end=' ')
