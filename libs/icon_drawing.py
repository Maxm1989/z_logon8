"""Icon drawing module - 图标绘制模块"""
import tkinter as tk


def create_folder_closed_icon(size=16):
    """创建关闭的文件夹图标，返回PhotoImage对象"""
    img = tk.PhotoImage(width=size, height=size)
    
    # 绘制文件夹身体
    for x in range(2, size-2):
        for y in range(4, size-2):
            img.put("#FFB84D", (x, y))  # 橙黄色
    
    # 绘制边框
    for x in range(2, size-2):
        img.put("#E69500", (x, 4))  # 上边框
        img.put("#E69500", (x, size-3))  # 下边框
    for y in range(4, size-2):
        img.put("#E69500", (2, y))  # 左边框
        img.put("#E69500", (size-3, y))  # 右边框
    
    # 绘制顶部标签
    for x in range(2, size-2):
        for y in range(1, 4):
            if y == 1:  # 顶部线
                img.put("#E69500", (x, y))
            elif y == 2:  # 中间填充
                img.put("#FFD966", (x, y))
            elif y == 3 and (x <= 5 or x >= size-5):  # 两边竖线
                img.put("#E69500", (x, y))
    
    return img


def create_folder_open_icon(size=16):
    """创建打开的文件夹图标，返回PhotoImage对象"""
    img = tk.PhotoImage(width=size, height=size)
    
    # 绘制文件夹身体
    for x in range(2, size-2):
        for y in range(5, size-2):
            img.put("#FFB84D", (x, y))
    
    # 绘制边框
    for x in range(2, size-2):
        img.put("#E69500", (x, 5))  # 上边框
        img.put("#E69500", (x, size-3))  # 下边框
    for y in range(5, size-2):
        img.put("#E69500", (2, y))  # 左边框
        img.put("#E69500", (size-3, y))  # 右边框
    
    # 绘制打开的标签部分
    # 左侧标签
    for x in range(2, 8):
        for y in range(2, 5):
            if y == 2:  # 顶部线
                img.put("#E69500", (x, y))
            elif y == 3:  # 中间填充
                img.put("#FFD966", (x, y))
            elif y == 4 and (x == 2 or x == 7):  # 两边竖线
                img.put("#E69500", (x, y))
    
    # 右侧标签
    for x in range(size-8, size-2):
        for y in range(2, 5):
            if y == 2:  # 顶部线
                img.put("#E69500", (x, y))
            elif y == 3:  # 中间填充
                img.put("#FFD966", (x, y))
            elif y == 4 and (x == size-8 or x == size-3):  # 两边竖线
                img.put("#E69500", (x, y))
    
    return img


def create_link_icon(size=16):
    """创建连接图标：插头造型，返回PhotoImage对象"""
    img = tk.PhotoImage(width=size, height=size)
    
    # 绘制插头主体（矩形）
    for x in range(3, size-3):
        for y in range(2, size-6):
            img.put("#81C784", (x, y))  # 浅绿色
    
    # 绘制插头边框
    for x in range(3, size-3):
        img.put("#4CAF50", (x, 2))  # 上边框
        img.put("#4CAF50", (x, size-7))  # 下边框
    for y in range(2, size-6):
        img.put("#4CAF50", (3, y))  # 左边框
        img.put("#4CAF50", (size-4, y))  # 右边框
    
    # 绘制两个插脚
    for x in range(5, 7):
        for y in range(size-6, size-2):
            img.put("#4CAF50", (x, y))  # 左插脚
    for x in range(size-7, size-5):
        for y in range(size-6, size-2):
            img.put("#4CAF50", (x, y))  # 右插脚
    
    return img


def draw_eye_icon(canvas, closed=False):
    """绘制眼睛图标到Canvas上"""
    # 清除画布
    canvas.delete("all")
    
    if closed:
        # 密码隐藏状态 - 画一个闭合的眼睛
        # 眼睛外轮廓
        canvas.create_oval(3, 5, 17, 15, outline='#4A90E2', width=1.5)
        # 内部弧形
        canvas.create_oval(6, 7, 14, 13, outline='#7FBCEB', width=1)
        # 斜杠，使用深灰色更接近黑色
        canvas.create_line(16, 6, 4, 14, fill='#666666', width=1.8, capstyle=tk.ROUND)
    else:
        # 密码可见状态 - 画一个睁开的眼睛
        # 眼睛外轮廓
        canvas.create_oval(3, 5, 17, 15, outline='#4A90E2', width=1.5)
        # 眼珠 - 使用深蓝色
        canvas.create_oval(8, 7, 12, 13, fill='#2C6FC8', outline='#2C6FC8')
        # 反光点
        canvas.create_oval(9, 8, 10, 9, fill='white', outline='white')
