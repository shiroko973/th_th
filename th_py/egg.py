def main_egg_input():
    egg_py = input("base: ")
    if egg_py == "dGggbmLvvIEg5oGt5Zac5L2g5oiQ5Yqf5Y+R546w5LqG5LiA5Liq5b2p6JuL":
        print("我去，你居然还真解开了")
        print("好吧，这毕竟是一个base，没有加密性")
        print("但能走到这一步，说明你很细心")
    else:
        print("不对")

def Chinese_Error_py():
    print("试试 Chinese_Error 这个模块")
    print("pip install Chinese_Error")

    try:
        import Chinese_Error as ce
        ce.enable()
        print("感谢安装，现在来看效果 ↓")
        print(未定义变量)
    except ImportError:
        print("未检测到 Chinese_Error，效果无法展示")