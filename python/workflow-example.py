'''
Example of using a Task runner similar to Prefect
https://docs.prefect.io/
'''

import inspect
from functools import wraps

# from IPython import embed

context = None


class Task:
    def __init__(self):
        self.args = tuple()
        self.kwargs = {}

    def bind(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        return self

    def _get_run_fn(self):
        return self.run


class FunctionTask(Task):
    def __init__(self, run_fn):
        self.run_fn = run_fn

    def __call__(self, *args, **kwargs):
        global context
        if context is None:
            raise ValueError(
                'Cannot call function {} outside a context'.format(
                    self.run_fn.__name__))
        print('current context = {}'.format(context))
        # do not return self as cannot add it to flow
        # should raise error if not in context
        # should add self to flow in context
        self.bind(*args, **kwargs)
        context.add_task(self)

    def _get_run_fn(self):
        return self.run_fn

    def run(self, *args, **kwargs):
        return self.run_fn(*args, **kwargs)


class Flow:
    def __init__(self, name: str):
        self.name = name
        self.tasks = []

    def __enter__(self):
        global context
        context = self
        return self

    def __exit__(self, type, value, traceback):
        global context
        context = None

    def add_task(self, task: Task):
        # add a message preventing task defined using @task decorator
        # it is automatically added
        # print('adding task {}'.format(task.__class__.__name__))
        self.tasks.append(task)

    def run(self):

        def task_arg_len(task):
            return len(task.args) + len(task.kwargs)

        for task in self.tasks:
            signature = inspect.signature(task._get_run_fn())
            if len(signature.parameters) != task_arg_len(task):
                raise ValueError(
                    'Invalid bind arguments for {}.run function'
                    '\nsignature {}'.format(
                        task.__class__.__name__, signature)
                )
            bound_args = signature.bind(*task.args, **task.kwargs)
            task.run(*bound_args.args, **bound_args.kwargs)
        return None


class HelloTask(Task):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self):
        print('hello')


class SubTask(Task):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, x: int, y: int) -> int:
        sub_total = x - y
        print('sub_total = {}'.format(sub_total))
        return sub_total


def main1():
    # initialize the task instances
    hello = HelloTask()
    sub = SubTask()

    flow = Flow("imperative flow")
    flow.add_task(hello)
    sub.bind(5, 3)
    flow.add_task(sub)
    flow.run()

    with Flow('functional flow') as flow:
        flow.add_task(hello)
        flow.add_task(sub.bind(5, 3))

    flow.run()


def task(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
    return FunctionTask(wrapper)


@task
def hello_fn():
    print('in hello')


@task
def sub_fn(x, y):
    sub_total = x - y
    print('sub_total = {}'.format(sub_total))
    return sub_total


def main():
    with Flow('functional flow 2') as flow:
        hello_fn()
        sub_fn(5, 3)

    print('about to run tasks')
    flow.run()


if __name__ == '__main__':
    main()
