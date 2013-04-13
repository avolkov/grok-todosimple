import grok
from todosimple import resource
from zope import interface, schema

def setup_widgets(self, ignore_request=False):
    super(self.__class__, self).setUpWidgets(ignore_request)
    self.widgets['title'].displayWidth = 50
    self.widgets['description'].height = 5

def check_title(value):
    """Add title value length constraint"""
    return len(value) > 2

class Todo(grok.Application, grok.Container):
    def __init__(self):
        super(Todo, self).__init__()
        self.title = 'To-Do list manager'
        self.next_id = 0

    def deleteProject(selfself, project):
        del self[project]

class IProject(interface.Interface):
    title = schema.TextLine(title=u'Title',
                            required=True,
                            constraint=check_title)
    kind = schema.Choice(title=u'Kind of project',
                         values=['personal', 'business'])
    description = schema.Text(title=u'Description', required=False)
    next_id = schema.Int(title=u'Next id', default=0)
    extra_id = schema.Int(title=u"Extra id", default=42)

    @interface.invariant
    def businessNeedsDescription(project):
        if project.kind == 'business' and not project.description:
            raise interface.Invalid(
                        "Business projects require description")

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
    form_fields = grok.AutoFields(IProject).omit('extra_id')
    label = "To begin, add a new project"
    setUpWidgets = setup_widgets
    @grok.action('Add Project')
    def add(self, **data):
        project = Project()
        self.applyData(project, **data)
        id = str(self.context.next_id)
        self.context.next_id += 1
        self.context[id] = project
        new_url = self.url(self.context[id])
        return self.redirect(new_url)

class EditProjectForm(grok.EditForm):
    grok.context(Project)
    grok.name('edit')
    form_fields = grok.AutoFields(Project).omit('next_id')
    label = "Edit the project"
    setUpWidgets = setup_widgets

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
