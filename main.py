import random
import time
import tkinter as tk
import subprocess
import pygame
from tkinter import scrolledtext
from gtts import gTTS
import shutil
import re
import os
import math
import pickle
import pyttsx3
import threading


class NoteAPP:#1,3
    def __init__(self,index,l,r,bookApp):
        self.root=tk.Tk()
        self.bookApp=bookApp
        self.index=index
        self.l=l
        self.r=r
        self.root.title("笔记")
        try:
            with open(path + '\\' + bookApp.filename + r'\notes.txt', 'r', encoding='utf-8') as f:
                self.note_history = eval(f.read())
        except:
            self.note_history=[]
        if self.index<len(self.note_history):
            note_text=self.note_history[index][2]
        else:
            note_text=''
        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack(side=tk.TOP, fill=tk.X)
        self.input_entry = tk.Entry(self.input_frame)
        self.input_entry.insert(0,note_text)
        self.input_entry.pack(side=tk.BOTTOM)
        self.frame_label = tk.Label(self.input_frame, text="输入笔记:")
        self.frame_label.pack(side=tk.BOTTOM)
        self.save_button=tk.Button(self.root,text='保存',command=self.save_note)
        self.save_button.pack(side=tk.BOTTOM)
        self.delete_button = tk.Button(self.root, text='删除此条笔记', command=self.delete_note)
        self.delete_button.pack(side=tk.BOTTOM)

    def run(self):
        self.root.mainloop()

    def save_note(self):
        text=self.input_entry.get()
        if self.index>=len(self.note_history):
            self.note_history.append([self.l,self.r,text,1])
        else:
            self.note_history[self.index][2]=text
        with open(path + '\\' + self.bookApp.filename + r'\notes.txt', 'w', encoding='utf-8') as f:
            f.write(str(self.note_history))

    def delete_note(self):
        try:
            self.note_history[self.index][3]=0
            self.bookApp.deactivate_note_tag(self.index)
            with open(path + '\\' + self.bookApp.filename + r'\notes.txt', 'w', encoding='utf-8') as f:
                f.write(str(self.note_history))
        except:
            pass


class FindStrAPP:#1*init,7*functional def
    def __init__(self,bookapp):
        self.bookApp=bookapp
        self.root=tk.Tk()
        self.root.title("字符串匹配")
        self.find_frame = tk.Frame(self.root)
        self.find_frame.pack(side=tk.TOP, fill=tk.X)
        self.find_label = tk.Label(self.find_frame, text="输入你想要查找的字符或模式:")
        self.find_label.pack(side=tk.LEFT)
        self.find_entry = tk.Entry(self.find_frame)
        self.find_entry.pack(side=tk.LEFT)
        self.find_button = tk.Button(self.find_frame, text="查找", command=self.find_pattern)
        self.find_button.pack(side=tk.LEFT)
        self.matches_label = tk.Label(self.root, text="")
        self.matches_label.pack(side=tk.BOTTOM, anchor='w')
        self.sign=0

    def one_closing(self):
        self.bookApp.remove_found_tag()
        self.bookApp.remove_cur_look_tag()
        self.root.destroy()

    def run(self):
        self.root.mainloop()

    def look_to(self,to_look_index):
        self.bookApp.remove_cur_look_tag()
        to_look_index%=len(self.matches)
        self.cur_look=to_look_index
        self.bookApp.jump_to(self.matches[to_look_index][2][0])
        self.bookApp.light_cur_look_tag(self.matches[to_look_index][2][0],self.matches[to_look_index][2][1])

    def jump_to(self):
        num=self.num_entry.get()
        try:
            num=int(num)-1
        except:
            num=len(num)-1
        self.look_to(num)

    def look_last(self):
        self.cur_look-=1
        self.look_to(self.cur_look)

    def look_next(self):
        self.cur_look+=1
        self.look_to(self.cur_look)

    def find_pattern(self):
        self.matches_label.config(text='')
        self.bookApp.remove_found_tag()
        self.bookApp.remove_cur_look_tag()
        pattern=self.find_entry.get()
        self.matches=self.bookApp.look_for_pattern(pattern)
        self.matches_label.config(text='查找到'+str(len(self.matches))+'个匹配项')
        self.cur_look=0
        if not self.sign:
            self.sign=1
            self.enter_num=tk.Frame(self.root)
            self.enter_num.pack(side=tk.BOTTOM, fill=tk.X)
            self.num_label=tk.Label(self.enter_num,text='查看第指定个：')
            self.num_label.pack(side=tk.LEFT)
            self.num_entry = tk.Entry(self.enter_num)
            self.num_entry.pack(side=tk.LEFT)
            self.jump_button = tk.Button(self.enter_num, text="跳转", command=self.jump_to)
            self.jump_button.pack(side=tk.LEFT)
            self.look_last = tk.Button(self.root, text='查看上一个', command=self.look_last)
            self.look_last.pack(side=tk.BOTTOM, fill=tk.X)
            self.look_next = tk.Button(self.root, text='查看下一个', command=self.look_next)
            self.look_next.pack(side=tk.BOTTOM, fill=tk.X)
            self.look_first=tk.Button(self.root,text='查看第一个',command=lambda x=0:self.look_to(x))
            self.look_first.pack(side=tk.BOTTOM, fill=tk.X)


class BookSelectionWindow:#1*init,3*functional def
    def __init__(self,path):
        self.root = tk.Tk()
        self.root.title("选择书籍")
        self.books_directory = path+r'\books'
        self.scrollbar = tk.Scrollbar(self.root)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.book_listbox = tk.Listbox(self.root, yscrollcommand=self.scrollbar.set, font=("Arial", 20))
        self.book_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.book_listbox.yview)
        self.load_books()

    def run(self):
        self.root.mainloop()

    def load_books(self):
        for file_name in os.listdir(self.books_directory):
            if file_name.lower().endswith(".txt"):
                book_name = file_name[:-4]
                self.book_listbox.insert(tk.END, book_name)
        self.book_listbox.bind("<Double-Button-1>", self.open_selected_book)

    def open_selected_book(self,event):
        selected_book_index=self.book_listbox.curselection()
        if selected_book_index:
            selected_book_name=self.book_listbox.get(selected_book_index)
            read_app=ReaderApp(selected_book_name,path)
            read_app.root.protocol("WM_DELETE_WINDOW",read_app.on_closing)
            read_app.run()


class Novel_Analyse:
    def __init__(self,bookApp):
        self.bookapp=bookApp
        self.root=tk.Tk()
        self.lang='中文' if is_chinese_in_total(bookApp.content) else '英文'
        self.basic_info_label=tk.Label(self.root,text='当前小说：'+bookApp.filename+'\n'
                                        +'小说语言：'+self.lang+'\n'
                                        +'小说字符数：'+str(len(bookApp.content))+'\n'
                                       +'小说章数：'+str(len(bookApp.chapters))+'\n'
                                       +'每章平均长度：'+str(round(len(bookApp.content)/len(bookApp.chapters)))+'\n')
        self.basic_info_label.pack(side=tk.BOTTOM,fill=tk.X)
        self.writing_habit=tk.Button(self.root,text='文章特征',command=self.see_habit)
        self.writing_habit.pack()

    def get_num_of_char(self,ch):
        return len(re.findall(re.escape(ch),self.bookapp.content))

    def see_habit(self):
        if self.lang=='英文':
            word_num=self.get_word_num(self.bookapp.content)
            self.basic_info_label.config(text='当前小说：'+self.bookapp.filename+'\n'
                                        +'小说字符数：'+str(len(self.bookapp.content))+'\n'
                                       +'小说章数：'+str(len(self.bookapp.chapters))+'\n'
                            +'每章平均长度：'+str(round(len(self.bookapp.content)/len(self.bookapp.chapters)))+'\n'
                                     +'单词数：'+str(word_num)+'\n')
            dots1=[',','.','!','?',';']
            s=0
            for i in range(len(dots1)):
                dots1[i]=[dots1[i],self.get_num_of_char(dots1[i])]
                s+=dots1[i][1]
            print('一级标点分布：')
            for i in range(len(dots1)):
                print(dots1[i][0],':',dots1[i][1]/s)
            print('平均句元字符长度：',len(self.bookapp.content)/s)
            print('平均句元单词数：',word_num/s)
        else:
            self.basic_info_label.config(text='当前小说：' + self.bookapp.filename + '\n'
                                              + '小说字符数：' + str(len(self.bookapp.content)) + '\n'
                                              + '小说章数：' + str(len(self.bookapp.chapters)) + '\n'
                                              + '每章平均长度：' + str(
                round(len(self.bookapp.content) / len(self.bookapp.chapters))) + '\n')
            dots1=['，','。','！','？','；']
            s=0
            for i in range(len(dots1)):
                dots1[i]=[dots1[i],self.get_num_of_char(dots1[i])]
                s+=dots1[i][1]
            print('一级标点分布：')
            for i in range(len(dots1)):
                print(dots1[i][0],':',dots1[i][1]/s)
            print('平均句元长度：',len(self.bookapp.content)/s)

    def get_word_num(self,oristr):
        if not oristr:
            return 0
        if 'a' <= oristr[0] <= 'z' or 'A' <= oristr[0] <= 'Z':
            sum_wd = 1
        else:
            sum_wd=0
        for i in range(1, len(oristr)):
            if ('a' <= oristr[i] <= 'z' or 'A' <= oristr[i] <= 'Z') \
                    and not ('a' <= oristr[i - 1] <= 'z' or 'A' <= oristr[i - 1] <= 'Z'):
                sum_wd += 1
        return sum_wd


class ReaderApp:#1*init,32*functional def
    def __init__(self, filename,path):
        self.root =tk.Tk()
        self.filename=filename
        self.root.title("阅读窗口")
        try:
            with open(path+'\\'+filename+r'\last_habit.txt','r',encoding='utf-8') as f:
                self.cur_font,self.cur_size,self.cur_bgcol,self.cur_word_col=eval(f.read())
        except:
            try:
                os.makedirs(path+'\\'+filename)
            except:
                pass
            self.cur_font = '宋体'
            self.cur_size = '12'
            self.cur_bgcol = 'white'
            self.cur_word_col = 'black'
        #print(self.cur_bgcol)
        self.stopread=False

        self.text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD,
                                              font=(self.cur_font, self.cur_size))
        self.text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        try:
            with open(path+'\\books\\'+filename+'.txt', 'r', encoding='ANSI') as file:
                self.content = file.read()
                self.text.insert(tk.END, self.content)
        except:
            with open(path+'\\books\\'+filename+'.txt', 'r', encoding='utf-8') as file:
                self.content = file.read()
                self.text.insert(tk.END, self.content)
        self.load_last_position()

        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)
        self.root.bind("<Control-f>", self.open_find_window)
        self.root.bind("<Control-u>",self.under_line_and_note)

        self.font_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="字体", menu=self.font_menu)
        fonts = [("宋体", "宋体"), ("黑体", "黑体"), ("微软雅黑", "微软雅黑"), ("华文细黑", "华文细黑"), ("楷体", "楷体"),
                 ("隶书", "隶书")]
        for i in fonts:
            self.font_menu.add_command(label=i[0], command=lambda x=i[1]: self.change_font(x))

        self.size_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="字号", menu=self.size_menu)
        size = [("特小", 9), ("小", 12), ("中", 15), ("大", 18), ("特大", 21)]
        for i in size:
            self.size_menu.add_command(label=i[0], command=lambda x=i[1]: self.change_font_size(x))

        self.color_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="字体颜色", menu=self.color_menu)
        wordcols = [("黑色", "black"), ("红色", "red"), ("白色", "white"), ("深灰色", "darkgray"),
                    ("浅灰色", "lightgray"), ("蓝色", "blue")]
        for i in wordcols:
            self.color_menu.add_command(label=i[0], command=lambda x=i[1]: self.change_font_color(x))

        self.bgcolor_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="背景颜色", menu=self.bgcolor_menu)
        bgcols = [("黑色1", "black"), ("白色", "white"), ("麦色", "wheat"), ("灰色", "lightgray"), ("米黄色", "beige")]
        for i in bgcols:
            self.bgcolor_menu.add_command(label=i[0], command=lambda x=i[1]: self.change_bg_color(x))

        self.read_from_current_position_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_command(label="从鼠标位置开始朗读", command=self.start_reading)
        self.menu.add_command(label="终止朗读", command=self.stop_reading)

        self.show_chapters = False
        self.show_chapters_button = tk.Button(self.root, text="显示章节", command=self.toggle_chapter_display)
        self.show_chapters_button.pack(side=tk.TOP, fill=tk.X)

        self.create_chapter_menu()
        self.text.configure(fg=self.cur_word_col)
        self.chapter_listbox.configure(fg=self.cur_word_col)
        self.text.configure(bg=self.cur_bgcol)
        self.chapter_listbox.configure(bg=self.cur_bgcol)
        self.chapter_listbox.configure(font=(self.cur_font, self.cur_size))
        self.renew_chapter_size()
        self.analyse_nevel_button=tk.Button(self.root,text='小说简介',command=self.analyse_novel)
        self.analyse_nevel_button.pack(side=tk.BOTTOM,fill=tk.X)
        self.next_chapter=tk.Button(self.root,text='下一章',command=self.to_next_chapter)
        self.next_chapter.pack(side=tk.BOTTOM,fill=tk.X)
        self.last_chapter=tk.Button(self.root,text='上一章',command=self.to_last_chapter)
        self.last_chapter.pack(side=tk.BOTTOM, fill=tk.X)
        self.set_note()

    def analyse_novel(self):
        analyse_window=Novel_Analyse(self)

    def under_line_and_note(self,event):
        start_index = str(self.text.tag_ranges("sel")[0])
        end_index=str(self.text.tag_ranges("sel")[1])
        try:
            with open(path+'\\'+self.filename+r'\notes.txt','r',encoding='utf-8') as f:
                note_history=eval(f.read())
        except:
            note_history=[]
        self.text.tag_add('note'+str(len(note_history)),start_index,end_index)
        self.text.tag_config('note'+str(len(note_history)),underline=1,foreground="brown")
        self.text.tag_bind('note'+str(len(note_history)),"<Button-3>",lambda event,x=len(note_history):self.show_note(x))
        note_APP=NoteAPP(len(note_history),start_index,end_index,self)

    def set_note(self):
        try:
            #print(path+'\\'+self.filename+r'\notes.txt')
            with open(path+'\\'+self.filename+r'\notes.txt','r',encoding='utf-8') as f:
                note_history=eval(f.read())#[[ind1,ind2,note,isactive],...]
            for i in range(len(note_history)):
                #print(note_history[i][3])
                if note_history[i][3]==1:
                    self.text.tag_add('note'+str(i),note_history[i][0],note_history[i][1])
                    self.text.tag_config('note'+str(i),underline=1)
                    self.text.tag_bind('note'+str(i),"<Button-3>",lambda event,x=i:self.show_note(x))
        except:
            pass

    def deactivate_note_tag(self,index):
        self.text.tag_remove('note'+str(index),"1.0",tk.END)

    def show_note(self,index):
        #print(type(index))
        NoteAPP(index,000,000,self)

    def to_last_chapter(self):
        with open(path + '\\' + self.filename + '\\' + 'chapter_indexs', 'rb') as f:
            indexs=pickle.load(f)
        here=self.text.index("@0,0")
        l = 0
        r = len(indexs) - 1
        while 1:
            mid = (l + r) >> 1
            #print(l, r, mid)
            if eval(indexs[mid]) < eval(here) and eval(indexs[mid+1]) >= eval(here):
                # print('md')
                self.jump_to(str(eval(indexs[mid]) + 5))
                break
            if eval(indexs[mid]) > eval(here):
                r = mid - 1
            else:
                l = mid + 1

    def to_next_chapter(self):
        with open(path + '\\' + self.filename + '\\'+'chapter_indexs', 'rb') as f:
            indexs=pickle.load(f)
        here=str(eval(self.text.index("@0,0"))+14)
        l=0
        r=len(indexs)-1
        #print(r)
        while l<=r:
            mid=(l+r)>>1
         #   print(l,r,mid,indexs[mid],here)
            if eval(indexs[mid])>eval(here) and eval(indexs[mid-1])<=eval(here):
                #print('md')
                self.jump_to(str(eval(indexs[mid])+5))
                break
            if eval(indexs[mid])>eval(here):
                r=mid-1
            else:
                l=mid+1
        #print('md')

    def run(self):
        self.root.mainloop()

    def open_find_window(self, event):
        findapp=FindStrAPP(self)
        findapp.root.protocol("WM_DELETE_WINDOW", findapp.one_closing)
        findapp.run()

    def jump_to(self,index):
        print(index)
        self.text.see(index)
        #print('md')

    def str_index2text_index(self,indexl,indexr):
        try:
            temp=self.splited_content[0]
        except:
            self.splited_content = self.content.split('\n')
            index = 0
            for i in range(len(self.splited_content)):
                self.splited_content[i] = (self.splited_content[i]+'\n', index, index + len(self.splited_content[i]))
                index = self.splited_content[i][2] + 1
        left,right=0,len(self.splited_content)-1
        while left<=right:
            mid =(left+right)>>1
            if self.splited_content[mid][1]<=indexl<=self.splited_content[mid][2]:
                indexl1=mid
                break
            elif indexl<self.splited_content[mid][1]:
                right=mid-1
            else:
                left=mid+1
        left,right=0,len(self.splited_content)-1
        #print(left,right,indexr)
        while left<=right:
            mid=(left+right)>>1
            if self.splited_content[mid][1]<=indexr<=self.splited_content[mid][2]:
                indexr1=mid
                break
            elif indexr<self.splited_content[mid][1]:
                right=mid-1
            else:
                left=mid+1
        indexl2=indexl-self.splited_content[indexl1][1]
        indexr2=indexr-self.splited_content[indexr1][1]
        return (str(indexl1+1)+'.'+str(indexl2),str(indexr1+1)+'.'+str(indexr2+1))

    def look_for_pattern(self,pattern):
        try:
            temp=self.splited_content[0]
        except:
            self.splited_content = self.content.split('\n')
            index = 0
            for i in range(len(self.splited_content)):
                self.splited_content[i] = (self.splited_content[i]+'\n', index, index + len(self.splited_content[i]))
                index = self.splited_content[i][2] + 1
        matches=re.findall(pattern,self.content)
        matches.append(('',(0,0)))
        for i in range(len(matches)-1):
            start=self.content.find(matches[i],matches[i-1][1][0]+1,len(self.content))
            matches[i]=[matches[i],(start,start+len(matches[i])-1)]
        matches.remove(('',(0,0)))
        for i in range(len(matches)):
            matches[i].append(self.str_index2text_index(matches[i][1][0],matches[i][1][1]))
            self.text.tag_add("found", matches[i][2][0],matches[i][2][1])
        self.text.tag_config("found", background="yellow")
        return matches

    def light_cur_look_tag(self,indexl,indexr):
        self.text.tag_add("curlook",indexl,indexr)
        self.text.tag_config("curlook",background="orange")

    def remove_cur_look_tag(self):
        self.text.tag_remove("curlook", "1.0", tk.END)

    def remove_found_tag(self):
        self.text.tag_remove("found", "1.0", tk.END)

    def change_font(self, font):
        self.cur_font = font
        self.text.configure(font=(self.cur_font, self.cur_size))
        self.chapter_listbox.configure(font=(self.cur_font, self.cur_size))
        self.renew_chapter_size()

    def change_font_size(self, size):
        self.cur_size = size
        self.text.configure(font=(self.cur_font, size))
        self.chapter_listbox.configure(font=(self.cur_font, size))
        self.renew_chapter_size()

    def change_font_color(self, color):
        self.cur_word_col = color
        self.text.configure(fg=color)
        self.chapter_listbox.configure(fg=color)

    def change_bg_color(self, color):
        self.cur_bgcol = color
        self.text.configure(bg=color)
        self.chapter_listbox.configure(bg=color)

    def load_last_position(self):
        try:
            with open(path+'\\'+self.filename+'\\'+'last_position.txt', 'r') as f:
                start = f.read()
            self.text.see(start)
        except FileNotFoundError:
            pass

    def save_last_position(self):
        start = self.text.index("@0,0")
        with open(path+'\\'+self.filename+'\\'+'last_position.txt', 'w') as f:
            f.write(start)

    def save_last_habit(self):
        with open(path+'\\'+self.filename+'\\'+'last_habit.txt','w',encoding='utf-8') as f:
            f.write(str([self.cur_font, self.cur_size, self.cur_bgcol, self.cur_word_col]))

    def on_closing(self):
        self.save_last_position()
        self.save_last_habit()
        self.root.destroy()

    def mark_chapter_names(self,chapters):
        if not chapters:
            return 0
        name_lens=list(map(lambda x:len(x),chapters))
        mean=Mean(name_lens)
        std=Std(name_lens)
        extreme_len_num=0
        #i=0
        for name_len in name_lens:
            if abs(name_len-mean)>std*5:
                #print(chapters[i])
                extreme_len_num+=1
            #i+=1
        extreme_len_mark=(len(self.content)/1e6)/(extreme_len_num+len(self.content)/1e6)
        #print(std, mean, extreme_len_mark)
        return extreme_len_mark**2*(1-(std/mean))

    def mark_chapter_gaps(self,chapters):
        #print(chapters)
        if not chapters:
            return 0
        indexs=[]
        for i in range(len(chapters)):
            indexs.append(self.content.find(chapters[i],0 if not indexs else indexs[-1],len(self.content)))
        indexs.append(len(self.content))
        gaps=[indexs[i]-indexs[i-1] for i in range(1,len(indexs))]
        mean=Mean([indexs[0]]+gaps)
        std=Std(gaps)
        std_mark=1-std/mean
        if mean<1300:
            mean_mark=mean/1300
        elif mean>1e4:
            mean_mark=1e4/mean
        else:
            mean_mark=1
        extreme_gap_num=0
        for i in gaps:
            if abs(i-mean)>5*std:
                extreme_gap_num+=1
        extreme_gap_mark=math.exp(1/(extreme_gap_num/len(chapters)+0.2171472409516259))#(0,100),(1/100,81.6),(1/50,67.8)
        #print(mean_mark,extreme_gap_mark,std_mark)
        return mean_mark*extreme_gap_mark*std_mark

    def pattern_auto_select(self):
        print('自动选择正则表达式中...')
        patterns = [r'第\d*章.*\n', r'第.*章\s.*\n', r'===(.*)===', r'第.*章.*\n', r'Chapter.*\n', r'CHAPTER.*\n',
                    r'\d+.{0,15}\n', r'\d+\n',
                    r'第[〇一二三四五六七八九十百千万零壹贰叁肆伍陆柒捌玖拾佰仟萬億兆参拾零` ]+回\s.*\n',r'第.+回\s.+\n',
            r'(第.*回\s.+\s.+)\s',r'[ \t]+第.+章[ \t].+[ \t]+',r'\d+、.*\n',r'([A-Z]+\s-\s.*?)\n']
        name_marks=[]
        gap_marks=[]
        for pattern in patterns:
            #print(pattern)
            cur_pattern_chapters=re.findall(pattern,self.content)
            name_marks.append(self.mark_chapter_names(cur_pattern_chapters))
            gap_marks.append(self.mark_chapter_gaps(cur_pattern_chapters))
        for i in range(len(name_marks)):
           print(patterns[i],':',name_marks[i],gap_marks[i])
        print('\n')
        name_marks=max_normalize(name_marks)
        gap_marks=max_normalize(gap_marks)
        marks=[(name_marks[i]*gap_marks[i],patterns[i]) for i in range(len(patterns))]
        # for i in range(len(marks)):
        #    print(marks[i][1],':',marks[i][0])
        marks.sort(key=lambda x:x[0],reverse=1)
        print('已为您选择最合适的正则表达式：“',marks[0][1],'”','(Relative Preferance:',marks[0][0]*100,'%)',sep='')
        return marks[0][1]

    def create_chapter_menu(self):
        try:
            with open(path+'\\'+self.filename+'\\'+'chapter','rb') as f:
                self.chapters=pickle.load(f)
        except:
            print('首次阅读',self.filename,'，预处理中...',sep='')
            pattern=self.pattern_auto_select()
            self.chapters = re.findall(pattern, self.content)
            with open(path+'\\'+self.filename+'\\'+'chapter','wb') as f:
                pickle.dump(self.chapters,f)
        self.chapter_listbox = tk.Listbox(self.root, selectmode=tk.SINGLE)
        self.chapter_listbox.pack(side=tk.LEFT, fill=tk.Y, expand=True)

        scrollbar = tk.Scrollbar(self.root, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.chapter_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.chapter_listbox.yview)

        for chapter in self.chapters:
            self.chapter_listbox.insert(tk.END, chapter)

        self.chapter_listbox.bind('<<ListboxSelect>>', self.on_chapter_select)
        self.hide_chapters()

    def toggle_chapter_display(self):
        if self.show_chapters:
            self.hide_chapters()
        else:
            self.show_chapters_button.config(text="隐藏章节")
            self.chapter_listbox.pack(side=tk.LEFT, fill=tk.Y, expand=True)
            self.show_chapters=True

    def hide_chapters(self):
        self.show_chapters_button.config(text="显示章节")
        self.chapter_listbox.pack_forget()
        self.show_chapters=False

    def on_chapter_select(self,event):#event不要删，tk的包里好像有个函数会传进来一个空参，删了接口对不上
        selected_index=self.chapter_listbox.curselection()[0]
        chapter=self.chapter_listbox.get(selected_index)
        self.jump_to_chapter(chapter)

    def renew_chapter_size(self):
        try:
            with open(path+'\\'+self.filename+'\\'+'chapter_indexs','rb') as f:
                self.indexs=pickle.load(f)
        except:
            self.indexs=[]
            for i in range(len(self.chapters)):
                self.indexs.append(self.text.search(self.chapters[i],'1.0' if not self.indexs else self.indexs[-1],stopindex=tk.END))
            with open(path+'\\'+self.filename+'\\'+'chapter_indexs','wb') as f:
                pickle.dump(self.indexs,f)
        #print('md')
        for index in self.indexs:
            self.text.tag_config("chapter_title", font=(self.cur_font, int(self.cur_size) + 2, 'bold'))
            self.text.tag_add("chapter_title", index, f"{index} lineend")

    def jump_to_chapter(self, chapter):
        #index=self.text.search(chapter, "1.0", stopindex=tk.END)
        #print(chapter,self.chapters)
        for i in range(len(self.chapters)):
            if chapter==self.chapters[i]:
                index=self.indexs[i]
        if index:
            #self.text.mark_set(tk.INSERT, index)
            self.text.see(index)

    def start_reading(self):
        self.stopread=False
        self.read_thread = threading.Thread(target=self.read_from_cur)
        self.read_thread.start()

    def stop_reading(self):
        self.stopread=True

    def highlight_by_index(self,indexl,indexr):
        self.text.tag_remove("highlight", "1.0", tk.END)
        self.text.see(str(int(indexl.split('.')[0])+8)+'.0')
        self.text.tag_add("highlight",indexl,indexr )
        self.text.tag_configure("highlight", background="yellow")

    def text_index2str_intex(self,index):
        return len(self.text.get('1.0',index))-1

    def read_from_cur(self):
        self.scale = tk.Scale(self.root, from_=0.5, to=5.0, length=300,
                              tickinterval=0.5, orient=tk.HORIZONTAL, resolution=0.01,label='阅读速度')
        self.scale.pack()
        self.scale.set(1)
        try:
            self.speecher
        except:
            self.speecher=Novel2Speech(self)
        str_index=self.text_index2str_intex(self.text.index(tk.INSERT))
        self.speecher.from_index(str_index)


class Novel2Speech:
    def __init__(self,bookApp):
        pygame.mixer.init()
        self.bookApp=bookApp
        try:
            with open(path+'\\'+self.bookApp.filename+'\\splited_indexs.txt','r',encoding='utf-8') as f:
                self.splited_indexs=eval(f.read())
        except:
            mid_content=self.bookApp.content.split('\n')
            mid_index=[]
            s=0
            for i in mid_content:
                mid_index.append((s,s+len(i)))
                s=s+len(i)+1
            splited_indexs=[]
            for i in range(len(mid_content)):
                if not self.judge_length(mid_content[i]):
                    a=self.split_section(mid_content[i],mid_index[i][0])
                    splited_indexs.extend(a[1])
                else:
                    splited_indexs.append(mid_index[i])
            print('md')
            with open(path+'\\'+self.bookApp.filename+'\\splited_indexs.txt','w',encoding='utf-8') as f:
                f.write(str(splited_indexs))
            self.splited_indexs=splited_indexs
        #self.index_self_check()

    def get_word_num(self,oristr):
        if not oristr:
            return 0
        if 'a' <= oristr[0] <= 'z' or 'A' <= oristr[0] <= 'Z':
            sum_wd = 1
        else:
            sum_wd=0
        for i in range(1, len(oristr)):
            if ('a' <= oristr[i] <= 'z' or 'A' <= oristr[i] <= 'Z') \
                    and not ('a' <= oristr[i - 1] <= 'z' or 'A' <= oristr[i - 1] <= 'Z'):
                sum_wd += 1
        return sum_wd

    def have_character(self,oristr):
        for i in range(len(oristr)):
            if 'a' <= oristr[i] <= 'z' or 'A' <= oristr[i] <= 'Z' or u'\u4e00' <= oristr[i] <= u'\u9fff':
                return 1
        return 0

    def judge_length(self,oristr):
        if not self.have_character(oristr):
            return 1
        lan=is_chinese_in_total(oristr)
        if lan:
            sum_ch=0
            for i in oristr:
                if u'\u4e00' <= i <= u'\u9fff':
                    sum_ch+=1
            if sum_ch<=30:
                return 1
            else:
                return 0
        else:
            if self.get_word_num(oristr)<=30:
                return 1
            else:
                return 0

    def split_section(self,oristr,begin_index):
        lan=is_chinese_in_total(oristr)
        if lan:
            split_couple = [r'[。！？]',r'[。！？，]',r'[。！？，；]',r'[。！？，；：]',r'[。！？，；：—]',r'[。！？，；：“”—]']
            mark = []
            for i in range(len(split_couple)):
                a = re.split(split_couple[i], oristr)
                # mark chinese
                s1 = 0
                s2 = 0
                tot = 0
                for j in a:
                    if not len(j):
                        continue
                    else:
                        tot += len(j)
                        s1 += 1
                        if not 4 <= len(j) and len(j) <= 30:
                            s2 += 1
                mark.append(((1 - s2 / s1) * (1 - abs(tot / s1 - 20) / 50), split_couple[i]))
            mark.sort(key=lambda x: x[0], reverse=1)
            top_couple=mark[0][1]
            splited_section=re.split(top_couple,oristr)
            splited_index=[]
            s=0
            for i in range(len(splited_section)):
                if splited_section[i]:
                    if s + len(splited_section[i]) < len(oristr):
                        splited_section[i] = splited_section[i] + oristr[s + len(splited_section[i])]
                        splited_index.append((begin_index + s, begin_index + s + len(splited_section[i]) - 1))
                    else:
                        splited_index.append((begin_index + s, begin_index + s + len(splited_section[i])))
                    s += len(splited_section[i])
                else:
                    splited_index.append((begin_index + s, begin_index + s))
                    s += 1
            return splited_section,splited_index
        else:
            split_couple = [r'[.!?]', r'[.!?,]', r'[.!?,;]', r'[.!?,:;]', r'[.!?,:;—]', r'[.!?,:;“”—]']
            mark = []
            s1 = 0
            s2 = 0
            tot = 0
            for i in range(len(split_couple)):
                a = re.split(split_couple[i], oristr)
                # mark eng
                for j in a:
                    if len(j)>0:
                        tot += self.get_word_num(j)
                        s1 += 1
                        if not 3 <= self.get_word_num(j) and self.get_word_num(j) <= 30:
                            s2 += 1
                mark.append(((1 - s2 / s1) * (1 - abs(tot / s1 - 20) / 50), split_couple[i]))
            mark.sort(key=lambda x: x[0], reverse=1)
            top_couple = mark[0][1]
            splited_section = re.split(top_couple, oristr)
            splited_index = []
            s = 0
            for i in range(len(splited_section)):
                if splited_section[i]:
                    if s + len(splited_section[i]) < len(oristr):
                        splited_section[i] = splited_section[i] + oristr[s + len(splited_section[i])]
                        splited_index.append((begin_index + s, begin_index + s + len(splited_section[i]) - 1))
                    else:
                        splited_index.append((begin_index + s, begin_index + s + len(splited_section[i])))
                    s+=len(splited_section[i])
                else:
                    splited_index.append((begin_index + s, begin_index + s))
                    s+=1
            return splited_section,splited_index

    def str_index2splited_index(self,index):
        for i in range(len(self.splited_indexs)):
            if (self.splited_indexs[i][0]<=index<=self.splited_indexs[i][1]) or self.splited_indexs[i][0]>index:
                return i

    def index_self_check(self,index=0):
        for i in range(index,len(self.splited_indexs)):
            if not (self.splited_indexs[i][1]-self.splited_indexs[i][0]):
                continue
            indexl,indexr=self.bookApp.str_index2text_index(self.splited_indexs[i][0],self.splited_indexs[i][1])
            self.bookApp.highlight_by_index(indexl,indexr)
            time.sleep(1)

    def delete_cache_ticking(self):
        time.sleep(10*60)
        shutil.rmtree('cache')

    def read_thread(self):
        file=''
        last_miss=0
        while self.read_index<len(self.splited_indexs) and not self.bookApp.stopread:
            text = self.bookApp.content[self.splited_indexs[self.read_index][0]
                                        :self.splited_indexs[self.read_index][1] + 1]
            while not self.have_character(text):
                self.read_index+=1
                text = self.bookApp.content[self.splited_indexs[self.read_index][0]
                                            :self.splited_indexs[self.read_index][1] + 1]
            cache_list=os.listdir('cache')
            for i in range(len(cache_list)):
                cache_list[i]=(cache_list[i],cache_list[i].replace('.mp3','').split('_')[0]
                               ,cache_list[i].replace('.mp3','').split('_')[1]
                               if len(cache_list[i].replace('.mp3','').split('_'))>1 else '1.0')
                #print(str(self.read_index),cache_list[i][1],str(self.read_index)==cache_list[i][1])
                if str(self.read_index)==cache_list[i][1]:
                    file='cache\\'+cache_list[i][0]
                    file_rate=cache_list[i][2]
                if self.read_index>int(cache_list[i][1]) or self.read_index+40<int(cache_list[i][1]):
                    try:
                        os.remove('cache\\'+cache_list[i][0])
                    except:
                        pass
            if file:
                self.miss*=0.9
                last_miss=0
                rate=self.bookApp.scale.get()
                if str(rate)==file_rate:
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.01)
                    pygame.mixer.music.stop()
                    if hasattr(pygame.mixer.music, 'unload'):
                        pygame.mixer.music.unload()
                    if self.bookApp.stopread:
                        self.bookApp.text.tag_remove("highlight", "1.0", tk.END)
                        return
                    indexl,indexr=self.bookApp.str_index2text_index(self.splited_indexs[self.read_index][0]
                                                                    ,self.splited_indexs[self.read_index][1])
                    self.bookApp.highlight_by_index(indexl,indexr)
                    pygame.mixer.music.load(file)
                    pygame.mixer.music.play()
                else:
                    sign=1
                    new_file='cache\\'+str(self.read_index)+'_'+str(rate)+'.mp3'
                    if rate > 2:
                        cmd = 'ffmpeg -i "{}" -filter:a "atempo={}" -vn "{}"'.format(file, 2, 'temp1.mp3')
                        try:
                            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                            os.remove(file)
                        except:
                            time.sleep(0.01)
                            try:
                                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                                os.remove(file)
                            except:
                                print(self.read_index,'Speed changing failed!')
                                sign=0
                        rate /= 2
                        if rate > 2 and sign:
                            cmd = 'ffmpeg -i "{}" -filter:a "atempo={}" -vn "{}"'.format('temp1.mp3', 2, 'temp2.mp3')
                            try:
                                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                                os.remove('temp1.mp3')
                            except:
                                print(self.read_index, 'Speed changing failed!')
                                sign = 0
                            rate /= 2
                            if rate > 2 and sign:
                                cmd = 'ffmpeg -i "{}" -filter:a "atempo={}" -vn "{}"'.format('temp2.mp3', 2,
                                                                                             'temp3.mp3')
                                try:
                                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                                    os.remove('temp2.mp3')
                                except:
                                    print(self.read_index, 'Speed changing failed!')
                                    sign = 0
                                rate /= 2
                                if sign:
                                    cmd = 'ffmpeg -i "{}" -filter:a "atempo={}" -vn "{}"'.format('temp3.mp3', rate,
                                                                                             new_file)
                                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                                    os.remove('temp3.mp3')
                            else:
                                cmd = 'ffmpeg -i "{}" -filter:a "atempo={}" -vn "{}"'.format('temp2.mp3', rate,
                                                                                             new_file)
                                try:
                                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                                    os.remove('temp2.mp3')
                                except:
                                    print(self.read_index, 'Speed changing failed!')
                                    sign = 0
                        else:
                            try:
                                cmd = 'ffmpeg -i "{}" -filter:a "atempo={}" -vn "{}"'.format('temp1.mp3', rate, new_file)
                                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                                os.remove('temp1.mp3')
                            except:
                                print(self.read_index, 'Speed changing failed!')
                                sign = 0
                    else:
                        cmd = 'ffmpeg -i "{}" -filter:a "atempo={}" -vn "{}"'.format(file, rate, new_file)
                        try:
                            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                            os.remove(file)
                        except:
                            print(self.read_index, 'Speed changing failed!')
                            sign = 0
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.001)
                    pygame.mixer.music.stop()
                    if hasattr(pygame.mixer.music, 'unload'):
                        pygame.mixer.music.unload()
                    if self.bookApp.stopread:
                        self.bookApp.text.tag_remove("highlight", "1.0", tk.END)
                        return
                    indexl,indexr=self.bookApp.str_index2text_index(self.splited_indexs[self.read_index][0]
                                                                    ,self.splited_indexs[self.read_index][1])
                    self.bookApp.highlight_by_index(indexl,indexr)
                    if sign:
                        pygame.mixer.music.load(new_file)
                        pygame.mixer.music.play()
                    else:
                        if not last_miss:
                            self.miss += 1
                            last_miss = 1
                        else:
                            self.miss += 1 / math.log(self.miss + 1, 2)  # 衰减增加的不信任度，防止不信任值过高导致即使gtts恢复正常也要很久才恢复信任
                        if self.bookApp.stopread:
                            self.bookApp.text.tag_remove("highlight", "1.0", tk.END)
                            return
                        indexl, indexr = self.bookApp.str_index2text_index(self.splited_indexs[self.read_index][0]
                                                                           , self.splited_indexs[self.read_index][1])
                        self.bookApp.highlight_by_index(indexl, indexr)
                        engine = pyttsx3.init()
                        rate = self.bookApp.scale.get()
                        voices = engine.getProperty('voices')
                        engine.setProperty('rate', rate * 200)
                        if is_chinese_in_total(text):
                            lang = 'zh'
                        else:
                            lang = 'en'
                        engine.setProperty('voice', lang)
                        engine.setProperty('voice', voices[0].id)
                        engine.say(text)
                        engine.runAndWait()
            else:
                #print('mmmmmmmmmd\n\n\n',self.read_index,os.listdir('cache'))
                if not last_miss:
                    self.miss+=1
                    last_miss=1
                else:
                    self.miss+=1/math.log(self.miss+1,2)#衰减增加的不信任度，防止不信任值过高导致即使gtts恢复正常也要很久才恢复信任
                if self.bookApp.stopread:
                    self.bookApp.text.tag_remove("highlight", "1.0", tk.END)
                    return
                indexl,indexr = self.bookApp.str_index2text_index(self.splited_indexs[self.read_index][0]
                                                                  ,self.splited_indexs[self.read_index][1])
                self.bookApp.highlight_by_index(indexl, indexr)
                engine = pyttsx3.init()
                rate=self.bookApp.scale.get()
                voices = engine.getProperty('voices')
                engine.setProperty('rate', rate*200)
                if is_chinese_in_total(text):
                    lang='zh'
                else:
                    lang='en'
                engine.setProperty('voice', lang)
                engine.setProperty('voice', voices[0].id)
                engine.say(text)
                engine.runAndWait()
            self.read_index+=1
        self.bookApp.text.tag_remove("highlight", "1.0", tk.END)

    def cache_thread(self):
        if not os.path.exists('cache'):
            os.makedirs('cache')
        is_first=1
        while self.cache_index<len(self.splited_indexs) and not self.bookApp.stopread:
            #print(self.cache_index,self.bookApp.stopread)
            text = self.bookApp.content[self.splited_indexs[self.cache_index][0]
                                        :self.splited_indexs[self.cache_index][1] + 1]
            while not self.have_character(text) and self.cache_index<len(self.splited_indexs):
                self.cache_index += 1
                text = self.bookApp.content[self.splited_indexs[self.cache_index][0]
                                            :self.splited_indexs[self.cache_index][1] + 1]
            while len(os.listdir('cache'))>=20 or self.cache_index>self.read_index+40:
                if self.bookApp.stopread:
                    #print('md')
                    DCT_threading = threading.Thread(target=self.delete_cache_ticking)
                    DCT_threading.start()
                    return
                cache_list = os.listdir('cache')
                for i in range(len(cache_list)):
                    cache_list[i] = (cache_list[i], cache_list[i].replace('.mp3', '').split('_')[0]
                                     , cache_list[i].replace('.mp3','').split('_')[1]
                               if len(cache_list[i].replace('.mp3','').split('_'))>1 else '1.0')
                    if self.read_index > int(cache_list[i][1]) or self.read_index + 40 < int(cache_list[i][1]):
                        try:
                            os.remove('cache\\' + cache_list[i][0])
                        except:
                            pass
                time.sleep(0.1)
            if self.cache_index<=self.read_index and not is_first:#指数退避
                self.cache_index+=random.randint(0,min(10,int(2**self.miss)))
            is_first=0
            if is_chinese_in_total(text):
                lang='zh-cn'
            else:
                lang='en'
            sign=1
            try:
                f = gTTS(text=text,lang=lang)
                file = 'cache' + '\\' + str(self.cache_index) + '.mp3'
                f.save(file)
            except:
                time.sleep(2+random.randint(0,min(8,int(2**self.miss))))#爬虫异常一次，弱指数退避
                try:
                    f=gTTS(text=text,lang=lang)
                    file = 'cache' + '\\' + str(self.cache_index) + '.mp3'
                    f.save(file)
                except:
                    time.sleep(5+random.randint(0,min(100-100/(self.miss/5+1.1),int(2.1**self.miss))))#爬虫异常两次，强指数退避
                    try:
                        f = gTTS(text=text, lang=lang)
                        file = 'cache' + '\\' + str(self.cache_index) + '.mp3'
                        f.save(file)
                    except:
                        sign=0
                        print(self.cache_index,'downloading failed!')
            if sign:
                rate=self.bookApp.scale.get()
                new_file='cache'+'\\'+str(self.cache_index)+'_'+str(rate)+'.mp3'
                if rate>2:
                    cmd = 'ffmpeg -i "{}" -filter:a "atempo={}" -vn "{}"'.format(file, 2, 'temp1.mp3')
                    try:
                        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                        os.remove(file)
                    except:
                        print(self.cache_index, 'Speed changing failed!(while caching)')
                        sign = 0
                    rate /= 2
                    if rate>2 and sign:
                        cmd = 'ffmpeg -i "{}" -filter:a "atempo={}" -vn "{}"'.format('temp1.mp3', 2,'temp2.mp3' )
                        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                        os.remove('temp1.mp3')
                        rate/=2
                        if rate>2:
                            cmd = 'ffmpeg -i "{}" -filter:a "atempo={}" -vn "{}"'.format('temp2.mp3', 2, 'temp3.mp3')
                            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                            os.remove('temp2.mp3')
                            rate/=2
                            cmd = 'ffmpeg -i "{}" -filter:a "atempo={}" -vn "{}"'.format('temp3.mp3', rate, new_file)
                            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                            os.remove('temp3.mp3')
                        else:
                            cmd = 'ffmpeg -i "{}" -filter:a "atempo={}" -vn "{}"'.format('temp2.mp3', rate, new_file)
                            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                            os.remove('temp2.mp3')
                    else:
                        cmd = 'ffmpeg -i "{}" -filter:a "atempo={}" -vn "{}"'.format('temp1.mp3', rate, new_file)
                        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                        os.remove('temp1.mp3')
                else:
                    cmd = 'ffmpeg -i "{}" -filter:a "atempo={}" -vn "{}"'.format(file, rate, new_file)
                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                    os.remove(file)
            self.cache_index+=1
        #print('md')
        DCT_threading = threading.Thread(target=self.delete_cache_ticking)
        DCT_threading.start()

    def from_index(self,str_index):
        self.miss=0
        index=self.str_index2splited_index(str_index)
        #self.index_self_check(index)
        self.read_index=index
        self.cache_index=index
        cache_threading=threading.Thread(target=self.cache_thread)
        cache_threading.start()
        dialog = tk.Toplevel(self.bookApp.root)
        dialog.title('提示')
        tk.Label(dialog, text="准备朗读，预处理中（此过程约5-10s）......").pack()
        t1=time.time()
        t2=time.time()
        s=0
        while t2-t1<10 and s<5:
            s=0
            t2=time.time()
            try:
                cache_list=os.listdir('cache')
                for i in cache_list:
                    if self.read_index+5>=int(i.split('_')[0])>=self.read_index:
                        s+=1
            except:
                pass
        dialog.destroy()
        reading_thread=threading.Thread(target=self.read_thread)
        reading_thread.start()
        cache_threading.join()
        reading_thread.join()
        print('threads stopped!')



def max_normalize(x):
    ma=max(x)
    x=list(map(lambda a:a/ma,x))
    return x

def Mean(x):
    if not len(x):
        return 0
    else:
        return (sum(x)+0.0)/len(x)

def Std(x):
    if not len(x):
        return 0
    else:
        mean=Mean(x)
        s=0
        for i in x:
            s+=(i-mean)**2
        return (s/len(x))**0.5

def is_chinese_in_total(str):
    s1=0
    s2=0
    for ch in str:
        if u'\u4e00' <= ch <= u'\u9fff':
            s1+=1
        elif 'a'<=ch<='z' or 'A'<=ch<='Z':
            s2+=1
    if s1/(s1+s2)>=0.5:
        return 1
    else:
        return 0



path=r'D:\大学\门前雪\小说记录\PythonReadBook\bookfiles'
show=BookSelectionWindow(path)
show.run()

