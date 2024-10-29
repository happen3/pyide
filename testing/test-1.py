class Test:
    def __init__(self, name):
        self.name = name
    def greet(self):
        print(f'Hello, {self.name}!')
    def bye(self):
        print("Bye, " + self.name)

if __name__ == "__main__":
    MyTest = Test('World')
    MyTest.greet()
    MyTest.bye()