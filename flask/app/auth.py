from flask import request, g, redirect, url_for

def require_login(func):
    def inner(*args, **kwargs):
        if 'user' not in g:
            return redirect(url_for('login', next=request.url, message='testing'))
        return func(*args, **kwargs)
    # Renaming the function name: https://stackoverflow.com/a/42254713/13631146
    inner.__name__ = func.__name__
    return inner
