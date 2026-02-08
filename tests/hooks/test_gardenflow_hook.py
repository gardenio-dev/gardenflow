import pytest

from gardenflow.hooks.gardenflow import GardenflowHook


class TestGardenflowHook:
    def test_hook_attributes(self):
        assert GardenflowHook.conn_type == "gardenflow"
        assert GardenflowHook.hook_name == "Gardenflow"
        assert GardenflowHook.default_conn_name == "gardenflow_default"
