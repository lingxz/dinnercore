# from project.utils import auth
# from flask import Blueprint, request, redirect
# from project import db, session
# from project.models import Task
# from project.utils import utils
# from sqlalchemy import text
# from datetime import datetime
# import json
#
# tasks = Blueprint('tasks', __name__)
#
#
# @tasks.route('/retrieve', methods=['POST'])
# @auth.login_required
# def retrieve():
#     """Swap to a post request because you are sending data"""
#     # Support for the reverse query here
#     todo_list = utils.retrieve_tasks_helper()
#
#     # Must generate the initial task
#     if len(todo_list) == 0:
#         task = Task(
#             content="Edit your first task",
#             user_id=session['user_id'],
#             due_date=None
#         )
#         db.session.add(task)
#         db.session.commit()
#         todo_list = utils.retrieve_tasks_helper()
#
#     return json.dumps(todo_list)
#
#
# @tasks.route('/retrieve_tasks', methods=['POST'])
# @auth.login_required
# def retrieve_tasks():
#     user_id = session['user_id']
#
#     # find all root nodes
#     roots = []
#     root1 = Task.query.filter(Task.user_id == user_id).filter(Task.lft == 0).first()
#
#     if not root1:
#         task = Task(
#             content="Edit your first task",
#             user_id=session['user_id'],
#             due_date=None
#         )
#         db.session.add(task)
#         db.session.commit()
#         trees = utils.retrieve_tasks_helper()
#         return json.dumps(trees)
#
#     roots.append(root1)
#     rgt = root1.rgt
#     lft = root1.lft
#
#     while True:
#         r = Task.query.filter(Task.user_id == user_id, Task.lft == rgt + 1).first()
#         if not r:
#             break
#         else:
#             roots.append(r)
#             rgt = r.rgt
#             lft = r.lft
#
#     trees = []
#     for root in roots:
#         trees.append(utils.get_tree(root))
#
#     # Recurse through the trees to extract every task
#     output = []
#     group = 0
#     for tree in trees:
#         output += utils.in_order_traverse(tree, [], 0, tree['id'])
#
#     return json.dumps(output)
#
#
# @tasks.route('/add', methods=['POST'])
# @auth.login_required
# def add_task():
#     data = request.json['content']
#     # if not data:
#     #     return redirect('/')
#
#     dt, content = utils.extract_datetime_from_text(data)
#
#     user_id = request.json['user_id']
#     prev_task = Task.query.get(request.json['prev_task'])
#     my_right = prev_task.rgt
#     task = Task(
#         content=content,
#         user_id=user_id,
#         due_date=dt,
#         my_right=my_right,
#         parent_id=prev_task.parent_id
#     )
#
#     user_id = str(user_id)
#     # Technically this should be wrapped in a transaction
#     cmd = "UPDATE tasks SET rgt = rgt + 2 WHERE user_id =" + user_id + " AND rgt > " + str(my_right)
#     db.engine.execute(text(cmd))
#     cmd2 = "UPDATE tasks SET lft = lft + 2 WHERE user_id =" + user_id + " AND lft > " + str(my_right)
#     db.engine.execute(text(cmd2))
#     db.session.add(task)
#     db.session.commit()
#     return json.dumps(utils.task_to_dictionary(task))
#
#
# @tasks.route('/make_subtask', methods=['POST'])
# @auth.login_required
# def make_subtask():
#     user_id = request.json['user_id']
#     id = request.json['subtask_id']
#     current_task = Task.query.filter_by(id=id).first()
#     content = current_task.content
#     # user_id = current_task.user_id
#     due_date = current_task.due_date
#
#     parent_id = request.json['prev_task_id']
#     parent_task = Task.query.filter_by(id=parent_id).first()
#
#     sub_tasks = utils.get_subtasks(parent_task)
#     if not sub_tasks:
#         # adding a child to a node with no existing children
#         parent_left = parent_task.lft
#         cmd = "UPDATE tasks SET rgt = rgt + 2 WHERE user_id = :user_id AND rgt > :parent_left"
#         cmd2 = "UPDATE tasks SET lft = lft + 2 WHERE user_id = :user_id AND lft > :parent_left"
#
#         db.engine.execute(cmd, {'user_id': str(user_id), 'parent_left': str(parent_left)})
#         db.engine.execute(cmd2, {'user_id': str(user_id), 'parent_left': str(parent_left)})
#         utils.delete_task_helper(current_task)
#         task = Task(
#             content=content,
#             user_id=user_id,
#             due_date=due_date,
#             parent_id=parent_id,
#             my_right=parent_left
#         )
#         db.session.add(task)
#         db.session.commit()
#     else:
#         sub_tasks.sort(key=lambda x: x.rgt)
#         prev_right = sub_tasks[-1].rgt
#
#         # Technically this should be wrapped in a transaction
#         cmd = "UPDATE tasks SET rgt = rgt + 2 WHERE user_id = :user_id AND rgt >  :prev_right"
#         db.engine.execute(cmd, {'user_id': str(user_id), 'prev_right': str(prev_right)})
#         cmd2 = "UPDATE tasks SET lft = lft + 2 WHERE user_id = :user_id AND lft > :prev_right"
#         db.engine.execute(cmd2, {'user_id': str(user_id), 'prev_right': str(prev_right)})
#         utils.delete_task_helper(current_task)
#         task = Task(
#             content=content,
#             user_id=user_id,
#             due_date=due_date,
#             parent_id=parent_id,
#             my_right=prev_right
#         )
#         db.session.add(task)
#         db.session.commit()
#
#     return json.dumps(utils.task_to_dictionary(task))
#
#
# @tasks.route('/add_subtask', methods=['POST'])
# @auth.login_required
# def add_subtask():
#     user_id = request.json['user_id']
#     parent_id = request.json['parent_id']
#     task_content = request.json['task_content']
#     parent_task = Task.query.filter_by(id=parent_id).first()
#
#     sub_tasks = utils.get_subtasks(parent_task)
#     if not sub_tasks:
#         # adding a child to a node with no existing children
#         parent_left = parent_task.lft
#         cmd = "UPDATE tasks SET rgt = rgt + 2 WHERE user_id = :user_id AND rgt > :parent_left"
#         cmd2 = "UPDATE tasks SET lft = lft + 2 WHERE user_id = :user_id AND lft > :parent_left"
#
#         db.engine.execute(cmd, {'user_id': str(user_id), 'parent_left': str(parent_left)})
#         db.engine.execute(cmd2, {'user_id': str(user_id), 'parent_left': str(parent_left)})
#         task = Task(
#             content=task_content,
#             user_id=user_id,
#             parent_id=parent_id,
#             my_right=parent_left
#         )
#         db.session.add(task)
#         db.session.commit()
#     else:
#         sub_tasks.sort(key=lambda x: x.rgt)
#         prev_right = sub_tasks[-1].rgt
#
#         # Technically this should be wrapped in a transaction
#         cmd = "UPDATE tasks SET rgt = rgt + 2 WHERE user_id = :user_id AND rgt >  :prev_right"
#         db.engine.execute(cmd, {'user_id': str(user_id), 'prev_right': str(prev_right)})
#         cmd2 = "UPDATE tasks SET lft = lft + 2 WHERE user_id = :user_id AND lft > :prev_right"
#         db.engine.execute(cmd2, {'user_id': str(user_id), 'prev_right': str(prev_right)})
#         task = Task(
#             content=task_content,
#             user_id=user_id,
#             parent_id=parent_id,
#             my_right=prev_right
#         )
#         db.session.add(task)
#         db.session.commit()
#
#     return json.dumps(utils.task_to_dictionary(task))
#
#
# @tasks.route('/get_prev_sibling', methods=['POST'])
# @auth.login_required
# def get_prev_sibling():
#     task_id = request.json['task_id']
#     task = Task.query.filter(Task.id == task_id).first()
#     parent_id = task.parent_id
#     user_id = task.user_id
#     left = task.lft
#     prev_sibling = Task.query.filter(Task.parent_id == parent_id, Task.user_id == user_id, Task.rgt == left - 1).first()
#     return json.dumps(utils.task_to_dictionary(prev_sibling))
#
#
# @tasks.route('/markdone', methods=['POST'])
# @auth.login_required
# def mark_as_done():
#     uid = request.json['id']
#     if not uid:
#         return redirect('/')
#     current_task = Task.query.filter_by(id=uid).first()
#     if current_task.done:
#         current_task.done = False
#         db.session.commit()
#         return json.dumps({'done': False})
#     else:
#         current_task.done = True
#         db.session.commit()
#         return json.dumps({'done': True})
#
#
# @tasks.route('/edit_task', methods=['POST'])
# @auth.login_required
# def edit_task():
#     uid = request.json['id']
#     content = request.json['content']
#     current_task = Task.query.filter_by(id=uid).first()
#     current_task.content = content
#     db.session.commit()
#     return 'OK'
#
#
# @tasks.route('/edit_date', methods=['POST'])
# @auth.login_required
# def edit_date():
#     uid = request.json['id']
#     new_date = request.json['date']
#     new_date = datetime.strptime(new_date, '%a %b %d %Y %H:%M:%S GMT%z (%Z)')
#     current_task = Task.query.filter_by(id=uid).first()
#     current_task.due_date = new_date
#     db.session.commit()
#     return new_date.strftime("%Y/%m/%d %H:%M:%S")
#
#
# @tasks.route('/remove_date', methods=['POST'])
# @auth.login_required
# def remove_date():
#     uid = request.json['id']
#     current_task = Task.query.filter_by(id=uid).first()
#     current_task.due_date = None
#     db.session.commit()
#     return 'OK'
#
#
# @tasks.route('/parse_task', methods=['POST'])
# @auth.login_required
# def parse_task():
#     uid = request.json['id']
#     my_text = request.json['content']
#     dt, content = utils.extract_datetime_from_text(my_text)
#     current_task = Task.query.filter_by(id=uid).first()
#     current_task.content = content
#     current_task.due_date = dt
#     db.session.commit()
#     return 'OK'
#
#
# @tasks.route('/delete_task', methods=['POST'])
# @auth.login_required
# def delete_task():
#     task_id = request.json['id']
#     # user_id = request.json['user_id']
#     current_task = db.session.query(Task).get(task_id)
#
#     # get all subordinates of task
#     # deleting a parent task deletes all subordinates
#
#     tree = Task.query.filter(Task.lft >= current_task.lft, Task.lft < current_task.rgt).all()
#
#     for task in tree:
#         utils.delete_task_helper(task)
#
#     return 'OK'
#
#
# @tasks.route('/get_direct_subtasks', methods=['POST'])
# @auth.login_required
# def get_direct_subtasks():
#     task_id = request.json['id']
#     parent = db.session.query(Task).get(task_id)
#     print(parent.content)
#     subtasks = utils.get_subtasks(parent)
#     subtasks_list = []
#     for subtask in subtasks:
#         subtask_dict = utils.task_to_dictionary(subtask)
#         subtasks_list.append(subtask_dict)
#     return json.dumps(subtasks_list)
