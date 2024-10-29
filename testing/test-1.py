class Test:
    def __init__(self, name):
        self.name = name
    def greet(self):
        print(f'Hello, {self.name}!')
    def bye(self):
        print("Bye, " + self.name)
    def is_lie(self, lie: bool):
        if lie:
            print("You're lying!")
        else:
            print("You're not lying!")
        print("L" if lie == True else "T")

if __name__ == "__main__":
    MyTest = Test('World')
    MyTest.greet()
    MyTest.bye()