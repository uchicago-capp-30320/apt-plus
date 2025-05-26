"""
NOTE:
This test is designed to be run inside the Docker container.
Make sure to run:
    docker exec -it apt-plus-airflow-scheduler-1 bash
    pip install pytest
    pytest tests/test_groceries_elt.py
"""
import sys
sys.path.append("/opt/airflow")  # Ensure Airflow DAGs path is available

import pytest
from airflow.models import DagBag
from dags.groceries_elt import grocery_elt_pipeline


# Test that the DAG is correctly loaded from the airflow/dags directory
def test_dag_loaded():
    dagbag = DagBag(dag_folder="../airflow/dags")
    dag = dagbag.get_dag('grocery_elt_pipeline')

    # Ensure the DAG exists and was loaded without import errors
    assert dag is not None
    assert not dagbag.import_errors
    assert dag.dag_id == 'grocery_elt_pipeline'

# Smoke test: Check that the transform task is defined and has a Python function
def test_transform_callable_exists():
    dag = grocery_elt_pipeline()
    assert hasattr(dag.get_task("transform"), "python_callable")

# Smoke test: Check that the merge task is defined and has a Python function
def test_merge_callable_exists():
    dag = grocery_elt_pipeline()
    assert hasattr(dag.get_task("merge"), "python_callable")
