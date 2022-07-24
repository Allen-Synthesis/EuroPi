import pytest

from europi import AnalogueInput, MAX_UINT16

from mock_hardware import MockHardware


@pytest.fixture
def analogueInput():
    return AnalogueInput(pin=1)  # actual pin value doesn't matter

AIN_MX_IN = 64354
@pytest.mark.parametrize(
    "value, min_voltage, max_voltage, expected",
    [        
        (int(AIN_MX_IN/10*0), 0 , 12,0.0),
        (int(AIN_MX_IN/10*1), 0 , 12,1.2),
        (int(AIN_MX_IN/10*2), 0 , 12,2.4),
        (int(AIN_MX_IN/10*3), 0 , 12,3.6),
        (int(AIN_MX_IN/10*4), 0 , 12,4.8),
        (int(AIN_MX_IN/10*5), 0 , 12,6.0),
        (int(AIN_MX_IN/10*6), 0 , 12,7.2),
        (int(AIN_MX_IN/10*7), 0 , 12,8.4),
        (int(AIN_MX_IN/10*8), 0 , 12,9.6),
        (int(AIN_MX_IN/10*9), 0 , 12,10.8),
        (int(AIN_MX_IN/10*10), 0 , 12,12),

        (int(AIN_MX_IN/10*0),  -6 , 6, -6.0),
        (int(AIN_MX_IN/10*1),  -6 , 6, -4.8),
        (int(AIN_MX_IN/10*2),  -6 , 6, -3.6),
        (int(AIN_MX_IN/10*3),  -6 , 6, -2.4),
        (int(AIN_MX_IN/10*4),  -6 , 6, -1.2),
        (int(AIN_MX_IN/10*5),  -6 , 6, 0.0),
        (int(AIN_MX_IN/10*6),  -6 , 6, 1.2),
        (int(AIN_MX_IN/10*7),  -6 , 6, 2.4),
        (int(AIN_MX_IN/10*8),  -6 , 6, 3.6),
        (int(AIN_MX_IN/10*9),  -6 , 6, 4.8),
        (int(AIN_MX_IN/10*10), -6 , 6, 6.0),

    ],
)
def test_read_voltage(mockHardware: MockHardware, analogueInput, value, min_voltage, max_voltage, expected):    
    mockHardware.set_min_max_voltage(analogueInput, min_voltage, max_voltage)
    mockHardware.set_ADC_u16_value(analogueInput, value)   

    assert round(analogueInput.read_voltage(),1) == expected


