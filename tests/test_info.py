from tests import reader


def test_get_manufacturer():
    manufacturer = reader.get_info_manufacturer()
    assert manufacturer == 'PHYCHIPS'


def test_get_model():
    model = reader.get_info_model()
    assert model == 'R4S5U1DK-E'


def test_get_details():
    details = reader.get_info_detail()
    assert details.max_tx_power == 27
    assert details.min_tx_power == 13
