import pytest
from contrib.strange_attractor import get_attractors


@pytest.mark.skip("not a real test")
def test_generate_ranges():
    """Can be used to generate ranges"""
    attractors = get_attractors()
    for attractor in attractors:
        attractor.estimate_ranges()
        print(f"{attractor.name}: x: {attractor.x_min} - {attractor.x_max}")
        print(f"{attractor.name}: y: {attractor.y_min} - {attractor.y_max}")
        print(f"{attractor.name}: z: {attractor.z_min} - {attractor.z_max}")

    assert False


# output from test
# Lorenz: x: -20.394994765598064 - 21.275120940199255
# Lorenz: y: -27.43024295359765 - 28.981277697415116
# Lorenz: z: 0.8424953124212676 - 53.71726601619622
# Pan-Xu-Zhou: x: -14.075702995421157 - 14.498528765859785
# Pan-Xu-Zhou: y: -17.2202634328533 - 17.859781904262686
# Pan-Xu-Zhou: z: 0.5948950929752651 - 30.283142691105404
# Rikitake: x: -5.590965414801476 - 7.884068883363314
# Rikitake: y: -2.840810842644633 - 4.557877707324136
# Rikitake: z: -0.1 - 10.411231297253208
# Rossler: x: -9.480827153205919 - 11.258039313880786
# Rossler: y: -10.650358754972927 - 8.5164905816445
# Rossler: z: -0.1 - 13.045880157159614

# Example saved state file, as generated on the module
{
    "Lorenz": {
        "x_min": -19.88703,
        "x_max": 21.27512,
        "y_min": -26.50838,
        "y_max": 28.98127,
        "z_min": 0.8424953,
        "z_max": 53.71726,
    },
    "Pan-Xu-Zhou": {
        "x_min": -14.19727,
        "x_max": 14.37684,
        "y_min": -17.39958,
        "y_max": 17.66736,
        "z_min": 0.9314724,
        "z_max": 30.04775,
    },
    "Rikitake": {
        "x_min": -6.380751,
        "x_max": 7.884183,
        "y_min": -3.405897,
        "y_max": 4.557963,
        "z_min": -0.1,
        "z_max": 10.41129,
    },
    "Rossler": {
        "x_min": -9.480834,
        "x_max": 11.25805,
        "y_min": -10.65037,
        "y_max": 8.516498,
        "z_min": -0.1,
        "z_max": 13.04592,
    },
}
