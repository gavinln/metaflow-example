'''
Example of using a Task runner similar to Prefect
https://docs.prefect.io/
'''

import inspect

# from IPython import embed


class Task:
    def __init__(self):
        self.args = tuple()
        self.kwargs = {}

    def bind(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class Flow:

    def __init__(self, name: str):
        self.name = name
        self.tasks = []

    def add_task(self, task: Task):
        self.tasks.append(task)

    def run(self):

        def task_arg_len(task):
            return len(task.args) + len(task.kwargs)

        for task in self.tasks:
            signature = inspect.signature(task.run)
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


# initialize the task instance
hello = HelloTask()
sub = SubTask()

flow = Flow("My imperative flow!")
flow.add_task(hello)
sub.bind(5, 3)
flow.add_task(sub)
flow.run()
