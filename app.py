from flask import Flask, render_template, request, redirect
from models import db, User, Post, Like, Comment
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db.init_app(app)

current_user = None


@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        file = request.files["image"]
        caption = request.form["caption"]

        if file:
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

            post = Post(
                image=file.filename,
                caption=caption
            )

            db.session.add(post)
            db.session.commit()

            return redirect("/")

    posts = Post.query.all()

    likes = {}
    comments = {}

    for post in posts:
        likes[post.id] = Like.query.filter_by(post_id=post.id).count()
        comments[post.id] = Comment.query.filter_by(post_id=post.id).all()

    return render_template(
        "home.html",
        posts=posts,
        likes=likes,
        comments=comments
    )


@app.route("/like/<int:post_id>")
def like(post_id):

    like = Like(post_id=post_id)

    db.session.add(like)
    db.session.commit()

    return redirect("/")


@app.route("/comment/<int:post_id>", methods=["POST"])
def comment(post_id):

    text = request.form["comment"]

    comment = Comment(
        text=text,
        post_id=post_id
    )

    db.session.add(comment)
    db.session.commit()

    return redirect("/")


@app.route("/delete/<int:post_id>")
def delete(post_id):

    post = Post.query.get(post_id)

    if post:

        image_path = os.path.join(app.config["UPLOAD_FOLDER"], post.image)

        if os.path.exists(image_path):
            os.remove(image_path)

        db.session.delete(post)
        db.session.commit()

    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User(
            username=username,
            password=password
        )

        db.session.add(user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    global current_user

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(
            username=username,
            password=password
        ).first()

        if user:
            current_user = user
            return redirect("/")

    return render_template("login.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)