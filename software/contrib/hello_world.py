from time import sleep
from europi import oled
from europi_script import EuroPiScript


class HelloWorld(EuroPiScript):
    def __init__(self):
        super().__init__()
        self.counter = 0

    @classmethod
    def display_name(cls):
        return "Hello World"

    @staticmethod
    def increment(counter):
        return counter + 1

    def main(self):
        while True:
            oled.centre_text(f"Hello world\n{self.counter}")

            self.counter = self.increment(self.counter)

            sleep(1)


if __name__ == "__main__":
    HelloWorld().main()
