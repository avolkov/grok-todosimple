import grok
from todosimple import resource

from zope import interface, schema

from zope.catalog.interfaces import ICatalog
from zope.component import getUtility

def setup_widgets(self, ignore_request=False):
    super(self.__class__, self).setUpWidgets(ignore_request)
    self.widgets['title'].displayWidth = 50
    self.widgets['description'].height = 5

def check_title(value):
    """Add title value length constraint"""
    return len(value) > 2

class IMetadata(interface.Interface):
    creator = schema.TextLine(title=u'Creator')
    creation_date = schema.Datetime(title=u'Creation date')
    modification_date = schema.Datetime(title=u'Modification date')

class ITodo(interface.Interface):
    title = schema.TextLine(title=u'Title', required=True)
    next_id = schema.Int(title=u'Next id', default=0)

class Todo(grok.Application, grok.Container):
    grok.implements(ITodo)
    title = u'To-Do list manager'
    next_id = 0

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

    @interface.invariant
    def businessNeedsDescription(project):
        if project.kind == 'business' and not project.description:
            raise interface.Invalid(
                        "Business projects require description")

class Project(grok.Container):
    grok.implements(IProject, IMetadata)
    next_id = 0
    description = u''

    def addList(self, title, description):
        id = str(self.next_id)
        self.next_id = self.next_id + 1
        self[id] = TodoList(title, description)

    def deleteList(self, list):
        del self[list]

class AddProjectForm(grok.AddForm):
    grok.context(Todo)
    grok.name('index')
    form_fields = grok.AutoFields(IProject)
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

class ProjectIndexes(grok.Indexes):
    """Grok indexer class"""
    grok.site(ITodo)
    grok.context(IProject)
    project_title = grok.index.Text(attribute='title')

class TodoSearch(grok.View):
    grok.context(Todo)
    grok.name('search')

    def update(self, query):
        if query:
            catalog = getUtility(ICatalog)
            self.results = catalog.searchResults(title=query)
