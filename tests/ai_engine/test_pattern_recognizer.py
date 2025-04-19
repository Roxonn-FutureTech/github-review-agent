import unittest
from unittest.mock import patch, MagicMock
import ast
from src.ai_engine.pattern_recognizer import PatternRecognizer

class TestPatternRecognizer(unittest.TestCase):
    def setUp(self):
        self.recognizer = PatternRecognizer()

    def test_recognize_design_patterns(self):
        test_content = """
class Singleton:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class Factory:
    @classmethod
    def create(cls, type):
        if type == "A":
            return ProductA()
        return ProductB()
"""
        ast_tree = ast.parse(test_content)
        patterns = self.recognizer.recognize_design_patterns(ast_tree)
        
        self.assertIn("singleton", patterns)
        self.assertIn("factory", patterns)

    def test_recognize_code_smells(self):
        test_content = """
class LongClass:
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
    def method6(self): pass
    def method7(self): pass
    def method8(self): pass
    def method9(self): pass
    def method10(self): pass

def long_parameter_list(a, b, c, d, e, f, g, h):
    pass
"""
        ast_tree = ast.parse(test_content)
        smells = self.recognizer.recognize_code_smells(ast_tree)
        
        self.assertIn("large_class", smells)
        self.assertIn("long_parameter_list", smells)

    def test_recognize_security_patterns(self):
        test_content = """
password = "hardcoded_password"
sql_query = "SELECT * FROM users WHERE id = " + user_id
exec(user_input)
"""
        ast_tree = ast.parse(test_content)
        security_issues = self.recognizer.recognize_security_patterns(ast_tree)
        
        self.assertIn("hardcoded_credentials", security_issues)
        self.assertIn("sql_injection", security_issues)
        self.assertIn("code_execution", security_issues)

    def test_recognize_performance_patterns(self):
        test_content = """
def inefficient_function():
    result = []
    for i in range(1000):
        result = result + [i]  # Inefficient list concatenation
        
    data = {}
    for key in data.keys():  # Inefficient dictionary iteration
        print(key)
"""
        ast_tree = ast.parse(test_content)
        performance_issues = self.recognizer.recognize_performance_patterns(ast_tree)
        
        self.assertIn("inefficient_list_usage", performance_issues)
        self.assertIn("inefficient_dict_iteration", performance_issues)

    def test_recognize_best_practices(self):
        test_content = """
def function():
    pass  # Missing docstring

class MyClass:  # Missing docstring
    pass

def unused_parameter(param):
    return 42
"""
        ast_tree = ast.parse(test_content)
        practices = self.recognizer.recognize_best_practices(ast_tree)
        
        self.assertIn("missing_docstring", practices)
        self.assertIn("unused_parameter", practices)

    def test_analyze_complexity_patterns(self):
        test_content = """
def complex_function(x):
    result = 0
    for i in range(10):
        for j in range(10):
            for k in range(10):
                if x > 0:
                    if i > 5:
                        result += 1
    return result
"""
        ast_tree = ast.parse(test_content)
        complexity = self.recognizer.analyze_complexity_patterns(ast_tree)
        
        self.assertGreater(complexity["nested_loops"], 2)
        self.assertGreater(complexity["nested_conditions"], 1)
        self.assertGreater(complexity["cognitive_complexity"], 5)

    def test_pattern_matching(self):
        test_patterns = [
            {"type": "class", "name": "TestClass"},
            {"type": "function", "name": "test_function"}
        ]
        
        match = self.recognizer.match_patterns(test_patterns, "class", "TestClass")
        self.assertTrue(match)
        
        match = self.recognizer.match_patterns(test_patterns, "function", "nonexistent")
        self.assertFalse(match)

    def test_pattern_validation(self):
        patterns = self.recognizer.recognize_design_patterns(ast.parse(""))
        self.assertTrue(any(p['type'] == 'function_definition' for p in patterns))

    def test_analyze_code_patterns(self):
        test_content = """
class TestClass:
    def __init__(self):
        self._value = 0
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, new_value):
        self._value = new_value
"""
        ast_tree = ast.parse(test_content)
        patterns = self.recognizer.analyze_code_patterns(ast_tree)
        
        # Test property pattern detection
        property_patterns = [p for p in patterns if p['type'] == 'property_pattern']
        self.assertTrue(len(property_patterns) > 0)
        self.assertEqual(property_patterns[0]['name'], 'value')
        
        # Test encapsulation pattern detection
        encapsulation_patterns = [p for p in patterns if p['type'] == 'encapsulation_pattern']
        self.assertTrue(len(encapsulation_patterns) > 0)
        self.assertIn('_value', encapsulation_patterns[0]['private_members'])

    def test_analyze_design_patterns(self):
        test_content = """
class Singleton:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
"""
        ast_tree = ast.parse(test_content)
        patterns = self.recognizer.analyze_design_patterns(ast_tree)
        
        # Test singleton pattern detection
        singleton_patterns = [p for p in patterns if p['type'] == 'singleton_pattern']
        self.assertTrue(len(singleton_patterns) > 0)
        self.assertEqual(singleton_patterns[0]['class_name'], 'Singleton')

if __name__ == '__main__':
    unittest.main()
