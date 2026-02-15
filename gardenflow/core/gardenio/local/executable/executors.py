"""Executors for the GardenIO local executable."""

import subprocess
from collections.abc import Generator
from pathlib import Path

from gardenflow.core.logging import logger


class StreamingExecutor:
    """Execute the GardenIO binary, yielding stdout lines."""

    def __init__(self, executable: Path, quiet: bool = False):
        self._executable = executable
        self._quiet = quiet

    def run(self, *args: str) -> Generator[str, None, None]:
        """Run a command and yield stdout lines.

        :param args: command arguments
        :yields: lines from stdout
        :raises subprocess.CalledProcessError: on non-zero
            exit
        """
        cmd = [str(self._executable), "--no-banner"]
        if self._quiet:
            cmd.append("-q")
        cmd.extend(args)

        logger().debug("exec.streaming", cmd=cmd)

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            for line in proc.stdout:
                yield line.rstrip("\n")
        finally:
            stdout = proc.stdout.read()
            proc.stdout.close()
            proc.wait()

            if proc.returncode != 0:
                stderr = proc.stderr.read()
                proc.stderr.close()
                logger().error(
                    "exec.streaming.failed",
                    cmd=cmd,
                    returncode=proc.returncode,
                    stdout=stdout,
                    stderr=stderr,
                )
                raise subprocess.CalledProcessError(
                    proc.returncode,
                    cmd,
                    output=stdout,
                    stderr=stderr,
                )
            proc.stderr.close()


class Executor:
    """Execute the GardenIO binary, returning the result."""

    def __init__(self, executable: Path, quiet: bool = True):
        self._executable = executable
        self._quiet = quiet

    def run(self, *args: str) -> str:
        """Run a command and return stdout.

        :param args: command arguments
        :returns: stdout as a string
        :raises subprocess.CalledProcessError: on non-zero
            exit
        """
        cmd = [str(self._executable), "--no-banner"]
        if self._quiet:
            cmd.append("-q")
        cmd.extend(args)

        logger().debug("exec", cmd=cmd)

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            logger().error(
                "exec.failed",
                cmd=cmd,
                returncode=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
            )
            raise subprocess.CalledProcessError(
                result.returncode,
                cmd,
                output=result.stdout,
                stderr=result.stderr,
            )

        return result.stdout
