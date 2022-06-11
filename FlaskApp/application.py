"Demo Flask application"
import json
import os
import subprocess
import urllib.request

from flask import Flask, render_template, render_template_string, url_for, redirect, flash, g
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, HiddenField, validators
import boto3

import config
import util

if "DYNAMO_MODE" in os.environ:
    import database_dynamo as database
else:
    import database

application = Flask(__name__)
application.secret_key = config.FLASK_SECRET

try:
    # this is how the CLI checks if metadata is available
    # https://github.com/boto/botocore/blob/5028b2106e078c4257be23db0905ac9a1593acf6/botocore/utils.py#L248
    doc_url = "http://169.254.169.254/latest/dynamic/instance-identity/document"
    doc = urllib.request.urlopen(doc_url, timeout=1).read().decode()
except urllib.error.URLError:
    print(" * Instance metadata not available")
    doc = '{ "availabilityZone" : "us-fake-1a",  "instanceId" : "i-fakeabc" }'

availablity_zone = json.loads(doc)["availabilityZone"]
instance_id = json.loads(doc)["instanceId"]

badges = {
    "apple" : "Mac User",
    "windows" : "Windows User",
    "linux" : "Linux User",
    "video-camera" : "Digital Content Star",
    "trophy" : "Employee of the Month",
    "camera" : "Photographer",
    "plane" : "Frequent Flier",
    "paperclip" : "Paperclip Afficionado",
    "coffee" : "Coffee Snob",
    "gamepad" : "Gamer",
    "bug" : "Bugfixer",
    "umbrella" : "Seattle Fan",
}

### FlaskForm set up
class EmployeeForm(FlaskForm):
    """flask_wtf form class"""
    employee_id = HiddenField()
    photo = FileField('image')
    full_name = StringField(u'Full Name', [validators.InputRequired()])
    location = StringField(u'Location', [validators.InputRequired()])
    job_title = StringField(u'Job Title', [validators.InputRequired()])
    badges = HiddenField(u'Badges')

@application.before_request
def before_request():
    "Set up globals referenced in jinja templates"
    g.availablity_zone = availablity_zone
    g.instance_id = instance_id

@application.route("/")
def home():
    "Home screen"
    s3_client = boto3.client('s3')
    employees = database.list_employees()
    if employees == 0:
        return render_template_string("""        
        {% extends "main.html" %}
        {% block head %}
        Employee Directory - Home
        <a class="btn btn-primary float-right" href="{{ url_for('add') }}">Add</a>
        {% endblock %}
        """)
    else:
        for employee in employees:
            try:
                if "object_key" in employee and employee["object_key"]:
                    employee["signed_url"] = s3_client.generate_presigned_url(
                        'get_object',
                        Params={'Bucket': config.PHOTOS_BUCKET, 'Key': employee["object_key"]}
                    )
            except: 
                pass

    return render_template_string("""
        {% extends "main.html" %}
        {% block head %}
        Employee Directory - Home
        <a class="btn btn-primary float-right" href="{{ url_for('add') }}">Add</a>
        {% endblock %}
        {% block body %}
            {%  if not employees %}<h4>Empty Directory</h4>{% endif %}

            <table class="table table-bordered">
              <tbody>
            {% for employee in employees %}
                <tr>
                  <td width="100">{% if employee.signed_url %}
                  <img width="50" src="{{employee.signed_url}}" /><br/>
                  {% endif %}
                  <a href="{{ url_for('delete', employee_id=employee.id) }}"><span class="fa fa-remove" aria-hidden="true"></span> delete</a>
                  </td>
                  <td><a href="{{ url_for('view', employee_id=employee.id) }}">{{employee.full_name}}</a>
                  {% for badge in badges %}
                  {% if badge in employee['badges'] %}
                  <i class="fa fa-{{badge}}" title="{{badges[badge]}}"></i>
                  {% endif %}
                  {% endfor %}
                  <br/>
                  <small>{{employee.location}}</small>
                  </td>
                </tr>
            {% endfor %}

              </tbody>
            </table>

        {% endblock %}
    """, employees=employees, badges=badges)

@application.route("/add")
def add():
    "Add an employee"
    form = EmployeeForm()
    return render_template("view-edit.html", form=form, badges=badges)

@application.route("/edit/<employee_id>")
def edit(employee_id):
    "Edit an employee"
    s3_client = boto3.client('s3')
    employee = database.load_employee(employee_id)
    signed_url = None
    if "object_key" in employee and employee["object_key"]:
        signed_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': config.PHOTOS_BUCKET, 'Key': employee["object_key"]}
        )

    form = EmployeeForm()
    form.employee_id.data = employee['id']
    form.full_name.data = employee['full_name']
    form.location.data = employee['location']
    form.job_title.data = employee['job_title']
    if 'badges' in employee:
        form.badges.data = employee['badges']

    return render_template("view-edit.html", form=form, badges=badges, signed_url=signed_url)

@application.route("/save", methods=['POST'])
def save():
    "Save an employee"
    form = EmployeeForm()
    s3_client = boto3.client('s3')
    key = None
    if form.validate_on_submit():
        if form.photo.data:
            image_bytes = util.resize_image(form.photo.data, (120, 160))
            if image_bytes:
                try:
                    # save the image to s3
                    prefix = "employee_pic/"
                    key = prefix + util.random_hex_bytes(8) + '.png'
                    s3_client.put_object(
                        Bucket=config.PHOTOS_BUCKET,
                        Key=key,
                        Body=image_bytes,
                        ContentType='image/png'
                    )
                except:
                    pass
        
        if form.employee_id.data:
            database.update_employee(
                form.employee_id.data,
                key,
                form.full_name.data,
                form.location.data,
                form.job_title.data,
                form.badges.data)
        else:
            database.add_employee(
                key,
                form.full_name.data,
                form.location.data,
                form.job_title.data,
                form.badges.data)
        flash("Saved!")
        return redirect(url_for("home"))
    else:
        return "Form failed validate"

@application.route("/employee/<employee_id>")
def view(employee_id):
    "View an employee"
    s3_client = boto3.client('s3')
    employee = database.load_employee(employee_id)
    if "object_key" in employee and employee["object_key"]:
        try:
            employee["signed_url"] = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': config.PHOTOS_BUCKET, 'Key': employee["object_key"]}
            )
        except:
            pass
    form = EmployeeForm()

    return render_template_string("""
        {% extends "main.html" %}
        {% block head %}
            {{employee.full_name}}
            <a class="btn btn-primary float-right" href="{{ url_for("edit", employee_id=employee.id) }}">Edit</a>
            <a class="btn btn-primary float-right" href="{{ url_for('home') }}">Home</a>
        {% endblock %}
        {% block body %}

  <div class="row">
    <div class="col-md-4">
        {% if employee.signed_url %}
        <img alt="Mugshot" src="{{ employee.signed_url }}" />
        {% endif %}
    </div>

    <div class="col-md-8">
      <div class="form-group row">
        <label class="col-sm-2">{{form.location.label}}</label>
        <div class="col-sm-10">
        {{employee.location}}
        </div>
      </div>
      <div class="form-group row">
        <label class="col-sm-2">{{form.job_title.label}}</label>
        <div class="col-sm-10">
        {{employee.job_title}}
        </div>
      </div>
      {% for badge in badges %}
      <div class="form-check">
        {% if badge in employee['badges'] %}
        <span class="badge badge-primary"><i class="fa fa-{{badge}}"></i> {{badges[badge]}}</span>
        {% endif %}
      </div>
      {% endfor %}
      &nbsp;
    </div>
  </div>
</form>
        {% endblock %}
    """, form=form, employee=employee, badges=badges)

@application.route("/delete/<employee_id>")
def delete(employee_id):
    "delete employee route"
    database.delete_employee(employee_id)
    flash("Deleted!")
    return redirect(url_for("home"))

@application.route("/info")
def info():
    "Webserver info route"
    return render_template_string("""
            {% extends "main.html" %}
            {% block head %}
                Instance Info
            {% endblock %}
            {% block body %}
            <b>instance_id</b>: {{g.instance_id}} <br/>
            <b>availability_zone</b>: {{g.availablity_zone}} <br/>
            <hr/>
            <small>Stress cpu:
            <a href="{{ url_for('stress', seconds=60) }}">1 min</a>,
            <a href="{{ url_for('stress', seconds=300) }}">5 min</a>,
            <a href="{{ url_for('stress', seconds=600) }}">10 min</a>
            </small>
            {% endblock %}""")

@application.route("/info/stress_cpu/<seconds>")
def stress(seconds):
    "Max out the CPU"
    flash("Stressing CPU")
    subprocess.Popen(["stress", "--cpu", "8", "--timeout", seconds])
    return redirect(url_for("info"))

if __name__ == "__main__":
    application.run(debug=True)
