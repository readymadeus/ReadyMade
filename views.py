#Present data to the user in any supported format or layout

from flask import Blueprint, request, redirect, render_template, url_for
from flask.views import MethodView
from RMFlask.models import Users, Projects

projects=Blueprint('projects',__name__,template_folder='templates')

class ListView(MethodView):
	def get(self):
		projects=Projects.objects.all()
		return render_template('projects/list.html', projects=projects)

class DetailView(MethodView):
	def get(self,orgname):
		project=Projects.objects.get_or_404(orgname=orgname)
		return render_template('projects/detail.html',user=project)

#Register the urls
projects.add_url_rule('/', view_func=ListView.as_view('list'))
projects.add_url_rule('/<orgname>/', view_func=DetailView.as_view('detail'))