import tornado.web
import os
from socket_handler import TaskDescriptor
from tornado import escape

class TaskHandler(tornado.web.RequestHandler):

    def get(self, slug=None):
        self.set_header("Content-Type", "application/json")
        if len(slug) == 0:
            """
                Return task list
            """
            tasks = [t[:-4] for t in next(os.walk("./task_descriptors"))[2] if t.endswith(".pkl")]
            response = []
            for task in tasks:
                descriptor = TaskDescriptor(task)
                response.append(dict(task_name=task, task_status=descriptor.get_status(),
                                     task_spent_time=descriptor.get_task_time_summary()))
            self.write(escape.json_encode(dict(data=response)))
        else:
            if (os.path.isfile("./task_descriptors/"+slug+".pkl")):
                descriptor = TaskDescriptor(slug)
                self.write(escape.json_encode(dict(
                    task_name=slug,
                    task_status=descriptor.get_status(),
                    task_spent_time=descriptor.get_task_time_summary()
                )))
            else:
                self.set_status(404)
                self.write(escape.json_encode(dict(
                    error='Task Not Found'
                )))

    def post(self, *args, **kwargs):
        return super(TaskHandler, self).post(*args, **kwargs)


