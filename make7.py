import os
from collections import namedtuple
from itertools import cycle

import ctypes  
import sys

'''Windows CMD命令行颜色'''

# 句柄号
STD_INPUT_HANDLE = -10  
STD_OUTPUT_HANDLE= -11  
STD_ERROR_HANDLE = -12  

# 前景色
FOREGROUND_BLACK    = 0x0 # 黑
FOREGROUND_BLUE     = 0x01 # 蓝
FOREGROUND_GREEN    = 0x02 # 绿
FOREGROUND_RED      = 0x04  # 红
FOREGROUND_INTENSITY = 0x08 # 加亮

# 背景色
BACKGROUND_BLUE     = 0x10 # 蓝
BACKGROUND_GREEN    = 0x20 # 绿
BACKGROUND_RED      = 0x40  # 红
BACKGROUND_INTENSITY = 0x80 # 加亮

colors = [FOREGROUND_BLUE, # 蓝字
          FOREGROUND_GREEN,# 绿字
          FOREGROUND_RED,  # 红字
          FOREGROUND_BLUE  | FOREGROUND_INTENSITY, # 蓝字(加亮)
          FOREGROUND_GREEN | FOREGROUND_INTENSITY, # 绿字(加亮)
          FOREGROUND_RED   | FOREGROUND_INTENSITY, # 红字(加亮)
          FOREGROUND_RED | FOREGROUND_INTENSITY| BACKGROUND_BLUE | BACKGROUND_INTENSITY] # 红字蓝底
          
texts = ['蓝字',
         '绿字',
         '红字',
         '蓝字(加亮)',
         '绿字(加亮)',
         '红字(加亮)',
         '红字蓝底']
          
# See "http://msdn.microsoft.com/library/default.asp?url=/library/en-us/winprog/winprog/windows_api_reference.asp" for information on Windows APIs.
  
std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)  
      
def set_cmd_color(color, handle=std_out_handle):  
    bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)  
    return bool  
      
def reset_color():  
    set_cmd_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE) 

class Level:
    def __init__(self):
        self.level = [[('', 0) for i in range(7)] for i in range(7)]
        self.three_poses = [(2, 0), (4, 1), (5, 2), (3, 3), (5, 4), (4, 5), (2, 6)]
        self.players = ['玩家1', '玩家2']
        self.player_colors = [FOREGROUND_RED, FOREGROUND_BLUE]
        self.color_dict = dict(zip(self.players, self.player_colors))

    def is_full(self):
        if all(i[0] for j in self.level for i in j):
            return True

    def is_finish(self):
        for i in range(7):
            for j in range(7):
                for h_value in [-1, 0, 1]:
                    for v_value in [-1, 0, 1]:
                        if not h_value and not v_value:
                            continue
                        def calc_itor(i, j, h_value, v_value):
                            player, sum_ = self.level[i][j]
                            if not player:
                                return
                            while True:
                                yield sum_
                                i += h_value
                                j += v_value
                                if i < 0 or i >= 7 or j < 0 or j >= 7:
                                    return
                                player_, value = self.level[i][j]
                                if player_ != player:
                                    return
                                sum_ += value
                        for value in calc_itor(i, j, h_value, v_value):
                            if value == 7:
                                return True
        return False

    def print_to_cmd(self):
        os.system('cls')
        for i in range(7):
            for j in range(7):
                player, value = self.level[6 - i][j]
                color = self.color_dict.get(player, FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE)
                if not player and (6 - i, j) in self.three_poses:
                    color = FOREGROUND_GREEN
                set_cmd_color(color)
                print(value, end=' ', flush=True)
            reset_color()
            print(flush=True)
        print('------------------------------------')
        print('红色为玩家1, 蓝色为玩家2, 绿色为可以填3的位置')

    def player_input(self, player):
        value = input('>>> [%s]请输入列数, 范围1-7\n' % player)
        j = int(value) - 1
        assert 0 <= j < 7, '列数超过范围, 请重新选择'
        for i in range(7):
            player_, _ = self.level[i][j]
            if not player_:
                max_value = 3 if (i, j) in self.three_poses else 2
                value = input('>>> [%s]请输入你想输入的数, 范围1-%d\n' % (player, max_value))
                v = int(value)
                assert 1 <= v <= max_value, '输入超过范围, 请重新选择'
                self.level[i][j] = (player, v)
                return
        raise AssertionError('这一列满了, 请重新选择')

def main():
    level = Level()
    players = level.players
    player_itor = cycle(players)
    level.print_to_cmd()
    while not level.is_full():
        current_player = next(player_itor)
        while True:
            try:
                level.player_input(current_player)
            except AssertionError as ex:
                print(str(ex))
            except Exception:
                print('输入不合法, 请重新输入')
            else:
                break
        level.print_to_cmd()
        if level.is_finish():
            print('胜者是%s' % current_player)
            return
    print('棋盘满了, 平局')

if __name__ == '__main__':
    main()
