from __future__ import print_function

import time

from simpleflow import (
    activity,
    Workflow,
    futures,
)


@activity.with_attributes(task_list='quickstart', version='example')
def repeat50k(s):
    return s * 50000


@activity.with_attributes(task_list='quickstart', version='example')
def length(x):
    return len(x)


class JumboFieldsWorkflow(Workflow):
    """
    This workflow demonstrates how you can use simpleflow jumbo fields, e.g.
    how simpleflow can automatically store input/results on S3 if their length
    crosses the SWF limits (32KB for input/results).
    """
    name = 'basic'
    version = 'example'
    task_list = 'example'

    def run(self, string):
        long_string = self.submit(repeat50k, str(string))
        string_length = self.submit(length, long_string)
        print('{} * 50k has a length of: {}'.format(
            string, string_length.result))
