import time
from behave import *


@then(
    "we sadly wait for {n} seconds because we have not figured out how to listen for events"
)
@given(
    "we sadly wait for {n} seconds because we have not figured out how to listen for events"
)
@when(
    "we sadly wait for {n} seconds because we have not figured out how to listen for events"
)
def step_impl(context, n: float):
    time.sleep(float(n))
