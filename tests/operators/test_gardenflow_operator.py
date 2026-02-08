import pytest

from gardenflow.operators.gardenflow import GardenflowOperator


class TestGardenflowOperator:
    def test_operator_defaults(self):
        op = GardenflowOperator(task_id="test")
        assert op.gardenflow_conn_id == "gardenflow_default"
