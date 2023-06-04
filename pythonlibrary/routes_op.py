from flask import render_template, request, redirect, session
from pythonlibrary import app, db

@app.route("/op/catalogue", methods = ['GET','POST'])
def catalogue():
    # authentication
    try:
        username = session['username']
    except KeyError:
        return redirect('/')
    cur = db.connection.cursor()
    auth_q = "select count(1) from Users where user_type = 'Operator' and username = '" + username +"';"
    cur.execute(auth_q)
    a = cur.fetchall()
    if a[0][0] == 0:
        return redirect('/')
    
    if request.method == 'GET':
        search_terms = ['','','','']
    elif request.method == 'POST':
        search_terms = [request.form['title'], request.form['genre'], request.form['author'], request.form['copies']]

    sid = session['school_id']
    
    query = "select title, first_name, last_name, available_copies from (Book left join Book_Author on Book.book_id = Book_Author.book_id) left join Book_Genre on Book_Genre.book_id = Book.book_id where school_id = "
    query += str(sid)
    query += " and title like('%"
    query += search_terms[0]
    query += "%') and CONCAT(first_name, ' ', last_name) like('%"
    query += search_terms[2]
    query += "%') and genre like('%"
    query += search_terms[1]
    query += "%') group by Book.book_id"
    if (search_terms[3] != '-'):
        query += (" order by available_copies " + search_terms[3])
    query +=';'
    
    cur.execute(query)
    books = cur.fetchall()
    cur.close()

    return render_template("op_catalogue.html", books = books)

@app.route("/op/overdue_loans", methods = ['GET','POST'])
def overdue_loans():
    # authentication
    try:
        username = session['username']
    except KeyError:
        return redirect('/')
    cur = db.connection.cursor()
    auth_q = "select count(1) from Users where user_type = 'Operator' and username = '" + username +"';"
    cur.execute(auth_q)
    a = cur.fetchall()
    if a[0][0] == 0:
        return redirect('/')

    if request.method == 'GET':
        search_terms = ['','','0']
    elif request.method == 'POST':
        search_terms = [request.form['first name'], request.form['last name'], request.form['days overdue']]
    
    sid = session['school_id']

    query = """
            select Users.username, first_name, last_name, timestampdiff(day, bor_res_time, current_timestamp)
            from Users
            join Bor_Res on Users.username = Bor_Res.username 
            where (returned_time is null
            and timestampdiff(hour, bor_res_time, current_timestamp) > (14+
            """
    query += search_terms[2]
    query += ")*24 and Users.first_name like('%"
    query += search_terms[0]
    query += "%') and Users.last_name like('%"
    query += search_terms[1]
    query += "%')and Users.school_id = "
    query += str(sid)
    query += ");"

    cur.execute(query)
    users = cur.fetchall()
    cur.close()

    return render_template("op_overdue_loans.html", users = users)

@app.route("/op/eval_average", methods = ['GET','POST'])
def avr_rating():
    # authentication
    try:
        username = session['username']
    except KeyError:
        return redirect('/')
    cur = db.connection.cursor()
    auth_q = "select count(1) from Users where user_type = 'Operator' and username = '" + username +"';"
    cur.execute(auth_q)
    a = cur.fetchall()
    if a[0][0] == 0:
        return redirect('/')

    if request.method == 'GET':
        search_terms = ['','']
    elif request.method == 'POST':
        search_terms = [request.form['username'], request.form['genre']]

    sid = session['school_id']

    # getting genres for the drop-down list
    cur = db.connection.cursor()
    cur.execute("select distinct genre from Book_Genre;")
    genres = cur.fetchall()

    query = """SELECT Users.username, first_name, last_name, ROUND(AVG(Likert_rating), 1)
            FROM Users
            JOIN Evaluation ON Users.username = Evaluation.username
            JOIN Book_Genre ON Evaluation.book_id = Book_Genre.book_id
            WHERE Users.username LIKE '%"""
    query += search_terms[0]
    query += "%' AND Book_Genre.genre LIKE '%"
    query += search_terms[1]
    query += "%' AND Users.school_id ="
    query += str(sid)
    query += " GROUP BY Users.username, first_name, last_name;"

    print(query)

    cur.execute(query)
    evals = cur.fetchall()
    cur.close()

    l = len(evals)
    
    if l != 0:
        s=0
        for student in evals:
            s += student[3]
            avr = s / len(evals)
    else:
        avr = '-'

    return render_template("op_avr_rating.html", evals = evals, genres = genres, avr = avr)