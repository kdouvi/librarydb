from flask import render_template, request, redirect, session
from pythonlibrary import app, db

@app.route("/admin/loans", methods = ['GET', 'POST'])
def admin_loans():
    # authentication
    cur = db.connection.cursor()
    cur.execute("select username from Users where user_type = 'Administrator' limit 1;")
    a = cur.fetchall()
    print('Admin = ' + a[0][0])
    try:
        username = session['username']
    except KeyError:
        return redirect('/')
    print('Username = ' + username)
    if a[0][0] != username:
        return redirect('/')

    if request.method == 'GET':
        month = '01'
        year = '2023'
    elif request.method == 'POST':
        month = request.form['month']
        year = request.form['year']
    
    query = "select School.school_name, count(*) from ((Bor_Res join Users on Bor_Res.username = Users.username) join School on Users.school_id = School.school_id) where (type = 'Borrowing' and bor_res_time like('"
    query += year
    query += "-"
    query += month
    query += "____________')) group by School.school_id;"
    
    print("Query = " + query)
    cur.execute(query)
    schools = cur.fetchall()
    cur.close()
    print(schools)
    return render_template("admin_loans.html", schools = schools )

    
@app.route("/admin/authors_by_genre", methods = ['GET', 'POST'])
def admin_authors_by_genre():
    # authentication
    cur = db.connection.cursor()
    cur.execute("select username from Users where user_type = 'Administrator' limit 1;")
    a = cur.fetchall()
    print('Admin = ' + a[0][0])
    try:
        username = session['username']
    except KeyError:
        return redirect('/')
    print('Username = ' + username)
    if a[0][0] != username:
        return redirect('/')
    
    # getting genres for the drop-down list
    cur = db.connection.cursor()
    cur.execute("select distinct genre from Book_Genre;")
    genres = cur.fetchall()

    if request.method == 'GET':
        g = ''
    elif request.method == 'POST':
        g = request.form['genre']
    
    query1 = "select distinct first_name, last_name from Book_Author join Book_Genre on Book_Author.book_id = Book_Genre.book_id where genre = '"
    query1 += g
    query1 += "' order by first_name;"
    cur.execute(query1)
    authors = cur.fetchall()

    query2 = "select distinct first_name, last_name from (Users join (Bor_Res join Book_Genre on Bor_Res.book_id = Book_Genre.book_id) on Users.username = Bor_Res.username) where user_type = 'Educator' and Book_Genre.genre = '"
    query2 += g
    query2 += "';"
    cur.execute(query2)
    profs = cur.fetchall()
    cur.close()

    return render_template("authors_by_genre.html", genres = genres, authors = authors, profs = profs)

@app.route("/admin/young_profs")
def admin_young_profs():
    # authentication
    cur = db.connection.cursor()
    cur.execute("select username from Users where user_type = 'Administrator' limit 1;")
    a = cur.fetchall()
    print('Admin = ' + a[0][0])
    try:
        username = session['username']
    except KeyError:
        return redirect('/')
    print('Username = ' + username)
    if a[0][0] != username:
        return redirect('/')
    
    query = """ SELECT first_name, last_name, COUNT(*) AS loans
                FROM Bor_Res
                JOIN Users ON Bor_Res.username = Users.username
                WHERE user_type = 'Educator' AND TIMESTAMPDIFF(YEAR, date_of_birth, CURRENT_DATE()) < 40
                GROUP BY Users.username
                ORDER BY loans DESC; """
    
    cur.execute(query)
    profs = cur.fetchall()

    return render_template("admin_young_profs.html", profs = profs)

@app.route("/admin/unborrowed_authors")
def unborrowed_authors():
    # authentication
    cur = db.connection.cursor()
    cur.execute("select username from Users where user_type = 'Administrator' limit 1;")
    a = cur.fetchall()
    print('Admin = ' + a[0][0])
    try:
        username = session['username']
    except KeyError:
        return redirect('/')
    print('Username = ' + username)
    if a[0][0] != username:
        return redirect('/')

    query = """select first_name, last_name
                from (select first_name, last_name, count(Bor_Res.bor_res_time) as loans
                from (Bor_Res right join Book_Author on Bor_Res.book_id = Book_Author.book_id and type = 'Borrowing')
                group by first_name, last_name) as subquery where loans = 0;"""
    cur.execute(query)
    authors = cur.fetchall()

    return render_template("admin_unborrowed_authors.html", authors = authors)

@app.route("/admin/same_loans_no")
def same_book_no():
    # authentication
    cur = db.connection.cursor()
    cur.execute("select username from Users where user_type = 'Administrator' limit 1;")
    a = cur.fetchall()
    print('Admin = ' + a[0][0])
    try:
        username = session['username']
    except KeyError:
        return redirect('/')
    print('Username = ' + username)
    if a[0][0] != username:
        return redirect('/')

    query = """
                select School.operator_name, School.operator_surname, plithos_a from
                    (select a.school_id as col1, b.school_id, plithos_a from 
                    (select school_id, plithos_a from
                    (select Book.school_id, count(school_id) as plithos_a from
                    Bor_Res join Book on Bor_Res.book_id = Book.book_id
                    where timestampdiff(day, bor_res_time, current_timestamp) < 365
                    group by school_id) as a
                    ) as a
                    join (select school_id, plithos_b from
                    (select Book.school_id, count(school_id) as plithos_b from
                    Bor_Res join Book on Bor_Res.book_id = Book.book_id
                    where timestampdiff(day, bor_res_time, current_timestamp) < 365
                    group by school_id) as b 
                    ) as b
                    on a.plithos_a = b.plithos_b
                    where plithos_a >= 20 and a.school_id != b.school_id)
                    as pinakara
                join School on pinakara.col1 = School.school_id;
            """
    cur.execute(query)
    print(query)
    ops = cur.fetchall()
    print(ops)
    return render_template("same_loans_no.html", ops = ops)

@app.route("/admin/not_stephen_kings")
def not_stephen_kings():
    # authentication
    cur = db.connection.cursor()
    cur.execute("select username from Users where user_type = 'Administrator' limit 1;")
    a = cur.fetchall()
    print('Admin = ' + a[0][0])
    try:
        username = session['username']
    except KeyError:
        return redirect('/')
    print('Username = ' + username)
    if a[0][0] != username:
        return redirect('/')

    query = """ 
                select name, surname, count(*) as book_no from 
                (
                    SELECT DISTINCT ISBN, Book_Author.first_name AS name, Book_Author.last_name AS surname
                    FROM Book_Author
                    JOIN Book ON Book_Author.book_id = Book.book_id
                ) AS subsubquery
                GROUP BY name, surname
                having book_no <= 
                ((SELECT MAX(plithos) FROM
                (
                SELECT name, surname, COUNT(*) AS plithos
                FROM
                (
                    SELECT DISTINCT ISBN, Book_Author.first_name AS name, Book_Author.last_name AS surname
                    FROM Book_Author
                    JOIN Book ON Book_Author.book_id = Book.book_id
                ) AS subsubquery
                GROUP BY name, surname
                ) AS subquery)
                -5);
            """
    cur.execute(query)
    authors = cur.fetchall()

    return render_template("admin_not_stephen_kings.html", authors = authors)