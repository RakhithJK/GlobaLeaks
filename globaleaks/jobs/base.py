
# -*- encoding: utf-8 -*-
#
# :authors: Arturo Filastò
# :licence: see LICENSE

import time
import datetime

from twisted.internet import reactor

class Job(object):
    """
    This is the base class from which jobs should heredit.

    retries: through this parameter you can specify a list of intervals after
    which a retry should happen. This is time in seconds.
    XXX in the future we may want to support a cronish like syntax for such
        timeouts (1m, 1h, 2d, 1m etc.)
    """
    retries = [2,3,5]
    def __init__(self, scheduled_time=time.time(), delay=None):
        """
        scheduled_time: the number of seconds since epoch in local time for when
        the job should be run.

        delay: the delay in seconds to wait for running the job after
        scheduled_time. (if you don't pass scheduled_time delay will run the
        job delay seconds after now)

        """
        self.scheduledTime = scheduled_time

        self.args = ()
        self.manager = None
        self.running = False
        self.failures = []

        if delay:
            self.scheduledTime += delay

    def failed(self):
        """
        Place here all the logic to handle the failure of one run of the
        object.
        We will by default attempt to re-run the Job the number of retry times
        that are specified in self.retries
        """
        pass

    def failedRetries(self):
        """
        We have failed also all the retries handle this appropriately.

        When we reach this point this job is considered to have not worked and
        we should not make any more attempts at running it again.

        Ideally we just want to log this, and move on with out life.
        """
        pass

    def success(self):
        """
        What to do when the job has run successfully.
        """
        pass

    def __str__(self):
        return str("%s - %s - %s" % (self.__class__, self.scheduledTime, self.running))

    def schedule(self, date):
        if isinstance(date, datetime.datetime):
            self.scheduledTime = time.mktime(date.timetuple())
        else:
            raise Exception("date argument must be an instance of datetime")

    def _run(self, *args):
        d = self.run()
        self.args = args
        return d

    def run(self):
        pass

class JobTimedout(Exception):
    pass

class TimeoutJob(Job):
    timeout = 2
    def timedOut(self):
        pass

    def _timedOut(self, d, *arg, **kw):
        self.timedOut()
        d.errback(JobTimedout("%s timed out after %s" % (self.__class__,
            self.timeout)))

    def _run(self, manager=None):
        d = Job._run(self, manager)
        reactor.callLater(self.timeout, self._timedOut, d)
        return d

