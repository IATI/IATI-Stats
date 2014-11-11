from decimal import Decimal
from statsrunner.common import decimal_default
import json

def test_decimal_default():
    assert json.dumps(Decimal('1.1'), default=decimal_default) == '1.1'
    assert json.dumps(Decimal('42'), default=decimal_default) == '42'
