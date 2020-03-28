import os, requests

from flask import Flask,  render_template, request, session, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = "super secret key"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    error =""
    #session["user_id"]=None
    session.clear()
    return render_template("login.html", error=error)

@app.route("/signup")
def signup():   
    return render_template("register.html")

@app.route("/logout")
def logout():
    #session["user_id"]=None
    session.clear()
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    userName = request.form.get("userName")
    password = request.form.get("password")
    
    if userName == "" or userName is None:
        error = "Enter valid user name."
        return render_template("login.html", error=error) 
    if password == "" or password is None:
        error = "Enter valid password."
        return render_template("login.html", error=error) 
    
    #check this user exist in DB
    user = db.execute("select * from users where username=:userName and password=:password", {"userName":userName, "password":password}).fetchone()
    if user is None:
        error = "Make sure User Name and Password are correct. For registration, Please click Sign Up."
        return render_template("login.html", error=error)
                                                                                   
    #Store in session
    session["user_id"]=user.id

    # return to home page
    return render_template("searchbook.html") 


@app.route("/register", methods=["POST"])
def register():
    userName = request.form.get("userName")
    password = request.form.get("password")
    confirmPassword = request.form.get("confirmPassword")
    
    if userName == "" or userName is None:
        error = "Enter valid user name."
        return render_template("register.html", error=error) 
    if password == "" or password is None:
        error = "Enter valid password."
        return render_template("register.html", error=error)      
    if password != confirmPassword:
        error = "Password mismatch"
        return render_template("register.html", error=error)      
    
    #check userName should unique in table
    user = db.execute("select * from users where username=:userName", {"userName":userName}).fetchone()
    if user is None:       
        db.execute("insert into users(username, password) values(:userName,:password)",{"userName":userName,"password":password})
        db.commit()
    else:
        error = "User Name already exists, Please choose another User Name."
        return render_template("register.html", error=error)
        
    # return to home page
    return render_template("register.html", success="User registered successfully. Click Sign In for book reviews.") 

@app.route("/searchbook", methods=["GET","POST"])
def searchbook():
    userId = session.get("user_id")   
    if userId is None:
        return render_template("login.html")
    
    isbn = request.form.get("isbn")
    title = request.form.get("title")
    author = request.form.get("author")
    
    if isbn== "" and title=="" and author=="":
        error = "Either of ISBN, title or author required."
        return render_template("searchbook.html", error=error) 
        
    #Get book list from DB
    try:   
        books = db.execute("select * from books where isbn like :isbn and lower(title) like :title and lower(author) like :author", 
                           {"isbn":f"%{isbn}%", "title":f"%{title.lower()}%", "author":f"%{author.lower()}%"}).fetchall()
    except:
        #raise Exception("Error: DB server down.")
        return render_template("searchbook.html", error="DB server down.")
    
    if len(books) == 0 or books is None:
        return render_template("searchbook.html", error="No results found.") 
    
    return render_template("searchbook.html", books=books) 

def goodreadsreview(isbn):
    data=[]
    try:
        res = requests.get("https://www.goodreads.com/book/review_counts.json", 
                       params={"key": "WB4gWpmKCNlYTQ0xnIiCmg", "isbns": isbn})
        if res.status_code != 200:
            #raise Exception("Error: API request unsuccessful.")
            print("Error: API request unsuccessful.")
        
        data = res.json()["books"][0]
        #print(data)  
    except:
         print("Error: API request unsuccessful.")
         
    return data

def getBookByISBN(isbn):
    book = db.execute("select * from books where isbn=:isbn", {"isbn":isbn}).fetchone()   
    return book

def getReviewsByISBN(isbn):      
    reviews=db.execute("select * from reviews where book_isbn=:isbn", {"isbn":isbn}).fetchall()
    return reviews

@app.route("/detailbook/<string:isbn>")
def detailbook(isbn):   
    userId = session.get("user_id")   
    if userId is None:
        return render_template("login.html")
    
    book = getBookByISBN(isbn)
    reviews = getReviewsByISBN(isbn)
    goodreads = goodreadsreview(isbn) 
    return render_template("detailbook.html", book=book, reviews=reviews, goodreads=goodreads)


@app.route("/api/bookdetail/<string:isbn>")
def bookdetail(isbn):   
    book = getBookByISBN(isbn)   
    goodreads = goodreadsreview(isbn) 
    if book is None:
        return jsonify({"Error":"Invalid ISBN"}, 404)
    if goodreads is None or len(goodreads)==0:
        return jsonify({"Error":"Invalid ISBN"}, 404)
        
    return jsonify({
        "title": book.title,
        "author": book.author,
        "year": book.year,
        "isbn": book.isbn,
        "review_count": goodreads["work_ratings_count"],
        "average_score": goodreads["average_rating"]
    }) 



@app.route("/addreview", methods=["POST"])
def addreview():    
    isbn = review = request.form.get("isbn")
    userId = session.get("user_id")   
    
    book = getBookByISBN(isbn)
    allreviews = getReviewsByISBN(isbn)    
    goodreads = goodreadsreview(isbn)  
    #print("isbn=" + isbn +", userId=" + str(userId))    
    reviewByUser = db.execute("select * from reviews where book_isbn=:isbn and user_id=:userId", {"isbn":str(isbn), "userId":userId}).fetchone()
    if reviewByUser is None: 
        review = request.form.get("review")
        rate = request.form.get("rate")        
        if review == "" or review is None:
            error = "Please enter review."
            return render_template("detailbook.html", error=error, book=book, review=allreviews, goodreads=goodreads)  
             
        db.execute("insert into reviews(review, rating, book_isbn, user_id) values(:review, :rating, :book_isbn, :user_id)",
                   {"review":review, "rating":rate, "book_isbn":isbn, "user_id":userId})
        db.commit()  
        allreviews = getReviewsByISBN(isbn)     
        return render_template("detailbook.html", book=book, reviews=allreviews, goodreads=goodreads)
    else:        
        error = "Review already added by you for this book."
        return render_template("detailbook.html", error=error, book=book, reviews=allreviews, goodreads=goodreads)    
        

@app.route("/navigatesearchbook")
def navigatesearchbook():
    return render_template("searchbook.html") 

if __name__ == "__main__":
    app.run()
