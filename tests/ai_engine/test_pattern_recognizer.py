import unittest
from src.ai_engine.pattern_recognizer import PatternRecognizer
import ast

class TestPatternRecognizer(unittest.TestCase):
    def setUp(self):
        self.recognizer = PatternRecognizer()

    def test_analyze_class_patterns(self):
        code = '''
class MyClass:
    def __init__(self):
        self.value = 0
    
    def method(self):
        return self.value
'''
        tree = ast.parse(code)
        patterns = self.recognizer.analyze({'test.py': {'ast': tree, 'content': code}})
        
        self.assertTrue(any(p['type'] == 'class_definition' for p in patterns))
        self.assertTrue(any(p['type'] == 'method_definition' for p in patterns))

    def test_analyze_function_patterns(self):
        code = '''
def decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@decorator
def my_function():
    pass
'''
        tree = ast.parse(code)
        patterns = self.recognizer.analyze({'test.py': {'ast': tree, 'content': code}})
        
        self.assertTrue(any(p['type'] == 'decorator' for p in patterns))
        self.assertTrue(any(p['type'] == 'function_definition' for p in patterns))
