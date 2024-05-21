import time
import threading
import random
import copy
usage_lock=threading.Lock()
cur_num_lock=threading.Lock()
printlock=threading.Lock()
pointer_lock=threading.Lock()
def use():
    t=time.time()
    global usage
    #print(usage)
    with usage_lock:
        for i in range(len(usage)):
            temp=[]
            for j in usage[i][0]:
                if t-j<=30:
                    temp.append(j)
            usage[i][0]=temp
        temp=copy.deepcopy(usage)
    temp.sort(key=lambda x:len(x[0]))
    #with printlock:
        #print(temp)
    global pointer
    try:
        pointer
    except:
        with pointer_lock:
            pointer=[temp[_][1] for _ in range(int(pressrate*ipnum)+1)]
            return pointer[0]
    if not len(temp[0][0]):
        for i in range(len(temp)-1,-1,-1):
            if temp[i][1] in pointer:
                with pointer_lock:
                    pointer.remove(temp[i][1])
                break
        with pointer_lock:
            pointer.append(temp[0][1])
        return temp[0][1]
    else:
        with pointer_lock:
            ma=0
            for i in pointer:
                with usage_lock:
                    if not usage[i][0]:
                        return i
                    if t-usage[i][0][-1]>ma:
                        ma=t-usage[i][0][-1]
                        th=i
            return th
def work():
    global usage,curnum
    node=use()
    #with printlock:
        #print(node)
    t = time.time()
    with usage_lock:
        usage[node][0].append(t)
    t=random.randint(1,5)
    time.sleep(t)
    with cur_num_lock:
        curnum-=1

def virt():
    t=time.time()
    gap=resttime/((1-pressrate)*ipnum)
    for i in range(int((1-pressrate)*ipnum)-1):
        usage[i][0]=[t-gap*i]

global ipnum,askdelay,resttime,pressrate,threadnum,usage,tot,curnum

ipnum=30
askdelay=3
resttime=30
pressrate=0.3
threadnum=30
tot=[0 for i in range(ipnum)]
usage=[[[],i] for i in range(ipnum)]
curnum=0
virt()
while 1:
    with cur_num_lock:
        cur=curnum
    while cur>threadnum:
        time.sleep(0.1)
        with cur_num_lock:
            cur=curnum
    with cur_num_lock:
        curnum+=1
    thread=threading.Thread(target=work)
    thread.start()
    global pointer
    with pointer_lock:
        ma=-1
        for i in range(len(pointer)):
            with printlock:
                if pointer[i]<10:
                    print('',pointer[i],end=' ')
                else:
                    print(pointer[i],end=' ')
        print()
        for i in range(len(pointer)):
            with usage_lock:
                with printlock:
                    if len(usage[pointer[i]][0])<10:
                        print('',len(usage[pointer[i]][0]),end=' ')
                    else:
                        print(len(usage[pointer[i]][0]),end=' ')
        print()
        print()
                #print(i,':',len(usage[i][0]),usage[i][0][-1] if len(usage[i][0]) else '')
            #print('\n\n')
