# Helper functions that are called in __init__.py
# Temporary refactor for the moment --> until blueprints are used
# None of the functions here call a route

from project import db, session
from project.models import Task
import parsedatetime as pdt
import datetime
from datetime import datetime


def retrieve_tasks_helper():
    # Support for the reverse query here
    tasks = Task.query. \
        filter(Task.user_id == session['user_id']). \
        order_by(Task.lft)

    todo_list = []
    for task in tasks:
        task_item = task_to_dictionary(task)
        todo_list.append(task_item)
    return todo_list


def task_to_dictionary(task):
    if task.due_date:
        # convert datetime object to string before sending
        due_date = task.due_date.strftime("%Y/%m/%d %H:%M:%S")
    else:
        due_date = None
    task_item = {
        'id': task.id,
        'content': task.content,
        'due_date': due_date,
        'done': task.done,
        'lft': task.lft,
        'rgt': task.rgt
    }
    return task_item


def extract_datetime_from_text(data):
    cal = pdt.Calendar()
    date_time = cal.nlp(data)
    if date_time and date_time[0][0] > datetime.now():  # if date is in the past, ignore date
        # if datetime was given
        dt = date_time[0][0]  # this defaults to 9am if no time was given
        # here we try to remove datetime from string
        date_string_start = date_time[0][2]
        date_string_end = date_time[0][3]
        content = data[:date_string_start].rstrip() + data[date_string_end:]
        if not content.strip():
            content = data

    else:
        dt = None
        content = data
    return dt, content


# Used to display tasks
def in_order_traverse(tree, output, depth, group):
    if 'children' in tree:
        out_tree = dict(tree)
        del out_tree['children']
        out_tree['depth'] = depth
        out_tree['group'] = group
        output = [out_tree]
        for subtree in tree['children']:
            output += in_order_traverse(subtree, [], depth + 1, group)
    else:
        tree['depth'] = depth
        tree['group'] = group
        output.append(tree)
    return output


def get_tree(root):
    tree = task_to_dictionary(root)
    tree['children'] = []
    children = Task.query.filter(Task.parent_id == root.id)

    if not children:
        return tree
    else:
        for child in children:
            tree['children'].append(get_tree(child))
        return tree


def delete_task_helper(current_task):
    # this is for deleting a leaf node only
    user_id = current_task.user_id
    my_left = current_task.lft
    my_right = current_task.rgt
    my_width = my_right - my_left + 1
    db.session.delete(current_task)

    cmd = "UPDATE tasks SET rgt = rgt - :my_width WHERE user_id = :user_id AND rgt > :my_right"
    db.engine.execute(cmd, {'my_width': str(my_width), 'user_id': str(user_id), 'my_right': str(my_right)})

    cmd = "UPDATE tasks SET lft = lft - :my_width WHERE user_id = :user_id AND lft > :my_right"
    db.engine.execute(cmd, {'my_width': str(my_width), 'user_id': str(user_id), 'my_right': str(my_right)})
    db.session.commit()


def get_subtasks(parent):
    subtasks = Task.query.filter(Task.parent_id == parent.id).all()
    return subtasks
