from lib_box.shellController import Shell
from firebase.init import init_firebase_admin

quit_commands = {'q!', 'Q!', 'quit', 'QUIT', 'exit', 'EXIT', '\\q'}

def __main__():
    init_firebase_admin()
    try:
        shell = Shell()
        while True:
            try:
                command = input(shell.prompt)
                if len(command):
                    if command in quit_commands:
                        break
                    else:
                        shell.fetch(command)
            except:
                pass
    except Exception as e:
        print(e)


if __name__ == '__main__':
    __main__()
