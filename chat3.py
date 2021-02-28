#== chat3.py ==
##-- A.B.Glazov -- 29/09/2020 --
##-- чат, отслеживание партнеров
##-- структура сообщения:   mess_nick, dest_nick, mess_data
##--<3>-- структура принятого сообщения:   ip, mess_nick, dest_nick, mess_data, mess_time


##-- библиотеки отрисовки
from tkinter import *
from tkinter import font
from tkinter import ttk 
from tkinter import simpledialog

##==<2>== библиотеки для работы с сетью
from socket import *
import threading
from time import *

#== переменные
##-- цвета элементов оформления
root_color  = "thistle"     #-- цвет формы
sel_color = "red"

##-- вспомогательные переменные
btn_width = 14             #-- размер кнопок
text_width = 400           #-- ширина поля чата

##--<3>-- списое партнеров (добавил время)
lst_partn = [("all","255.255.255.255",-1),("piter","192.168.1.200",0)]
partn_tau = 3000           #-- время ожидания партнера в мс

##==<2>== UDP сокет для приема сообщений
HOST_IN = ''
PORT_IN = 4000
BUFSIZE = 1024
SOCKADDR_IN = (HOST_IN,PORT_IN)
uServSock = socket(AF_INET,SOCK_DGRAM)
uServSock.bind(SOCKADDR_IN)

##==<2>==  очередь для приема сообщений и флаг ее занятости
ls_in =[]       
busy_in = 0
main_tau = 30   #-- период цикла главной функции  

##==<2>== UDP  сокет для отправки сообщений
HOST_OUT = '127.0.0.1'
PORT_OUT = 4000
BUFSIZE = 1024
SOCKADDR_OUT = (HOST_OUT,PORT_OUT)
uCliSock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
uCliSock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

#== функции 
##--<3>-- функция приема сообщений для потока приема
def work_in():
    global ls_in
    global busy_in
    while True:
        data,addr = uServSock.recvfrom(BUFSIZE)
        loc_data = data.decode('cp1251')                        
        loc_data = loc_data.strip()
                               
        mess_time = str(get_timems())   #--<3>--
        st = addr[0] + '|' +  loc_data + "|" + mess_time #-- запомнить IP и строку

        while busy_in:
            sleep(0.001)
        busy_in = 2
        ls_in.append(st)
        busy_in = 0
                                
        sleep(0.001)
    uServSock.close()

##---<2>--  отправить сообщение 
def send_mess( mess, ip ):
    #print( ip )    
    st = mess.encode('cp1251')
    sock_addr = ( ip, PORT_OUT)
    uCliSock.sendto(st,sock_addr)

##--<3>-- получить время в миллисекундах
def get_timems():
    return int(time()*1000)
	
	
#== создать форму
root = Tk()
root.resizable(width=False, height=False)
dFont = font.Font(family="helvetica", size=12)
stl = ttk.Style()

root.configure(background=root_color )
stl.configure('.', font=dFont, background=root_color , foreground= "black")

ttk.Label(root, text = 'проcтой чат (версия 1)').grid(row = 0, column = 0, pady = 5)

#== левая панель для текстовых сообщений
pnl_left = Frame(root)
pnl_left.grid(row = 2, column = 0, columnspan = 6, rowspan = 10, pady = 10, padx = 10)

##== панель для вывода получекнных сообщений (основная)
pnl_mess = Frame(pnl_left, width = 700)
pnl_mess.grid(row = 2, column = 0)

###== текстовое поле для вывода получекнных сообщений
tbx_mess = Text(pnl_mess, height = 30, wrap=WORD, font = dFont )
tbx_mess.pack(side = 'left', fill = 'both', expand = 1)

###== полоса прокрутки для текстового поля получекнных сообщений
sbr_mess = Scrollbar(pnl_mess)
sbr_mess['command'] = tbx_mess.yview
tbx_mess['yscrollcommand'] = sbr_mess.set
sbr_mess.pack(side = 'right', fill = 'y')

##== панель для вывода сообщений 
pnl_send = Frame(pnl_left)
pnl_send.grid(row = 3, column = 0, pady = 5)

###== текстовое поле для вывода получекнных сообщений
tbx_send = Text(pnl_send, height = 3, wrap=WORD, font = dFont )
tbx_send.pack(side = 'left', fill = 'both', expand = 1)

###== полоса прокрутки для текстового поля отправляемых сообщений
sbr_send = Scrollbar(pnl_send)
sbr_send['command'] = tbx_send.yview
tbx_send['yscrollcommand'] = sbr_send.set
sbr_send.pack(side = 'right', fill = 'y')

###==<2>== обработчик <Enter> для текстового поля отправки
def fnc_tbxsend(event):
    my_nick = var_nick.get()
    if not my_nick:
        my_nick = simpledialog.askstring("замечание","введите Ваш ник ")
        var_nick.set(my_nick)
    
    partn_nick = var_partn.get()
    text_send = tbx_send.get(1.0,END).strip()
    #print(text_send)
    if len(text_send) > 0:
        send_mess( my_nick + "|" + partn_nick + "|" + text_send, HOST_OUT )    #--<2>--
        text_out = "\n(  >>>  " + partn_nick + "  ):    " + text_send 
        tbx_mess.insert(END, text_out )
        tbx_send.delete(1.0, END)
        
tbx_send.bind('<Return>',fnc_tbxsend)

#== правая панель для контактов
pnl_right = Frame(root, background=root_color)
pnl_right.grid(row = 0, column = 8, rowspan = 20)

##-- поле вашего Ника
ttk.Label(pnl_right, text = 'Ваше имя:' ).grid(row = 0, column = 0, sticky=W, padx= 5)
var_nick = StringVar()
var_nick.set("")
edt_nick = ttk.Entry(pnl_right, width = btn_width, textvariable= var_nick, font = dFont )
edt_nick.grid(row = 1, column = 0, padx= 5, pady = 5, sticky=W)

##-- поле ника партнера
ttk.Label(pnl_right, text = 'Партнер:').grid(row = 2, column = 0, sticky=W, pady = 5)
var_partn = StringVar()
var_partn.set("")
edt_partn = ttk.Entry(pnl_right, width = btn_width, textvariable= var_partn, font = dFont )
edt_partn.grid(row = 3, column = 0, padx= 5, pady = 5, sticky=W)

#== панель со списком партнеров
ttk.Label(pnl_right, text = 'партнеры').grid(row = 5, column = 0, padx = 5, pady = 5)
pnl_partn = Frame(pnl_right)
pnl_partn.grid(row = 6, column = 0, padx = 5, pady = 5, sticky=N)

##-- список партнеров с прокруткой
lbx_partn = Listbox(pnl_partn, width = btn_width, height = 16, font = dFont)
lbx_partn.pack(side="left", fill="y")
sbr_partn = Scrollbar(pnl_partn, orient="vertical")
sbr_partn.pack(side="right", fill="y")

sbr_partn.config(command=lbx_partn.yview)
lbx_partn.config(yscrollcommand=sbr_partn.set)

##--<2>-- обработать двойной клик по элементу списка
def fnc_setpartn(ev):
    global HOST_OUT
    index = lbx_partn.curselection()
    partn = lbx_partn.get(index)
    var_partn.set(partn)
    #print(index, lst_partn)
    HOST_OUT = lst_partn[index[0]][1]
    #print( HOST_OUT)

lbx_partn.bind("<Double-Button-1>", fnc_setpartn)

#== действия при запуске программы
cur_time = get_timems()
lst_partn[1] = ("piter","192.168.1.200",cur_time)
##-- загрузить список партнеров

for partn in lst_partn:
    lbx_partn.insert( END, partn[0] )
    

##--<2>-- выбрать начального партнера        
lbx_partn.selection_set(0)
partn = lbx_partn.get(0)
var_partn.set(partn)
HOST_OUT = lst_partn[0][1]

##--<2>-- создать и запустить поток приема сообщений
tr_in = threading.Thread( target = work_in)
tr_in.daemon = True
tr_in.start()

##--<3>-- запомнить время запуска
time_stamp = get_timems()

##==<3>== главная функция, запускаемая в цикле 
def main():
    global ls_in
    global busy_in
    global time_stamp
    global HOST_OUT

    flg_partnchange = 0   #-- сбросить признак изменения списка пратнеров 
    my_nick = var_nick.get()
    if len( ls_in ) > 0:
        #-- аккуратно извлечь сообщение из очереди
        while busy_in:
            sleep(0.001)
        busy_in = 2
        mess_in = ls_in.pop(0)
        busy_in = 0
        #-- вывести его в поле приема
        lst_mess = mess_in.split("|")
                
        mess_ip, mess_nick, dest_nick, mess_data, mess_time = lst_mess  #--<3>--
        print( mess_ip, mess_nick, dest_nick, mess_data, mess_time) 
        mess_time = int(mess_time)
        if mess_nick != my_nick:
            
            if mess_data != "%*%" :
                text_in = "\n(  " + mess_nick + "  >>>>  ):    " + mess_data 
                tbx_mess.insert(END, text_in )
                    
            ##--<3>-- найти партнера в списке по IP 
            sel_num = -1
            for num, partn in enumerate(lst_partn):
                if partn[1] == mess_ip and partn[0] == mess_nick:
                    lst_partn[num] = (partn[0], partn[1], mess_time) 
                    sel_num = num
                    break
            ##--<3>-- добавить, если не нашли
            if sel_num < 0:
                lst_partn.append( (mess_nick, mess_ip, mess_time) )
                flg_partnchange = 1
                        
    ##--<3>-- проверить время и удалить выключенные записи
    cur_time = get_timems()
    for num in range(len(lst_partn)-1,-1,-1):
        if lst_partn[num][2] == -1:  #-- запрещаем удалять all
            continue
        if cur_time > lst_partn[num][2] + 3*partn_tau:
            del lst_partn[num]
            flg_partnchange = 1

    ##--<3>-- показать изменения списка партнеров
    if flg_partnchange == 1:
        lbx_partn.delete(0,END)
        for partn in lst_partn:
            lbx_partn.insert( END, partn[0] )

        lbx_partn.selection_set(0)
        partn = lbx_partn.get(0)
        var_partn.set(partn)
        HOST_OUT = "255.255.255.255"
                        
    ##--<3>-- отправить всем пустое сообшение
    if cur_time - time_stamp >= partn_tau:
        time_stamp = cur_time

        if not my_nick:
            my_nick = simpledialog.askstring("замечание","введите Ваш ник ")
            var_nick.set(my_nick)
        
        mess =  my_nick + "|all|%*%"
        send_mess(mess, "255.255.255.255")
        sleep(0.005)
                
    root.after(main_tau, main)
    
main()

#== запустить обработку событий 
root.mainloop()

#==<2>== закрыть сокеты по завершению программы
uCliSock.close()

