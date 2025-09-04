def get_tasks_stats(tasks):
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task.get('completed') == True)
    active_tasks = total_tasks - completed_tasks
    return active_tasks, completed_tasks

    
def calculate_progress(active_tasks, completed_tasks):
    total = active_tasks + completed_tasks
    progress = (completed_tasks//total) * 100
    return progress