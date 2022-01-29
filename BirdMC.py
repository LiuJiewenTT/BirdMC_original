from threading import Thread
import multiprocessing
import cv2
import numpy as np
import time
import sys
import os

multiprocessing.freeze_support()

# 输出提示信息：
infos = ["One Picture a time!", "Author: 刘杰文", "Email:liuljwtt@foxmail.com"]
print('INFOs: ')
for i in infos:
    print(i)
print("")

# 检查参数有效
def validx(strx):
    strx = strx.lower()
    xlst = ['png', 'jpg', 'jpeg', 'jpe', 'tif', 'tiff', 'bmp', 'dib', 'pbm', 'pgm', 'ppm', 'sr', 'ras', 'exr', 'jp2']
    for i in xlst:
        if strx == i:
            return True
    return False


bird_img = 'bird.png'
# 每次启动只能处理一张图片
# 启动参数
saveDelaytime = 100  # -sdt. 单位：ms
quitAferSave = False    # -qas

# 准备启动参数
LPinfos = [["-help", "Show help messages."],
           ["-sdt", "set saveDelaytime used in the animation of saving. Measured in (ms). Default: 100"],
           ["-qas", "Whether to quit immediately after saving. Value: True or False. Default: False"],
           ["Last", "Last parameter is fixed for image path. ONLY ONE PICTURE!"]]
LPinfos = dict(LPinfos)
# 获取分隔符
divd = ('\\' if os.name == 'nt' else '/')
# 获取工作目录
wkp = ""
if divd == '\\':
    wkp1 = sys.argv[0].replace("/", "\\")
    wkp2 = wkp1.split(sep=divd)
    wkp = wkp2[0]
    for i in wkp2[1:-1]:
        wkp = wkp + divd + i
# 获取处理对象
last_arg = sys.argv[len(sys.argv) - 1]
# 检验扩展名
filename = ""
if validx(last_arg.split(sep='.')[-1]) is True:
    # 合法
    # 设置对象
    bird_img = last_arg
    # 记录文件名
    filename = last_arg.split(sep=divd)[-1]
else:
    filename = bird_img
# 获取无后缀文件名
fnn1 = filename.split(sep='.')
fnn = fnn1[0]
for i in fnn1[1:-1]:
    fnn = fnn + '.' + i
# 检验输出目录是否存在
is_OPe = os.path.exists(wkp+divd+"output")
if not is_OPe:
    os.mkdir(wkp+divd+"output")
# 处理其他启动参数
def proc_LPs():
    global quitAferSave, saveDelaytime
    n_max = len(sys.argv) - 1
    if n_max > 2:
        for i in range(1, n_max):
            if sys.argv[i] == "-qas":
                if sys.argv[i+1] == "help":
                    print(sys.argv[i], LPinfos[sys.argv[i]])
                else:
                    quitAferSave = (True if sys.argv[i+1] == "True" else False)
            elif sys.argv[i] == "-sdt":
                if sys.argv[i + 1] == "help":
                    print(sys.argv[i], LPinfos[sys.argv[i]])
                else:
                    saveDelaytime = eval(sys.argv[i+1])
            elif sys.argv[i] == "-help":
                for i in LPinfos:
                    print(i, LPinfos[i])
                print("")
proc_LPs()
# 输出预处理结果
print(fnn)
print(bird_img)
print(f'file name: {filename}')
print(f'Working path: {wkp}')
print(f'{"output dir DOES NOT exist" if not is_OPe else "Dirs exist."}')


# 载入图像，不改动此图像，作为备份。
imgviewx = cv2.imread(bird_img)
# 复制图像，只对该图像进行操作。
img2 = imgviewx.copy()
# 获取尺寸和通道数。尺寸以[h,w]/[y,x]方式返回。
shape = imgviewx.shape
print(shape[1::-1], shape[2])  # 以[w,h]/[x,y]方式呈现
# 计算最多能有多少区块
w_max = shape[1] // 128
h_max = shape[0] // 128
print(128, f'[{w_max},{h_max}]')  # [x,y]形式呈现
# 选择区域
pos1 = []
pos2 = []
chklstt = []
y_inv = x_inv = 1
is_LBd = False
is_wd1_OFF = False


def saveDis(n):
    global pos1, pos2
    res_tmp1 = chklstt[:n]
    res_tmp2 = chklstt[n:]
    print('res_tmp1 len: ', len(res_tmp1))
    resVt = imgviewx.copy()
    for i in res_tmp1:
        # print(i)
        pos1 = i[0]
        ret = selectf(i[1][0], i[1][1], doinv=False, res=resVt)
        # cv2.waitKey(1)
        resVt = ret[1]
    for i in res_tmp2:
        pos1 = i[0]
        ret = selectf(i[1][0], i[1][1], doinv=True, res=resVt)
        # cv2.waitKey(1)
        resVt = ret[1]
    cv2.waitKey(saveDelaytime)
    # time.sleep(1)

def saveChks():
    n = 0
    for pt1, pt2 in chklstt:
        n = n + 1
        print(f'Saving image chunk {n} ....')
        patht = wkp+divd+"output"+divd+fnn+str(n)+'.'+fnn1[-1]
        print(patht)
        cv2.imwrite(patht, imgviewx[pt1[1]:pt2[1], pt1[0]:pt2[0]])
        saveDis(n)
        # time.sleep(1)
    if not quitAferSave:
        print(f'Finish saving {n} images.\nPress Esc or Click x-Button to quit.')
    else:
        print(f'Finish saving {n} images.\nquitAfterSave is set to True. Quitting....')
        cv2.destroyAllWindows()


def thd1f():
    global img2, is_wd1_OFF
    # 设定窗口，名称/标题；大小适应图像，不可伸缩。
    cv2.namedWindow('Bird', cv2.WINDOW_AUTOSIZE)
    # 设置鼠标响应事件处理函数
    cv2.setMouseCallback('Bird', wd1Callback)
    cv2.imshow('Bird', img2)
    # 避免x关闭窗口后继续运行（死循环，主线程等待、不退出）
    while not is_wd1_OFF:
        # waitKey()必须与imshow()连用，否则不显示图像；64位机需要加0xFF。
        k = (cv2.waitKey(0) & 0xFF)
        # 27 is Esc, 13 is Enter, 10 is Shift
        if (k == 27) or (cv2.getWindowProperty('Bird', cv2.WND_PROP_VISIBLE) < 1):
            is_wd1_OFF = True
            cv2.destroyAllWindows()
        elif k == 13:
        # elif k == ord('s') or k == ord('S'):
            # Save chunk images
            print(f'pos1 is {pos1} and pos2 is {pos2}')
            saveChks()


def srt1(x, y):
    return [y, x] if y < x else [x, y]
    # if x>y:
    #     return [y,x]
    # else:
    #     return [x,y]


def selectf(x, y, doinv=True, res=imgviewx):
    global img2, pos1, pos2, y_inv, x_inv
    ret = []
    i_pre = j_pre = i3 = j3 = 0
    if pos1 == []:
        print('pos1 is empty')
        return
    # 准备选区坐标，并处理（按大小排序）。
    pos_t = [[pos1[1], y], [pos1[0], x]]
    if pos_t[0][0] > pos_t[0][1]:
        pos_t[0] = pos_t[0][::-1]
        y_inv = -1
    else:
        y_inv = 1
    if pos_t[1][0] > pos_t[1][1]:
        pos_t[1] = pos_t[1][::-1]
        x_inv = -1
    else:
        x_inv = 1

    try:
        # 复制指定区域原图像
        img_t = res[pos_t[0][0]:pos_t[0][1], pos_t[1][0]:pos_t[1][1]].copy()
        # img_t = imgviewx[pos_t[1]:y, pos_t[0]:x].copy()
        if doinv:
            img_t = cv2.bitwise_not(img_t)
        # else:
        #     print('no inv')

        # 保存改动准备下一步
        img2 = res.copy()
        if doinv:
            img2[pos_t[0][0]:pos_t[0][1], pos_t[1][0]:pos_t[1][1]] = img_t.copy()
            # img2[pos_t[1]:y, pos_t[0]:x] = img_t.copy()

        # 绘制分块
        # 设定边界限制和预处理
        if y_inv > 0:
            j_pre = pos_t[0][0]
            j_lim = pos_t[0][1]
        else:
            j_pre = pos_t[0][1]
            j_lim = pos_t[0][0]

        # 绘制区块边界
        for j in range(1, h_max + 1):
            # 重置i_pre
            if x_inv > 0:
                i_pre = pos_t[1][0]
                i_lim = pos_t[1][1]
            else:
                i_pre = pos_t[1][1]
                i_lim = pos_t[1][0]

            j2 = j * 128 * y_inv
            # 确定本行
            if y_inv > 0:
                j3 = pos_t[0][0] + j2
            else:
                j3 = pos_t[0][1] + j2
            # 越界检查
            if j3 * y_inv > j_lim * y_inv:
                break
            for i in range(1, w_max + 1):
                i2 = i * 128 * x_inv
                # 确定本列
                if x_inv > 0:
                    i3 = pos_t[1][0] + i2
                else:
                    i3 = pos_t[1][1] + i2
                # 越界检查
                if i3 * x_inv > i_lim * x_inv:
                    break
                # print(f"ir:{i_pre},{i3}")
                # print(f"jr:{j_pre},{j3}")
                # 将BGR转为RGB
                img2[j3, i_pre:i3:x_inv, 0::1] = img2[j3, i_pre:i3:x_inv, 2::-1]
                jtc = (128 // 4 + int(128 % 4 != 0))
                # jtc = (i3-i_pre) * x_inv // 4
                img2[j3, i_pre:i3:(4 * x_inv), 0::1] = np.zeros([1, jtc, 3], np.uint8)
                img2[j3, i_pre:i3:(4 * x_inv), 0] = np.ones([1, jtc], np.uint8) * 255

                img2[j_pre:j3:y_inv, i3, 0::1] = img2[j_pre:j3:y_inv, i3, 2::-1]
                itc = (128 // 4 + int(128 % 4 != 0))
                # itc = (j3 - j_pre) * y_inv // 4
                img2[j_pre:j3:(4 * y_inv), i3, 0::1] = np.zeros([itc, 3], np.uint8)
                img2[j_pre:j3:(4 * y_inv), i3, 0] = np.ones([itc, ], np.uint8) * 255

                # 选取左上角和右下角坐标点
                lstt = [srt1(i_pre, i3), srt1(j_pre, j3)]
                ret.append([[lstt[0][0], lstt[1][0]], [lstt[0][1], lstt[1][1]]])

                # print(f"ib:{i_pre},{i3}")
                i_pre = i3
                # print(f"ia:{i_pre},{i3}")
            # print(f"jb:{j_pre},{j3}")
            j_pre = j3
            # print(f"ja:{j_pre},{j3}")
        # 完成变动，显示！
        cv2.imshow('Bird', img2)
    except AttributeError as ae:
        # 目前似乎是“失去一个维度”才会触发，然而不可避免（没必要），所以保留错误处理代码。
        print('！pos_t=', pos_t, end='')
        print(ae)
    except ValueError as ve:
        print('i_pre=', i_pre, 'i3=', i3, 'x_inv', x_inv, 'j_pre', j_pre, 'j3', j3, 'y_inv', y_inv)
        print(ve)
    if res is not imgviewx:
        return ret, img2
    else:
        return ret


def wd1Callback(event, x, y, flags, param):
    global pos1, pos2, is_LBd, img2, imgviewx, chklstt
    if event == cv2.EVENT_LBUTTONDOWN:
        print('mouse down at: ', x, y)
        pos1 = [x, y]
        is_LBd = True
    elif event == cv2.EVENT_LBUTTONUP:
        print('mouse up at: ', x, y)
        pos2 = [x, y]
        is_LBd = False
        chklstt = selectf(x, y)
        # print(chklstt[-1])
        x = chklstt[-1][1 if x_inv > 0 else 0][0]
        y = chklstt[-1][1 if y_inv > 0 else 0][1]
        selectf(x, y)
        print(f'{len(chklstt)} chunks are selected.')
    elif event == cv2.EVENT_MOUSEMOVE:
        # 移动：处理选区
        # print('mouse is moving')
        # 仅当pos1设置时开始选择
        if is_LBd == True:
            selectf(x, y)

    # 右键取消/清除选区
    if event == cv2.EVENT_RBUTTONDOWN:
        print('RBCd')
        print('Selection is clear now')
        pos1 = []
        pos2 = []
        img2 = imgviewx.copy()
        cv2.imshow('Bird', img2)


# 为显示图像和选定区域另开线程。
thd1 = Thread(target=thd1f, name='thd1')
thd1.start()

# 主线程
# wd1显示，反馈。
while not is_wd1_OFF:
    print('Window 1 is ON')
    time.sleep(1)
print('Window 1 is OFF, shutting down....')
