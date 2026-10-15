from flask import Blueprint,abort,flash,g,redirect,render_template,request,url_for
from sqlalchemy.orm import selectinload
from .auth import login_required
from .extensions import db
from .models import Post,Tag
from .security import post_value

bp=Blueprint("posts",__name__,url_prefix="/posts")


def owned_post(post_id):
    post=db.session.scalar(db.select(Post).where(Post.id==post_id,Post.author_id==g.user.id))
    if post is None:
        abort(404,description="No accessible post with that ID.")
    return post


def read_fields():
    title=post_value(request.form.get("title",""),100)
    body=post_value(request.form.get("body",""),2000)
    values=request.form.getlist("tags")
    available=db.session.scalars(db.select(Tag).order_by(Tag.name)).all()
    allowed={tag.name:tag for tag in available}
    if title is None or body is None or len(values)>3 or len(values)!=len(set(values)) or any(v not in allowed for v in values):
        return None,"Use a title (1–100), body (1–2000), and up to three listed tags."
    return (title,body,[allowed[v] for v in values]),None


@bp.get("/")
@login_required
def index():
    query=request.args.get("q","").strip()
    raw_page=request.args.get("page","1")
    if len(query)>80 or not raw_page.isascii() or not raw_page.isdecimal() or not 1<=int(raw_page)<=1000:
        abort(400,description="Use a search of at most80characters and page1–1000.")
    statement=db.select(Post).where(Post.author_id==g.user.id).options(selectinload(Post.tags)).order_by(Post.id.desc())
    if query:
        statement=statement.where(Post.title.contains(query,autoescape=True))
    page=db.paginate(statement,page=int(raw_page),per_page=5,max_per_page=5,error_out=False)
    return render_template("posts.html",page=page,q=query)


@bp.get("/<int:post_id>")
@login_required
def detail(post_id):
    return render_template("detail.html",post=owned_post(post_id))


@bp.route("/create",methods=["GET","POST"])
@login_required
def create():
    error=None
    if request.method=="POST":
        fields,error=read_fields()
        if fields:
            title,body,tags=fields
            row=Post(title=title,body=body,author_id=g.user.id,tags=tags)
            db.session.add(row)
            db.session.commit()
            flash("Post created in your local database.","success")
            return redirect(url_for("posts.detail",post_id=row.id),code=303)
    return form_page(None,error)


@bp.route("/<int:post_id>/edit",methods=["GET","POST"])
@login_required
def edit(post_id):
    row=owned_post(post_id)
    error=None
    if request.method=="POST":
        fields,error=read_fields()
        if fields:
            row.title,row.body,row.tags=fields
            db.session.commit()
            flash("Your post was updated.","success")
            return redirect(url_for("posts.detail",post_id=row.id),code=303)
    return form_page(row,error)


def form_page(row,error):
    if request.method=="POST":
        title=request.form.get("title","")[:100]
        body=request.form.get("body","")[:2000]
        selected=request.form.getlist("tags")
    else:
        title=row.title if row else ""
        body=row.body if row else ""
        selected=[tag.name for tag in row.tags] if row else []
    tags=db.session.scalars(db.select(Tag).order_by(Tag.name)).all()
    return render_template("form.html",post=row,title=title,body=body,tags=tags,selected=selected,error=error),400 if error else 200


@bp.post("/<int:post_id>/delete")
@login_required
def delete(post_id):
    row=owned_post(post_id)
    db.session.delete(row)
    db.session.commit()
    flash("Your post was deleted.","info")
    return redirect(url_for("posts.index"),code=303)
