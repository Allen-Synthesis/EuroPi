from hello_world import HelloWorld


def test_increment():
    hw = HelloWorld()
    assert hw.increment(1) == 2