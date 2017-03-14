celery -A task_other worker -E -Q sqlreview_analysis -l info
celery -A task_other worker -E -Q -l info
celery -A task_exports worker -E -l info
celery -A task_export worker -E -l info
celery -A task_capture worker -E -Q sqlreview_obj -l debug -B -n celery-capture-obj
celery flower --address=0.0.0.0 --broker=redis://:password@127.0.0.1:6379/0
celery -A task_capture worker -E -Q sqlreview_other -l info -B -n celery-capture-other