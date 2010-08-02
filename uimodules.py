#!/usr/bin/env python
import tornado.web

class BaseUIModule(tornado.web.UIModule):
    def __init__(self, handler):
        self.data = handler.data
        super(BaseUIModule, self).__init__(handler)

class HeaderUserInfo(BaseUIModule):
    def render(self):
        return self.render_string('modules/header-user-info.html', user=self.current_user)
