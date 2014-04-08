# coding: utf-8 
# vim:fdm=marker:fmr=\:,\:
# required python packages: flask, markdown

import sys, os.path #:1
import logging, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

import markdown
from flask import Flask, request, render_template, url_for, redirect, abort, flash, abort, Markup
from google.appengine.ext import ndb


if os.environ.get('SERVER_SOFTWARE', '').startswith('Development'):
    DEBUG = True
else:
    DEBUG = False

SECRET_KEY = 'EGO03043'

app = Flask(__name__)
app.config.from_object(__name__)

# Model :1
class Post(ndb.Model):
    body  = ndb.TextProperty()
    created_date = ndb.DateProperty(auto_now_add=True)

    @property
    def key_name(self):
        return self.key.id()


# Views :1
@app.route('/')
def home_page():
    p = Post.query().order(-Post.created_date).fetch(1)
    if p:
        p = p[0]
    else:
        p = None
    return render_template('post.html', p=p)


@app.route('/<key_name>')
def view_post(key_name):
    p = Post.get_by_id(key_name)
    return render_template('post.html', p=p)


@app.route('/add', methods=['GET', 'POST'])
def add_post():
    if request.method == 'GET':
        return render_template('form-post.html', p=None)

    url_id = request.form['url_id']
    body   = request.form['body']
    pe = Post.get_by_id(url_id)
    if pe:
        flash('Already existed for that url id')
        p = Post(id=url_id, body=body)
        return render_template('form-post.html', p=p)

    p = Post(id=url_id, body=body)
    p.put()
    flash('successfuly saved')

    return redirect(url_for('view_post', key_name=p.key.id()))


# Utils :1
def static_url(name):
    production_cdn = {
            'bootstrap.js':  '//netdna.bootstrapcdn.com/bootstrap/3.1.1/js/bootstrap.min.js',
            'html5shiv.js':  'https://oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js',
            'respond.js':  'https://oss.maxcdn.com/libs/respond.js/1.4.2/respond.min.js',
            'jquery.js':  'https://ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js',

            'bootstrap.css': '//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css',
            'normalize.css': '//localhost:7000/css/normalize.css',
            }

    local_cdn = {
            'bootstrap.css': '//localhost:7000/css/bootstrap.min.css',
            'normalize.css': '//localhost:7000/css/normalize.css',

            'bootstrap.js':  '//localhost:7000/js/bootstrap.min.js',
            'html5shiv.js':  '//localhost:7000/js/html5shiv.js',
            'respond.js':  '//localhost:7000/js/respond.min.js',
            'jquery.js':  '//localhost:7000/js/jquery.js',
            }

    if DEBUG:
        return local_cdn[name]
    else:
        return production_cdn[name]


def to_html(text):
    return Markup(markdown.markdown(text))


# adding custom filter
app.jinja_env.filters['static_url'] = static_url
app.jinja_env.filters['to_html'] = to_html
