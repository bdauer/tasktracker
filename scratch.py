import datetime
import SQLAlchemy

def add_task(name, value, date, recurring=False):
    """
    Add a new task.
    """
    return True

def mark_complete(task):
    """
    mark a task as complete.
    """
    return True

def start_task():

    start = datetime.datetime.now()


# store tasks in sqlite database

class Task(db.model):
    __tablename__
