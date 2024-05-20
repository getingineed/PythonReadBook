import threading
import time
import urllib.request
import re
import os
import random
import requests
import dateutil.parser
from urllib.parse import quote

#signal_file_lock=threading.Lock()
clash_op_lock=threading.Lock()
usage_dic_lock=threading.Lock()
print_lock=threading.Lock()
signal_lock=threading.Lock()

class Proxying_by_Clash:
    def __init__(self,limit='all'):
        self.renew_api()
        self.limit=limit
        #supported limit modes:
            #'all': no limit
            #'in' : china mainland (HK,TW excluded)
            #'ex' : exterals (mainland excluded)
            #'as' : Asia
            #'eu' : Europe
            #'am' : Emerica
            #'af' : Africa
            #'ru' : Russia
            #'me' : Mid East
            #'au' : Australia

        # thread control signals: (4 mode supported)
        self.limited_fastest_TCS = 0
        self.time_first_TCS=0
        self.proxies=self.get_proxies()
        self.current_node=self.proxies['proxies']['GLOBAL']['now']
        #  0 : not a thread
        #  1 : thread working signal
        # -1 : thread terminating signal
        #  2 : thread pausing signal(don't change node)

    def get_proxies(self):
        return requests.get(f'{self.api}/proxies').json()

    def ip_information(self):
        response = requests.get('http://ip-api.com/json/')
        return response.json()
    def renew_api(self):
        with open(r'C:\Users\minran.DESKTOP-UOFUVTU\.config\clash\config.yaml','r') as f:
            a=f.read()
        a=a.split('\n')
        sign=0
        for i in a:
            if 'external-controller' in i:
                print('Initializing clash port number successfully:',i.split(':')[-1])
                self.api='http://localhost:'+i.split(':')[-1]
                sign=1
                break
        if not sign:
            print('Failed to renew clash api port number!\nUsing default...')
            self.api='http://localhost:9090'

    def change_proxy(self,group, new_proxy):
        data = {'name': new_proxy}
        try:
            requests.put(f'{self.api}/proxies/{group}', json=data)
            self.current_node=new_proxy
        except:
            print('节点切换失败！（'+self.current_node+'->'+new_proxy+'）')

    def filter_limit(self,limit=0):
        if not limit:
            limit='all'
        ins=['DIRECT','CN-上海游戏节点','CN-浙江BGP','CN-安徽联通','CN-河南移动','CN-江苏BGP','CN-宿迁BGP','CN-浙江BGP(443端口)',
             'CN-江苏BGP(443端口)','CN-宿迁BGP(443端口)','CN-安徽联通(443端口)','CN-河南移动(443端口)','CN-安徽 500m','CN-河南1G']
        exs=['TW 1G 家宽/Netflix','TW 1G(443端口) 家宽/Netflix','HK 5G','HK 5G(443端口)','JP 5G','GER Frankfurt 5G',
             '广日隧道-春川 5x', '广港隧道-香港 A 5x', '广港隧道-香港 B 5x', '广港隧道-台湾 5x', '广新隧道-新加坡 5x',
             '广港隧道-孟买 5x', '广日隧道-首尔 5x', '辽日隧道-墨西哥 5x', '辽德隧道-法兰克福 5x', '辽德隧道-迪拜 5x',
             '辽德隧道-英国 5x', '辽日隧道-美国阿什本 5x', '辽日隧道-美国芝加哥 5x','Singapore4G/Netflix', 'JP500m/Netflix',
             'UK 4G/Netflix', 'US Chicago 4G/Netflix', 'US Ashburn 4G/Netflix', 'Dubai 4G/Netflix', 'Korea 500m/Netflix',
             'Korea Chunchuan 4G/Netflix', 'Korea Seoul  4G/Netflix', 'Mexico 4G/Netflix', 'Mumbai 4G/Netflix','日本1 [3×]'
             , '日本2 [3×]', '韩国1 [3×]', '韩国2 [3×]', '香港01', '香港02', '新加坡2 [3×]', '香港03', '香港04 [2×]',
             '香港05  [3×]', '新加坡1 [3×]','IN1|0.1|导航|https://new.dc.cyou','US3|0.5|官网|https://dash.cutecloud.cc',
             'KR1|1.0|群组|https://t.me/urebest','KR2|1.0|频道|https://t.me/cutecloudch','BR1|0.1|请惠存上述联系方式避免失联~',
             'IN2|0.1|倍率:标准x0.1~1|中转x1.5|专线x3','US1|0.5|节点有倍率，请注意倍率提示~','US2|0.5|若有问题请于官网发起工单~',
             'BR2|0.1|推荐使用CuteCloud或萌云加速器~','US4|0.5|全职/兼职代理限时招募中~','TR.土耳其.A | 中转','AS.亚洲.TEST | 直连.V2',
             'JP.日本.A | 中转', 'JP.日本.B | 中转', 'JP.日本.C | 中转', 'JP.日本.X | 专线', 'JP.日本.Z | 专线', 'JP.东京.A | 中转',
             'JP.东京.B | 中转', 'JP.东京.C | 中转', 'JP.东京.X | 专线', 'JP.东京.Y | 专线', 'HK.香港.A | 中转', 'HK.香港.B | 中转',
             'HK.香港.C | 中转', 'HK.香港.X | 专线', 'KR.韩国.A | 中转', 'KR.韩国.B | 中转', 'KR.韩国.C | 中转', 'KR.韩国.X | 专线',
             'KR.韩国.Z | 专线', 'SG.新加坡.A | 中转', 'SG.新加坡.B | 中转', 'SG.新加坡.C | 中转', 'SG.新加坡.X | 专线',
             'SG.新加坡.Z | 专线', 'TW.台湾.A | 中转', 'IN.印度.A | 中转', 'IN.印度.B | 中转', 'IN.印度.X | 专线', 'IN.印度.Z | 专线',
             'MY.马来西亚.X | 专线', 'US.美国.A | 中转', 'US.美国.B | 中转', 'US.美国.C | 专线', 'US.美国.X | 专线.VA',
             'US.美国.Y | 专线.VA', 'US.美国.Z | 专线.VA', 'DE.德国.A | 中转', 'DE.德国.X | 专线', 'DE.德国.Z | 专线',
             'UK.英国.A | 中转', 'UK.英国.B | 中转', 'UK.英国.Z | 专线', 'AE.阿联酋.A | 中转', 'AE.阿联酋.X | 专线',
             'AU.澳洲.A | 中转', 'AU.澳洲.X | 专线', 'BR.巴西.A | 中转', 'BR.巴西.X | 专线', 'CL.智利.A | 中转',
             'CL.智利.Y | 专线', 'FR.法国.A | 中转', 'FR.法国.X | 专线', 'IT.意大利.A | 中转', 'IT.意大利.Z | 专线',
             'MX.墨西哥.A | 中转', 'MX.墨西哥.X | 专线', 'NL.荷兰.X | 专线', 'SA.沙特.A | 中转', 'SA.沙特.X | 专线',
             'UAE.迪拜.A | 中转', 'UAE.迪拜.Z | 专线', 'ZA.南非.A | 中转', 'RU.俄罗斯.A | 中转', 'TR.土耳其.A | 中转']
        ass=['TW 1G 家宽/Netflix','TW 1G(443端口) 家宽/Netflix','HK 5G','HK 5G(443端口)','JP 5G','广日隧道-春川 5x',
             '广港隧道-香港 A 5x', '广港隧道-香港 B 5x', '广港隧道-台湾 5x', '广新隧道-新加坡 5x', '广港隧道-孟买 5x',
             '广日隧道-首尔 5x','Singapore4G/Netflix', 'JP500m/Netflix','Korea 500m/Netflix','Korea Chunchuan 4G/Netflix',
             'Korea Seoul  4G/Netflix', 'Mumbai 4G/Netflix','日本1 [3×]', '日本2 [3×]', '韩国1 [3×]', '韩国2 [3×]', '香港01',
             '香港02', '新加坡2 [3×]', '香港03', '香港04 [2×]', '香港05  [3×]', '新加坡1 [3×]','IN1|0.1|导航|https://new.dc.cyou',
             'KR1|1.0|群组|https://t.me/urebest','KR2|1.0|频道|https://t.me/cutecloudch','IN2|0.1|倍率:标准x0.1~1|中转x1.5|专线x3',
             'AS.亚洲.TEST | 直连.V2', 'JP.日本.A | 中转', 'JP.日本.B | 中转', 'JP.日本.C | 中转', 'JP.日本.X | 专线', 'JP.日本.Z | 专线',
             'JP.东京.A | 中转', 'JP.东京.B | 中转', 'JP.东京.C | 中转', 'JP.东京.X | 专线', 'JP.东京.Y | 专线', 'HK.香港.A | 中转',
             'HK.香港.B | 中转', 'HK.香港.C | 中转', 'HK.香港.X | 专线', 'KR.韩国.A | 中转', 'KR.韩国.B | 中转', 'KR.韩国.C | 中转',
             'KR.韩国.X | 专线', 'KR.韩国.Z | 专线', 'SG.新加坡.A | 中转', 'SG.新加坡.B | 中转', 'SG.新加坡.C | 中转',
             'SG.新加坡.X | 专线', 'SG.新加坡.Z | 专线', 'TW.台湾.A | 中转', 'IN.印度.A | 中转', 'IN.印度.B | 中转',
             'IN.印度.X | 专线', 'IN.印度.Z | 专线', 'MY.马来西亚.X | 专线']
        eus=['GER Frankfurt 5G','辽德隧道-法兰克福 5x','辽德隧道-英国 5x','UK 4G/Netflix', '英国01','BR1|0.1|请惠存上述联系方式避免失联~',
             'BR2|0.1|推荐使用CuteCloud或萌云加速器~','DE.德国.A | 中转', 'DE.德国.X | 专线', 'DE.德国.Z | 专线',
             'UK.英国.A | 中转', 'UK.英国.B | 中转', 'UK.英国.Z | 专线','FR.法国.A | 中转', 'FR.法国.X | 专线', 'IT.意大利.A | 中转',
             'IT.意大利.Z | 专线','NL.荷兰.X | 专线']
        ams=['辽日隧道-美国阿什本 5x','辽日隧道-美国芝加哥 5x','辽日隧道-墨西哥 5x','US Chicago 4G/Netflix','US Ashburn 4G/Netflix'
             ,'美国1', '美国2','US3|0.5|官网|https://dash.cutecloud.cc','US1|0.5|节点有倍率，请注意倍率提示~',
             'US2|0.5|若有问题请于官网发起工单~','US4|0.5|全职/兼职代理限时招募中~','US.美国.A | 中转', 'US.美国.B | 中转',
             'US.美国.C | 专线', 'US.美国.X | 专线.VA', 'US.美国.Y | 专线.VA', 'US.美国.Z | 专线.VA','BR.巴西.A | 中转',
             'BR.巴西.X | 专线', 'CL.智利.A | 中转', 'CL.智利.Y | 专线','MX.墨西哥.A | 中转', 'MX.墨西哥.X | 专线']
        mes=[ 'AE.阿联酋.A | 中转', 'AE.阿联酋.X | 专线','SA.沙特.A | 中转', 'SA.沙特.X | 专线', 'UAE.迪拜.A | 中转', 'UAE.迪拜.Z | 专线']
        aus=['AU.澳洲.A | 中转', 'AU.澳洲.X | 专线']
        afs=['ZA.南非.A | 中转']
        rus=['RU.俄罗斯.A | 中转']
        self.proxies=self.get_proxies()
        names = self.proxies['proxies']['GLOBAL']['all']
        filtered = []
        if limit=='all':
            for i in names:
                if i in ins or i in exs:
                    filtered.append(i)
        if limit=='in':
            for i in names:
                if i in ins:
                    filtered.append(i)
        if limit=='as':
            for i in names:
                if i in ass:
                    filtered.append(i)
        if limit=='ex':
            for i in names:
                if i in exs:
                    filtered.append(i)
        if limit=='am':
            for i in names:
                if i in ams:
                    filtered.append(i)
        if limit=='eu':
            for i in names:
                if i in eus:
                    filtered.append(i)
        if limit=='ru':
            for i in names:
                if i in rus:
                    filtered.append(i)
        if limit=='me':
            for i in names:
                if i in mes:
                    filtered.append(i)
        if limit=='au':
            for i in names:
                if i in aus:
                    filtered.append(i)
        if limit=='af':
            for i in names:
                if i in afs:
                    filtered.append(i)
        return filtered

    def change_one_by_use(self,strategy='average focus',limit=0):
        global usage_dic,rest_time
        if not limit:
            limit=self.limit
        nodes=self.filter_limit(limit)
        availables=[]
        proxs=self.proxies['proxies']
        for i in range(len(nodes)):
            delays=proxs[nodes[i]]['history']
            for j in range(len(delays)):
                delays[j]['time']=dateutil.parser.isoparse(delays[j]['time'])
            delays.sort(key=lambda x:x['time'])
            if delays and delays[-1]['delay']!=0:
                usage=usage_dic.get(nodes[i],[])
                t=time.time()
                usage_in_1min=[]
                for j in usage:
                    if t-j<rest_time:
                        usage_in_1min.append(j)
                with usage_dic_lock:
                    usage_dic[nodes[i]]=usage_in_1min
                availables.append([nodes[i],delays[-1]['delay'],len(usage_in_1min)])#[(名称，最近时延，1分钟内使用次数),...]
        availables.sort(key=lambda x:(x[2],x[1]))
        if strategy=='average focus':
            self.change_proxy('GLOBAL',availables[0][0])
        if strategy=='someone survive':
            dense_discriminate=3
            survive_percent=0.3
            stressed_percent=0.4
            index1=int(len(availables)*survive_percent)
            index2=len(availables)-int(len(availables)*stressed_percent)-1
            if not 0<index1<index2<len(availables):
                self.change_proxy('GLOBAL',availables[0][0])
            if availables[index2][2]/availables[index2-1][2]>dense_discriminate:
                if availables[index1][2]/availables[index1-1][2]>dense_discriminate:
                    self.change_proxy('GLOBAL', availables[0][0])
                else:
                    self.change_proxy('GLOBAL', availables[index1][0])
            else:
                self.change_proxy('GLOBAL', availables[index2][0])
        if strategy=='rest 1 minute':
            global pointer,press_rate
            try:
                pointer
            except:
                pointer=[availables[_][0] for _ in range(int(press_rate*len(availables))+1)]
                self.change_proxy('GLOBAL',pointer[0])
                return
            if availables[0][2]==0:
                for i in range(len(availables)-1,-1,-1):
                    if availables[i][0] in pointer:
                        pointer.remove(availables[i][0])
                        break
                pointer.append(availables[0][0])
                self.change_proxy('GLOBAL',availables[0][0])
            else:
                ma=0
                with usage_dic_lock:
                    t=time.time()
                    for i in pointer:
                        if not usage_dic[i]:
                            self.change_proxy('GLOBAL',i)
                            return
                        if t-usage_dic[i][-1]>ma:
                            ma=t-usage_dic[i][-1]
                            least_recently_used_node=i
                self.change_proxy('GLOBAL',least_recently_used_node)

    def limited_fastest(self,limit=0):
        if not limit:
            limit=self.limit

    def time_switch(self,limit=0):
        if not limit:
            limit=self.limit

    def usage_switch(self,limit=0):
        if not limit:
            limit=self.limit

global usage_dic
usage_dic={}
clash=Proxying_by_Clash()

def get_raw(url,index,unicode,vary_node,limit=0,strategy='average focus'):
    path='crawl control\\'+str(unicode)
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.79'}
    encoded_url = quote(url, safe="/:")
    global book,cur_thread_num
    if vary_node:
        with clash_op_lock:
            clash.change_one_by_use(strategy,limit)
            current_node = clash.current_node
        with print_lock:
            print(index,current_node)
        with usage_dic_lock:
            usage=usage_dic.get(clash.current_node,[])
            t=time.time()
            usage.append(t)
            usage_dic[clash.current_node]=usage
    try:
        req=urllib.request.Request(headers=headers,url=encoded_url)
        content=urllib.request.urlopen(req).read()
    except:
        with print_lock:
            try:
                print(index,'failed!',url, current_node)
            except:
                print(index, 'failed!', url)
        with signal_lock:
            try:
                book[index]=0
                cur_thread_num-=1
            except:
                pass
        return
    with open(path+'\\'+str(index)+'.txt','wb') as f:
        f.write(content)
    with signal_lock:
        try:
            book[index]=1
            cur_thread_num-=1
        except:
            pass
    with print_lock:
        print(index,'successful!')

def virtualize_usage(limit):
    global press_rate,rest_time
    prox=clash.filter_limit(limit)
    #print(prox)
    proxies=clash.get_proxies()['proxies']
    able=[]
    for i in prox:
        if proxies[i]['history'] and proxies[i]['history'][-1]['delay']!=0:
            able.append(i)
    gap=rest_time/len(able)
    t=time.time()
    for i in range(int((1-press_rate)*len(able))-1):
        usage_dic[able[i]]=[t-gap*i]

global press_rate,rest_time
press_rate=0.3
rest_time=30

def multicrawl(url_list,node_usage='constant',strategy='average focus',limit=0,max_thread=20):
    path='crawl control'
    vusign=1
    if not os.path.exists(path):
        os.makedirs(path)
    if not os.path.exists(path+'\\'+'last unique code.txt'):
        with open(path+'\\'+'last unique code.txt','w') as f:
            f.write('1')
        unique_code=0
    else:
        with open(path+'\\'+'last unique code.txt','r') as f:
            unique_code=int(f.read())
        with open(path+'\\'+'last unique code.txt','w') as f:
            f.write(str(unique_code+1))
    cur_path=path+'\\'+str(unique_code)
    os.makedirs(cur_path)

    t=time.time()
    global book
    global cur_thread_num
    book=[0 for _ in url_list]
    cur_thread_num=0
    sign=1
    threads=[]
    while sign:
        with signal_lock:
            temp=cur_thread_num
        while temp>=max_thread:
            with signal_lock:
                temp=cur_thread_num
            time.sleep(0.1)
        k=-1
        sign=0
        for i in range(len(book)):
            with signal_lock:
                temp=book[i]
            if not temp:
                sign=1
                if temp!=2:
                    k=i
                    with signal_lock:
                        book[i]=2
                    break
        if k!=-1:
            with signal_lock:
                cur_thread_num+=1
            if node_usage=='vary node':
                if strategy=='rest 1 minute' and vusign:
                    virtualize_usage(limit)
                    vusign=0
                thread=threading.Thread(target=get_raw,args=(url_list[k],k,unique_code,1,limit,strategy))
            else:
                thread=threading.Thread(target=get_raw,args=(url_list[k],k,unique_code,0,limit,strategy))
            threads.append(thread)
            thread.start()
    for i in threads:
        i.join()
    return unique_code
