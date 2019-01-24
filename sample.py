from loggerqos3 import Logger

qos3_logger=Logger("test1.log", "http://localhost:8200")

# from loggerqos3 import ApmHelper

import time

# apm_helper=ApmHelper("http://localhost:8200", "from_sample")



@qos3_logger.timeit
def standalone_function():
    time.sleep(0.5)
    print("timed fucntion !")

standalone_function()


@qos3_logger.timeit_name("standalone_function_named_true")
def standalone_function_named():
    time.sleep(0.5)
    print("timed fucntion named !")

standalone_function_named()


qos3_logger.info("script started")

try:
    x=int("five")
except ValueError as err:
    qos3_logger.error("integer error ",err)

# apm_helper.info("blablabla")


class AAA():
    def __init__(self):
        self.x=1
        self.y=1

    @qos3_logger.timeit
    def from_class(self, z):
        print(self.x+self.y+z, "from_class")

    @qos3_logger.timeit_name("from_class_named_true")
    def from_class_named(self, z):
        print(self.x+self.y+z,"from_class_named")

a=AAA()
a.from_class(1)
a.from_class_named(1)
