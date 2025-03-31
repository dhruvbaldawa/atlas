"""Dummy workflow for testing Temporal integration.

This module provides a simple workflow that demonstrates basic Temporal
functionality, including activity execution and deterministic workflow design.
"""

import logging
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

# Import activities using the correct syntax
with workflow.unsafe.imports_passed_through():
    from backend.activities.dummy import echo_message, get_current_time, simulate_work

logger = logging.getLogger(__name__)


@workflow.defn
class DummyWorkflow:
    """A simple dummy workflow for testing Temporal integration.

    This workflow demonstrates basic Temporal features including:
    - Activity execution with retry policies
    - Deterministic workflow design
    - Activity chaining
    """

    @workflow.run
    async def run(self, message: str | None = None) -> dict:
        """Run the dummy workflow.

        Args:
            message: Optional message to include in the workflow result

        Returns:
            dict: Results of the workflow execution
        """
        workflow.logger.info("Starting DummyWorkflow execution")

        # Step 1: Get current time
        current_time = await workflow.execute_activity(
            get_current_time,
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=RetryPolicy(
                maximum_attempts=3,
                initial_interval=timedelta(seconds=1),
            ),
        )

        workflow.logger.info(f"Received current time: {current_time}")

        # Step 2: Echo message if provided
        echo_result = None
        if message:
            echo_result = await workflow.execute_activity(
                echo_message,
                message,
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=RetryPolicy(
                    maximum_attempts=3,
                    initial_interval=timedelta(seconds=1),
                ),
            )
            workflow.logger.info(f"Echo result: {echo_result}")

        # Step 3: Simulate work
        work_result = await workflow.execute_activity(
            simulate_work,
            3,  # 3 seconds of simulated work
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(
                maximum_attempts=2,
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
            ),
        )

        workflow.logger.info(f"Work simulation result: {work_result}")

        # Return all results
        return {
            "start_time": current_time,
            "echo_result": echo_result,
            "work_result": work_result,
            "workflow_id": workflow.info().workflow_id,
        }


@workflow.defn
class ChainedDummyWorkflow:
    """A workflow that demonstrates chaining multiple workflows together."""

    @workflow.run
    async def run(self, messages: list[str]) -> list[dict]:
        """Run a series of dummy workflows in sequence.

        Args:
            messages: List of messages to process

        Returns:
            List[dict]: Results from each workflow execution
        """
        workflow.logger.info(f"Starting ChainedDummyWorkflow with {len(messages)} messages")

        results = []
        for i, message in enumerate(messages):
            workflow.logger.info(f"Processing message {i + 1}/{len(messages)}: {message}")

            # Execute a child workflow for each message
            child_result = await workflow.execute_child_workflow(
                DummyWorkflow.run,
                message,
                id=f"{workflow.info().workflow_id}-child-{i}",
                retry_policy=RetryPolicy(maximum_attempts=1),
            )

            results.append(child_result)
            workflow.logger.info(f"Completed child workflow {i + 1}")

        workflow.logger.info("ChainedDummyWorkflow completed successfully")
        return results
