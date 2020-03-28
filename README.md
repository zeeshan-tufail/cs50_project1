# Project 1

Web Programming with Python and JavaScript

Short Description: To build book review site using below framework and languages:
---------------------------------------------------------------------------------
	- HTML5, Bootstrap CSS and Custom SASS file
	- SQLAlchemy for DB execution
	- Cloud Heroku Prostgre DB  
	- Python 3.8
	- goodreads API

Python File Descriptions:
------------------------
	- import.py : Stand-alone program use to load books.csv data into books table.
	- application.py: Main python web application program to handles the web request and response, Also published API book detail resource. 


HTML templates File Descriptions:
------------------------
	- layout.html : It is use as template.
	- register.html :  User registration page, to create a username and password.
	- login.html : Site login page to enter the website.
	- searchbook.html : It use to search books for reviews. You can search by isbn, title or author.
	- detailbook.html : Book detail with reviews, and you can also add reviews. On this page we are getting counts and rating from goodreads API.

Book Reviews API Resource:
--------------------------
	- http://localhost:5000/api/bookdetail/<isbn>


CSS:
---
 static folder contains sass and css file
 

