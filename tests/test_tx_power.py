from tests import reader


def test_correct_tx_power():
    reader.set_tx_power(15)
    assert reader.get_tx_power() == 15


def test_too_high_tx_power():
    reader.set_tx_power(50)
    assert reader.get_tx_power() != 50


def test_too_low_tx_power():
    reader.set_tx_power(0)
    assert reader.get_tx_power() != 0
