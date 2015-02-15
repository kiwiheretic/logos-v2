# logos-decorators.py


def irc_room_permission_required(permission):
    def permission_decorator(func):
        def func_wrapper(self, regex, chan, nick, **kwargs):
            if self.get_auth().is_authorised(nick, chan, permission):
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


