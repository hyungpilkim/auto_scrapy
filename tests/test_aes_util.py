import os
import sys
import pytest

import aes_util
import qt_gui
from collections import namedtuple

class TestClass():
    @pytest.fixture
    def aes_util(self):
        aes_manager = aes_util.AesUtil()
        yield aes_manager

    def test_aes(self, aes_util):  
        plain = 'ganadara'
        print('plain', plain)
        encrypt = aes_util.encrypt(plain)
        print('encrypt', encrypt)
        decrypt = aes_util.decrypt(encrypt)
        print('decrypt type', type(decrypt))
        print('decrypt', decrypt)
        assert plain == decrypt