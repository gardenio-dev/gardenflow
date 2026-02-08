import pytest

from gardenflow.sensors.gardenflow import GardenflowSensor


class TestGardenflowSensor:
    def test_sensor_defaults(self):
        sensor = GardenflowSensor(task_id="test")
        assert sensor.gardenflow_conn_id == "gardenflow_default"
