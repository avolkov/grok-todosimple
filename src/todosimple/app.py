import grok
from todosimple import resource
from zope import interface, schema

class Todo(grok.Application, grok.Container):
    def __init__(self):
        super(Todo, self).__init__()
        self.title = 'To-Do list manager'
        self.next_id = 0

    def deleteProject(selfself, project):
        del self[project]

class IProject(interface.Interface):
    title = schema.TextLine(title=u'Title', required=True)
    kind = schema.Choice(title=u'Kind of project',
                         values=['personal', 'business'])
    description = schema.Text(title=u'Description', required=False)
    next_id = schema.Int(title=u'Next id', default=0)

class Project(grok.Container):
    grok.implements(IProject)

    def addList(self, title, description):
        id = str(self.next_id)
        self.next_id += 1
        self[id] = TodoList(title, description)

    def deleteList(self, list):
        del self[list]

class AddProjectForm(grok.AddForm):
    grok.context(Todo)
    grok.name('index')
    form_fields = grok.AutoFields(IProject).omit('next_id')
    label = "To begin, add a new project"

    @grok.action('Add Project')
    def add(self, **data):
        project = Project()
        self.applyData(project, **data)
        id = str(self.context.next_id)
        self.context.next_id += 1
        self.context[id] = project
        new_url = self.url(self.context[id])
        return self.redirect(new_url)

class ProjectView(grok.View):
    grok.context(Project)
    grok.name('index')
    def render(self):
        ctx = self.context
        outstr = """
Title: %s\n
Kind: %s\n
Description: %s\n
next_id: %d\n
""" % (ctx.title, ctx.kind, ctx.description, ctx.next_id) 
        return outstr
