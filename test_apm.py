import unittest
from loggerqos3 import ApmHelper

class TestCalc(unittest.TestCase):

  def setUp(self):

    self.apm_helper = ApmHelper("http://localhost:8200", "unittest1")

    class X():
      def __init__(self):
        self.x = 1
        self.y = 1

      @self.apm_helper.timeit
      def decoratored(self,z):
        return self.x + self.y + z

      @self.apm_helper.timeit_custom_naming("custom function name")
      def decoratored_with_param(self,z):
        return self.x + self.y + z

    self.X = X()

  def tearDown(self):
    pass

  def test_standalone(self):

    @self.apm_helper.timeit
    def func1():
      return True

    self.assertEqual(func1(), True)
  
  def test_standalone_with_param(self):

    @self.apm_helper.timeit_custom_naming("custom function name")
    def func1():
      return True

    self.assertEqual(func1(), True)


  def test_in_class(self):
    self.assertEqual(self.X.decoratored(1), 3)
  
  def test_in_class_with_param(self):
    self.assertEqual(self.X.decoratored_with_param(1), 3)

if __name__ == '__main__':
    unittest.main()