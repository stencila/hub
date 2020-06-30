from datetime import datetime
import time

from jobs.base.job import Job


class Sleep(Job):
    """
    A sleep job mainly for testing.

    Provides a means of testing job logging, termination and failure.
    """

    name = "sleep"

    def do(self, seconds: int = 1, repeat: int = 10, fail: int = 0, **kwargs):  # type: ignore
        for rep in range(1, repeat + 1):
            if rep == fail:
                raise RuntimeError("Failing at repetition {}".format(rep))

            time.sleep(seconds)
            self.info(
                "This is repetition {} at {}.".format(
                    rep, datetime.utcnow().isoformat()
                )
            )

        return "Slept for {} seconds, {} times and finished at {}.".format(
            seconds, repeat, datetime.utcnow().isoformat()
        )
