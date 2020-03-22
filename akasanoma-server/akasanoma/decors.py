from functools import wraps


def login_required(func):
    @wraps(func)
    def wrapper(req, **kwargs):

        if req.user:
            return func(req, **kwargs)
        else:
            return {'status':False, 'data':'Login Required'}
    
    return wrapper


def user_required(user_type):

    def inner(func):

        @wraps(func)
        def wrapper(req, **kwargs):

            if req.user.user_type == user_type:
                return func(req, **kwargs)
            else:
                return {'status':False, 'data':'Permission Required'}
    
    return inner