from bookui.app import app
from flask import render_template, redirect
from bookui.app import book

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/toc')
def toc():
    return render_template('toc.html', chapters=[(i+1, c['title']) for i, c in enumerate(book)])


@app.route('/chapter/<int:cno>')
@app.route('/chapter/<int:cno>/<int:pno>')
def chapter(cno, pno=1):
    chap = book[cno-1]
    content = chap['content'][pno-1]
    content = content.replace('<phrase>','<span class="phrase">').replace('</phrase>', '</span>')
    return render_template('chapter.html',
                           cno=cno,
                           pno=pno,
                           ptot=len(chap['content']),
                           content=content,
                           ctitle=chap['title'])
