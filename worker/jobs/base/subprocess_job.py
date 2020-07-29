import io
import json
import subprocess
import threading
from typing import List, Optional, Union

from .job import Job, DEBUG, INFO, WARN, ERROR


class SubprocessJob(Job):
    """
    Runs a job in a local subprocess.

    This provides a convenient way to define a job that uses another
    process (e.g. a standalone binary, a script in another language).
    Simply override the `do()` attribute of the class. e.g.

        class MyJob(SubprocessJob):

            def do(self, arg1, arg2):
                return super().do(['mybinary', arg1, arg2])

    It assumes the POSIX conventions of:

    - diagnostic logs are written to `stderr` and the result is written
      to `stdout`

    - a non-zero exit code indicates a failure

    If that does not apply, you'll have to handle streams and exit codes
    differently in your `do()` method.
    """

    def __init__(self):
        super().__init__()
        self.process = None
        self.thread = None

    def do(self, args: List[str], input: Optional[bytes] = None):  # type: ignore
        """
        Do the job.

        Override of `Job.do` which starts the subprocess, with a
        thread to asynchronously read it's `stderr` in order to
        update the log using the logic

        - if a line can be parsed as JSON and has a `message` property
          then it assumed to be a log entry
        - otherwise, it is treated as a INFO message, but changed to
          an ERROR if the exit code is non-zero
        """
        self.process = subprocess.Popen(
            args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )

        def handle_stderr(stderr: Union[List[str], io.TextIOWrapper]):
            for line in stderr:
                try:
                    entry = json.loads(line)
                    if isinstance(entry, dict) and "message" in entry:
                        self.log(
                            level=entry.get("level", INFO), message=entry["message"]
                        )
                    else:
                        self.info(line.strip())
                except json.decoder.JSONDecodeError:
                    self.info(line.strip())

        if input:
            stdout_data, stderr_data = self.process.communicate(input=input)
            if stderr_data:
                handle_stderr(stderr_data.decode().split("\n"))
        else:
            self.thread = threading.Thread(
                target=handle_stderr,
                args=(io.TextIOWrapper(self.process.stderr, encoding="utf-8"),),  # type: ignore
            )
            self.thread.start()
            self.process.wait()
            stdout_data = self.process.stdout.read()  # type: ignore

        if self.process.returncode != 0:
            for log in self.log_entries:
                log["level"] = ERROR
            raise RuntimeError(
                "Subprocess exited with non-zero code: {}".format(
                    self.process.returncode
                )
            )

        return stdout_data.decode() if stdout_data else None

    def terminated(self):
        """
        Job has been terminated.

        Override of `Job.terminate` which kills the
        subprocess.
        """
        self.process.kill()
