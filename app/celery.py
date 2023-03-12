from celery import Celery
import  celery
def start_celery_app():
    app = celery.Celery('app',
                 broker='amqp://',
                 backend='rpc://',
                 include=['app.tasks'])

    # Optional configuration, see the application user guide.
    app.conf.update(
        result_expires=3600,
    )

    app.start()

from celery import Celery
from celery.schedules import crontab

app = Celery()
app.conf.beat_schedule = {
    'add-every-30-seconds': {
        'task': 'tasks.add',
        'schedule': 30.0,
        'args': (16, 16)
    },
}
app.result_backend = 'db+sqlite:///results.db'
app.conf.timezone = 'UTC'
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    sender.add_periodic_task(10.0, test.s('hello'), name='add every 10')

    # Calls test('world') every 30 seconds
    sender.add_periodic_task(30.0, test.s('world'), expires=10,  name="That task")

    sender.add_periodic_task(30.0, test.s('world'), expires=10, name="This TASK")

    # Executes every Monday morning at 7:30 a.m.
    sender.add_periodic_task(
        crontab(hour=7, minute=30, day_of_week=1),
        test.s('Happy Mondays!'),
    )

@app.task
def test(arg):
    # print(arg*100)
    print("task executed")



@app.task
def add(x, y):
    z = x + y
    print(z)



