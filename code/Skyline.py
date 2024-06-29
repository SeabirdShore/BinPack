from greedypacker import skyline,item,guillotine
import sys
import math
import time
Nparam=10000 #根据不同的数据下限进行维护
S=skyline.Skyline(Nparam,sys.maxsize,heuristic='bottom_left') #尽量放在最左下角
#start=time.time()
with open ('test.txt','r') as file:
    n=int(file.readline())
    for _ in range(n):
        line = file.readline().strip()  #去掉换行符
        h,w = map(float,line.split())   #取出小矩形的高度和宽度
        h=math.ceil(Nparam*h)    #转成整型
        w=math.ceil(Nparam*w)   
        S.insert(item.Item(w,h))    #online算法
    optH=math.ceil(Nparam*float(file.readline()))#转成整型，10000是减小约去的误差
#end=time.time()

#print(optH)
#print(S.filledheight)
print(S.bin_stats)
a=(float)(S.filledheight)   #填充的高度
b=(float)(optH)      #最优的高度
print(a/b)
#print(1000*(end-start))
