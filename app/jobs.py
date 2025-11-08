from .extensions import celery

@celery.task
def background_task(arg1):
    # long-running task
    pass