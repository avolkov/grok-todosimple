import grok

from todosimple import resource

class Todosimple(grok.Application, grok.Container):
    pass

class Index(grok.View):
    def update(self):
        resource.style.need()
