from tornado import websocket
from tornado import escape

import datetime as dt
import pickle

clients = []
descriptors = {}

class TaskDescriptor:

    STATUS_NEW = 0
    STATUS_INITED = 1
    STATUS_RESETED = 2
    STATUS_STARTED = 3
    STATUS_STOPED = 4

    def __init__(self, task_name, ext='.pkl', path='./task_descriptors/'):
        self.ext = ext
        self.path = path
        self.task_name = task_name
        self.task_descriptor_file_path = self.path + self.task_name + self.ext
        self.set_status(self.STATUS_NEW)

    def task_init(self):
        f = open(self.task_descriptor_file_path, 'wb')
        work = {
            'result': [],
            'timer': []
        }
        pickle.dump(work, f)
        f.close()
        self.set_status(self.STATUS_INITED)

    def task_reset(self):
        work = pickle.load(open(self.task_descriptor_file_path, 'rb'))
        work['result'] = []
        work['timer'] = []
        pickle.dump(work, open(self.task_descriptor_file_path, 'wb'))
        self.set_status(self.STATUS_RESETED)

    def task_start(self):
        work = pickle.load(open(self.task_descriptor_file_path, 'rb'))
        work['timer'].append(dt.datetime.now())
        pickle.dump(work, open(self.task_descriptor_file_path, 'wb'))
        self.set_status(self.STATUS_STARTED)

    def task_stop(self):
        work = pickle.load(open(self.task_descriptor_file_path, 'rb'))
        stop_time = dt.datetime.now()
        delta = (stop_time - work['timer'].pop()).total_seconds()
        work['result'].append(delta/3600)
        pickle.dump(work, open(self.task_descriptor_file_path, 'wb'))
        self.set_status(self.STATUS_STOPED)

    def get_task_time_summary(self):
        f = open(self.task_descriptor_file_path, 'rb')
        work = pickle.load(f)
        summ = sum(work['result'])
        f.close()
        return summ

    def set_status(self, status):
        self.status = status

    def get_status(self):
        return self.status

class WorkTimerHandler(websocket.WebSocketHandler):
    def on_close(self):
        clients.remove(self)
        print("WebSocket closed")

    def open(self, *args, **kwargs):
        clients.append(self)
        print("WebSocket opened")

    def on_message(self, message):
        client_request_data = escape.json_decode(message)
        task_name = client_request_data['task']
        if (task_name not in descriptors):
            descriptors[task_name] = TaskDescriptor(task_name)
        """
            TaskDescriptor descriptor
        """
        descriptor = descriptors[task_name]
        try:
            actions = {
                "reset": lambda task: descriptor.task_reset(task),
                "start": lambda task: descriptor.task_start(task),
                "stop": lambda task: descriptor.task_stop(task),
                "init": lambda task: descriptor.task_init(task)
            }
            actions[client_request_data['action']](task_name)
            for client in clients:
                client.write_message(escape.json_encode({
                    'task': task_name,
                    'status': descriptor.get_status()
                }))
        except Exception as ex:
            for client in clients:
                client.write_message(escape.json_encode({
                    'error': ex.message
                }))
            pass


