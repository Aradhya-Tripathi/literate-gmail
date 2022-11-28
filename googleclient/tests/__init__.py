from unittest import TestCase
import os


class BaseTestClass(TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        os.environ["CI"] = "True"
