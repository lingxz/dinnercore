#dinnerCore

How to run code

### Running the core
```python
python manage.py runserver # it will run with the debug option
```

### Running the app - after a change to DB model (assuming you made the change)
```python
python manage.py db migrate
python manage.py db upgrade
python manage.py runserver
```

### Running the app - after a change to DB model (you did not make the change)
```python
python manage.py db upgrade
python manage.py runserver
```