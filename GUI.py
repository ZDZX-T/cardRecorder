import tkinter
import threading
import time
import pyautogui

# 窗口
root = tkinter.Tk()
root.wm_attributes('-topmost', 1)
root.title('TZ记牌器')
root.geometry('280x150')
root.resizable(0, 0)
lamp = tkinter.Button(root, text=' ', width=3, height=1)
lamp.place(x=230, y=15)  # 状态指示灯

# 界面变量
alphaInEntry = tkinter.StringVar()
num_dw = tkinter.StringVar()  # 大王
num_xw = tkinter.StringVar()  # 小王
num_2 = tkinter.StringVar()  # 2
num_A = tkinter.StringVar()  # A
num_K = tkinter.StringVar()  # K
num_Q = tkinter.StringVar()  # Q
num_J = tkinter.StringVar()  # J
num_10 = tkinter.StringVar()  # 10
num_9 = tkinter.StringVar()  # 9
num_8 = tkinter.StringVar()  # 8
num_7 = tkinter.StringVar()  # 7
num_6 = tkinter.StringVar()  # 6
num_5 = tkinter.StringVar()  # 5
num_4 = tkinter.StringVar()  # 4
num_3 = tkinter.StringVar()  # 3

# 数据
cards = [0, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 1, 1]
# 牌     空  A  2  3  4  5  6  7  8  9  10 J  Q  K  小 大
myConfidence = 1  # 我的牌的置信度
otherConfidence = 1  # 别人的牌的置信度
whiteConfidence = 1  # 检测白块的置信度
waitTime = 1  # 等待状态稳定延时
myFilter = 40  # 我的牌检测结果过滤参数
otherFilter = 25  # 别人的牌检测结果过滤参数

# 坐标
myPos = (0, 0, 0, 0)  # 我的截图区域
lPos = (0, 0, 0, 0)  # 左边截图区域
rPos = (0, 0, 0, 0)  # 右边截图区域

# 信号量
shouldExit = 0  # 通知上一轮记牌结束
canRecord = threading.Lock()  # 开始记牌


def setAlpha():
    global alphaInEntry
    root.attributes('-alpha', float(alphaInEntry.get()))


def initial():
    global myPos, lPos, rPos, myConfidence, otherConfidence, whiteConfidence, waitTime, myFilter, otherFilter
    f = open('settings.txt', 'r', encoding='utf-8')
    alphaInEntry.set(f.readline().split(' ')[0])  # 读取透明度
    my = f.readline().split(' ')
    myPos = (int(my[0]), int(my[1]), int(my[2]), int(my[3]))
    left = f.readline().split(' ')
    lPos = (int(left[0]), int(left[1]), int(left[2]), int(left[3]))
    right = f.readline().split(' ')
    rPos = (int(right[0]), int(right[1]), int(right[2]), int(right[3]))
    myConfidence = float(f.readline().split(' ')[0])
    otherConfidence = float(f.readline().split(' ')[0])
    whiteConfidence = float(f.readline().split(' ')[0])
    waitTime = float(f.readline().split(' ')[0])
    myFilter = int(f.readline().split(' ')[0])
    otherFilter = int(f.readline().split(' ')[0])
    f.close()


def loadCardsNum():  # 显示牌的数目
    global cards, num_dw, num_xw, num_2, num_A, num_K, num_Q, num_J, num_10, num_9, num_8, num_7, num_6, num_5
    global num_4, num_3
    global lamp

    strCards = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
    # 牌         空  A   2   3   4   5   6   7   8   9   10  J   Q   K   小   大
    for i in range(16):
        if cards[i] == 0:
            strCards[i] = ''
        else:
            strCards[i] = str(cards[i])

    num_dw.set(strCards[15])
    num_xw.set(strCards[14])
    num_2.set(strCards[2])
    num_A.set(strCards[1])
    num_K.set(strCards[13])
    num_Q.set(strCards[12])
    num_J.set(strCards[11])
    num_10.set(strCards[10])
    num_9.set(strCards[9])
    num_8.set(strCards[8])
    num_7.set(strCards[7])
    num_6.set(strCards[6])
    num_5.set(strCards[5])
    num_4.set(strCards[4])
    num_3.set(strCards[3])

    lamp.config(background='springgreen')


def cardsFilter(location, distance):  # 牌检测结果滤波
    if len(location) == 0:
        return 0
    locList = [location[0][0]]
    count = 1
    for e in location:
        flag = 1  # “是新的”标志
        for have in locList:
            if abs(e[0]-have) <= distance:
                flag = 0
                break
        if flag:
            count += 1
            locList.append(e[0])
    return count


def findMyCards():
    global cards, lamp
    myCardsNum = {'rdw': 0,
                  'bxw': 0,
                  'b2': 0,
                  'r2': 0,
                  'bA': 0,
                  'rA': 0,
                  'bK': 0,
                  'rK': 0,
                  'bQ': 0,
                  'rQ': 0,
                  'bJ': 0,
                  'rJ': 0,
                  'b10': 0,
                  'r10': 0,
                  'b9': 0,
                  'r9': 0,
                  'b8': 0,
                  'r8': 0,
                  'b7': 0,
                  'r7': 0,
                  'b6': 0,
                  'r6': 0,
                  'b5': 0,
                  'r5': 0,
                  'b4': 0,
                  'r4': 0,
                  'b3': 0,
                  'r3': 0,
                  }
    lamp.config(background='red')
    img = pyautogui.screenshot(region=myPos)
    for i in myCardsNum.keys():
        result = pyautogui.locateAll(needleImage='pics\\m' + i + '.png', haystackImage=img, confidence=myConfidence)
        myCardsNum[i] = cardsFilter(list(result), myFilter)

    cards[1] -= myCardsNum['bA'] + myCardsNum['rA']
    cards[2] -= myCardsNum['b2'] + myCardsNum['r2']
    cards[3] -= myCardsNum['b3'] + myCardsNum['r3']
    cards[4] -= myCardsNum['b4'] + myCardsNum['r4']
    cards[5] -= myCardsNum['b5'] + myCardsNum['r5']
    cards[6] -= myCardsNum['b6'] + myCardsNum['r6']
    cards[7] -= myCardsNum['b7'] + myCardsNum['r7']
    cards[8] -= myCardsNum['b8'] + myCardsNum['r8']
    cards[9] -= myCardsNum['b9'] + myCardsNum['r9']
    cards[10] -= myCardsNum['b10'] + myCardsNum['r10']
    cards[11] -= myCardsNum['bJ'] + myCardsNum['rJ']
    cards[12] -= myCardsNum['bQ'] + myCardsNum['rQ']
    cards[13] -= myCardsNum['bK'] + myCardsNum['rK']
    cards[14] -= myCardsNum['bxw']
    cards[15] -= myCardsNum['rdw']


def findOtherCards(pos):  # 检测pos内的牌
    global cards, lamp
    print(pos)
    otherCardsNum = {'rdw': 0,
                     'bxw': 0,
                     'b2': 0,
                     'r2': 0,
                     'bA': 0,
                     'rA': 0,
                     'bK': 0,
                     'rK': 0,
                     'bQ': 0,
                     'rQ': 0,
                     'bJ': 0,
                     'rJ': 0,
                     'b10': 0,
                     'r10': 0,
                     'b9': 0,
                     'r9': 0,
                     'b8': 0,
                     'r8': 0,
                     'b7': 0,
                     'r7': 0,
                     'b6': 0,
                     'r6': 0,
                     'b5': 0,
                     'r5': 0,
                     'b4': 0,
                     'r4': 0,
                     'b3': 0,
                     'r3': 0,
                     }
    lamp.config(background='red')
    time.sleep(waitTime)
    img = pyautogui.screenshot(region=pos)
    for i in otherCardsNum.keys():
        result = pyautogui.locateAll(needleImage='pics\\o' + i + '.png', haystackImage=img, confidence=otherConfidence)
        otherCardsNum[i] = cardsFilter(list(result), otherFilter)
    cards[1] -= otherCardsNum['bA'] + otherCardsNum['rA']
    cards[2] -= otherCardsNum['b2'] + otherCardsNum['r2']
    cards[3] -= otherCardsNum['b3'] + otherCardsNum['r3']
    cards[4] -= otherCardsNum['b4'] + otherCardsNum['r4']
    cards[5] -= otherCardsNum['b5'] + otherCardsNum['r5']
    cards[6] -= otherCardsNum['b6'] + otherCardsNum['r6']
    cards[7] -= otherCardsNum['b7'] + otherCardsNum['r7']
    cards[8] -= otherCardsNum['b8'] + otherCardsNum['r8']
    cards[9] -= otherCardsNum['b9'] + otherCardsNum['r9']
    cards[10] -= otherCardsNum['b10'] + otherCardsNum['r10']
    cards[11] -= otherCardsNum['bJ'] + otherCardsNum['rJ']
    cards[12] -= otherCardsNum['bQ'] + otherCardsNum['rQ']
    cards[13] -= otherCardsNum['bK'] + otherCardsNum['rK']
    cards[14] -= otherCardsNum['bxw']
    cards[15] -= otherCardsNum['rdw']


def haveWhite(pos):  # 是否有白块
    result = pyautogui.locateOnScreen('pics\\white.png', region=pos, confidence=whiteConfidence)
    if result is None:
        return 0
    else:
        return 1


def stop():
    global shouldExit, lamp
    shouldExit = 1
    lamp.config(background='yellow')


def start():
    t = threading.Thread(target=startRecord)
    t.setDaemon(True)
    t.start()


def startRecord():  # 开始记牌
    global shouldExit, canRecord
    global cards

    print('\n', end='')
    shouldExit = 1
    canRecord.acquire()
    cards = [0, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 1, 1]  # 重置牌的数目
    findMyCards()
    loadCardsNum()
    shouldExit = 0
    lmod = 0  # 左边人上一次的状态，0代表没有出牌，1代表已经出牌
    rmod = 0  # 同理
    while not shouldExit:
        if rmod == 0 and haveWhite(rPos) == 1 and (not shouldExit):  # 右边的人刚才没出牌，现在出牌了
            findOtherCards(rPos)
            loadCardsNum()
            rmod = 1
        if rmod == 1 and haveWhite(rPos) == 0 and (not shouldExit):  # 右边人刚刚出牌了，现在牌没了
            rmod = 0
        if lmod == 0 and haveWhite(lPos) == 1 and (not shouldExit):  # 左边的人刚才没出牌，现在出牌了
            findOtherCards(lPos)
            loadCardsNum()
            lmod = 1
        if lmod == 1 and haveWhite(lPos) == 0 and (not shouldExit):  # 左边的人刚刚出牌了，现在牌没了
            lmod = 0
    canRecord.release()


if __name__ == '__main__':
    initial()  # 初始化

    # 设置透明度
    tkinter.Entry(root, textvariable=alphaInEntry, width=4).place(x=150, y=120)
    tkinter.Button(root, text='设置透明度', command=setAlpha).place(x=190, y=115)
    setAlpha()

    # 设置检测区域
    # tkinter.Button(root, text='设置检测区域', command=setScanArea).place(x=20, y=115)

    # 开始记牌
    tkinter.Button(root, text='开始', command=start).place(x=100, y=115)

    # 停止记牌，调试用
    tkinter.Button(root, text='stop', font=('', 8), command=stop).place(x=5, y=125)

    # 显示
    x_start = 20
    y_start = 5
    x_add = 30
    x_dif = 2
    y_dif = 25
    tkinter.Label(root, text='大', font=('', 14), width=1).place(x=x_start, y=y_start)
    tkinter.Entry(root, textvariable=num_dw, font=('', 14), width=1).place(x=x_start + x_dif, y=y_start + y_dif)
    x_start += x_add
    tkinter.Label(root, text='小', font=('', 14), width=1).place(x=x_start, y=y_start)
    tkinter.Entry(root, textvariable=num_xw, font=('', 14), width=1).place(x=x_start + x_dif, y=y_start + y_dif)
    x_start += x_add
    tkinter.Label(root, text='2', font=('', 14), width=1).place(x=x_start, y=y_start)
    tkinter.Entry(root, textvariable=num_2, font=('', 14), width=1).place(x=x_start + x_dif, y=y_start + y_dif)
    x_start += x_add
    tkinter.Label(root, text='A', font=('', 14), width=1).place(x=x_start, y=y_start)
    tkinter.Entry(root, textvariable=num_A, font=('', 14), width=1).place(x=x_start + x_dif, y=y_start + y_dif)
    x_start += x_add
    tkinter.Label(root, text='K', font=('', 14), width=1).place(x=x_start, y=y_start)
    tkinter.Entry(root, textvariable=num_K, font=('', 14), width=1).place(x=x_start + x_dif, y=y_start + y_dif)
    x_start += x_add
    tkinter.Label(root, text='Q', font=('', 14), width=1).place(x=x_start, y=y_start)
    tkinter.Entry(root, textvariable=num_Q, font=('', 14), width=1).place(x=x_start + x_dif, y=y_start + y_dif)
    x_start += x_add
    tkinter.Label(root, text='J', font=('', 14), width=1).place(x=x_start, y=y_start)
    tkinter.Entry(root, textvariable=num_J, font=('', 14), width=1).place(x=x_start + x_dif, y=y_start + y_dif)
    x_start = 20
    y_start = 60
    tkinter.Label(root, text='10', font=('', 14), width=2).place(x=x_start - 5, y=y_start)
    tkinter.Entry(root, textvariable=num_10, font=('', 14), width=1).place(x=x_start + x_dif, y=y_start + y_dif)
    x_start += x_add
    tkinter.Label(root, text='9', font=('', 14), width=1).place(x=x_start, y=y_start)
    tkinter.Entry(root, textvariable=num_9, font=('', 14), width=1).place(x=x_start + x_dif, y=y_start + y_dif)
    x_start += x_add
    tkinter.Label(root, text='8', font=('', 14), width=1).place(x=x_start, y=y_start)
    tkinter.Entry(root, textvariable=num_8, font=('', 14), width=1).place(x=x_start + x_dif, y=y_start + y_dif)
    x_start += x_add
    tkinter.Label(root, text='7', font=('', 14), width=1).place(x=x_start, y=y_start)
    tkinter.Entry(root, textvariable=num_7, font=('', 14), width=1).place(x=x_start + x_dif, y=y_start + y_dif)
    x_start += x_add
    tkinter.Label(root, text='6', font=('', 14), width=1).place(x=x_start, y=y_start)
    tkinter.Entry(root, textvariable=num_6, font=('', 14), width=1).place(x=x_start + x_dif, y=y_start + y_dif)
    x_start += x_add
    tkinter.Label(root, text='5', font=('', 14), width=1).place(x=x_start, y=y_start)
    tkinter.Entry(root, textvariable=num_5, font=('', 14), width=1).place(x=x_start + x_dif, y=y_start + y_dif)
    x_start += x_add
    tkinter.Label(root, text='4', font=('', 14), width=1).place(x=x_start, y=y_start)
    tkinter.Entry(root, textvariable=num_4, font=('', 14), width=1).place(x=x_start + x_dif, y=y_start + y_dif)
    x_start += x_add
    tkinter.Label(root, text='3', font=('', 14), width=1).place(x=x_start, y=y_start)
    tkinter.Entry(root, textvariable=num_3, font=('', 14), width=1).place(x=x_start + x_dif, y=y_start + y_dif)
    root.mainloop()
