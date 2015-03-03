# logos-decorators.py

def login_required():
    def permission_decorator(func):
        def func_wrapper(self, regex, chan, nick, **kwargs):
            if self.get_auth().is_authenticated(nick):
                f_res = func(self, regex, chan, nick, **kwargs)
                return f_res
            else:
                self.msg(chan, "You are not logged in")
        return func_wrapper
    return permission_decorator

def irc_room_permission_required(permission):
    def permission_decorator(func):
        def func_wrapper(self, regex, chan, nick, **kwargs):
            if 'room' in regex.groupdict():
                room = regex.group('room')
            else:
                room = chan
            if self.get_auth().is_authorised(nick, room, permission):
                f_res = func(self, regex, chan, nick, **kwargs)
                return f_res
            else:
                self.msg(chan, "You are not authorised or not logged in")

        return func_wrapper
    return permission_decorator

def irc_network_permission_required(permission):
    def permission_decorator(func):
        def func_wrapper(self, regex, chan, nick, **kwargs):
            if self.get_auth().is_authorised(nick, '#', permission):
                f_res = func(self, regex, chan, nick, **kwargs)
                return f_res
            else:
                self.msg(chan, "You are not authorised or not logged in")

        return func_wrapper
    return permission_decorator


