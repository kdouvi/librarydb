from flask import render_template, request, redirect, session
from pythonlibrary import app, db
import MySQLdb

@app.route("/user/catalogue", methods = ['GET', 'POST'])
def user_catalogue():
    # authentication
    try:
        username = session['username']
    except KeyError:
        return redirect('/')
    cur = db.connection.cursor()
    auth_q = "select count(1) from Users where user_type <=2  and username = '" + username +"';"
    cur.execute(auth_q)
    a = cur.fetchall()
    if a[0][0] == 0:
        return redirect('/')
    
    if request.method == 'GET':
        search_terms = ['','','']
    elif request.method == 'POST':
        search_terms = [request.form['title'], request.form['genre'], request.form['author']]

    sid = session['school_id']

    query = """
            SELECT bookid, title, authors, summary, pc, ac, genres, ROUND(average_rating, 1) FROM
            (
            SELECT books.book_id as bookid, books.title as title, books.author_names as authors, books.summary as summary,
                books.page_count as pc, books.available_copies as ac, genres.genre_names as genres,
                AVG(Evaluation.Likert_rating) AS average_rating, books.school_id as sch
            FROM (
            SELECT Book.book_id, Book.title, Book.summary, Book.page_count, Book.available_copies, Book.school_id,
                    GROUP_CONCAT(CONCAT(Book_Author.first_name, ' ', Book_Author.last_name) SEPARATOR ', ') AS author_names
            FROM Book
            JOIN Book_Author ON Book.book_id = Book_Author.book_id
            GROUP BY Book.book_id, Book.title, Book.summary, Book.page_count, Book.available_copies
            ) AS books
            JOIN (
            SELECT Book.book_id,
                    GROUP_CONCAT(DISTINCT Book_Genre.genre SEPARATOR ', ') AS genre_names
            FROM Book
            JOIN Book_Genre ON Book.book_id = Book_Genre.book_id
            GROUP BY Book.book_id
            ) AS genres ON books.book_id = genres.book_id
            LEFT JOIN Evaluation ON books.book_id = Evaluation.book_id
            GROUP BY books.book_id, books.title, books.author_names, books.summary, books.page_count, books.available_copies, genres.genre_names
            ORDER BY books.book_id
            ) as books
            WHERE books.title LIKE '%"""
    query += search_terms[0]
    query += "%' AND books.authors LIKE '%"
    query += search_terms[2]
    query += "%' AND books.genres LIKE '%"
    query += search_terms[1]
    query += "%' AND books.sch = "
    query += str(sid)
    query += ";"

    cur.execute(query)
    books = cur.fetchall()
    cur.close()

    return render_template("user_catalogue.html", books = books)

@app.route("/user/loans_and_reservations")
def loans_and_reservations():
    # authentication
    try:
        username = session['username']
    except KeyError:
        return redirect('/')
    cur = db.connection.cursor()
    auth_q = "select count(1) from Users where user_type <=2  and username = '" + username +"';"
    cur.execute(auth_q)
    a = cur.fetchall()
    if a[0][0] == 0:
        return redirect('/')
    
    query = "select Book.book_id, Book.title, substring(bor_res_time, 1, 16), substring(returned_time, 1, 16) from Book join Bor_Res on Book.book_id = Bor_Res.book_id where username = '"
    query1 = query + username + "' and type = 'Borrowing';"
    query2 = query + username + "' and type = 'Reservation';"
    
    cur.execute(query1)
    loans = cur.fetchall()
    cur.execute(query2)
    reservations = cur.fetchall()
    cur.close()

    return render_template("user_loans_and_reservations.html", loans = loans, reservations = reservations)

@app.route("/user/reserve_book", methods= ['POST'])
def reserve_book():
    # authentication
    try:
        username = session['username']
    except KeyError:
        return redirect('/')
    cur = db.connection.cursor()
    auth_q = "select count(1) from Users where user_type <=2  and username = '" + username +"';"
    cur.execute(auth_q)
    a = cur.fetchall()
    if a[0][0] == 0:
        return redirect('/')
    
    bid = request.form['book_id']

    print("BOOK REQUESTED: "+ str(bid))
    query = "insert into Bor_Res values ("+str(bid)+",'"+username+"',default,default,'Reservation');"
    
    try:
        cur.execute(query)
        db.connection.commit()
        cur.close()
        return render_template("user_res_ok.html")
    except MySQLdb.OperationalError as e:
        session['error_msg'] = e.args[1]
        return redirect("/")