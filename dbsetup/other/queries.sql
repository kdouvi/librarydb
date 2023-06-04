-- Admin

-- 1
select School.school_name, count(*) 
from ((Bor_Res join Users on Bor_Res.username = Users.username) join School on Users.school_id = School.school_id)
where (type = 'Borrowing' and bor_res_time like("2022-______________"))
group by School.school_id;

--2
select distinct first_name, last_name from Book_Author join Book_Genre on Book_Author.book_id = Book_Genre.book_id where genre = 'Fantasy' order by first_name;
select first_name, last_name from (Users join (Bor_Res join Book_Genre on Bor_Res.book_id = Book_Genre.book_id) on Users.username = Bor_Res.username) where user_type = 'Educator' and Book_Genre.genre = 'Fantasy';

--3
SELECT first_name, last_name, COUNT(*) AS loans
FROM Bor_Res
JOIN Users ON Bor_Res.username = Users.username
WHERE user_type = 'Educator' AND TIMESTAMPDIFF(YEAR, date_of_birth, CURRENT_DATE()) < 40
GROUP BY Users.username
ORDER BY loans DESC;

--4
select first_name, last_name
from (select first_name, last_name, count(Bor_Res.bor_res_time) as loans
from (Bor_Res right join Book_Author on Bor_Res.book_id = Book_Author.book_id and type = 'Borrowing')
group by first_name, last_name) as subquery where loans = 0;

--5
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

-- 7
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

-- Op

-- 1
select title, first_name, last_name, available_copies
from (Book left join Book_Author on Book.book_id = Book_Author.book_id) left join Book_Genre on Book_Genre.book_id = Book.book_id
where school_id = 551003 and title like('%') and CONCAT(first_name, ' ', last_name) like('%%') and genre like('%%')
group by Book.book_id order by available_copies asc;


-- 2
;
select Users.username, first_name, last_name, timestampdiff(day, bor_res_time, current_timestamp)
from Users
join Bor_Res on Users.username = Bor_Res.username 
where (returned_time is null
and timestampdiff(hour, bor_res_time, current_timestamp) > (14)*24 
and Users.first_name like('%%')
and Users.last_name like('%%')
and Users.school_id = 920305
);

-- 3
;
select Users.username, first_name, last_name, round(avg(Likert_rating), 1) from
(Users join Evaluation on Users.username = Evaluation.username) as ev_usr
join Book_Genre on ev_usr.book_id = Book_Genre.book_id
where Users.username like('%%') and Book_Genre.genre like('%%')
group by Users.username, first_name, last_name;

SELECT Users.username, first_name, last_name, ROUND(AVG(Likert_rating), 1)
FROM Users
JOIN Evaluation ON Users.username = Evaluation.username
JOIN Book_Genre ON Evaluation.book_id = Book_Genre.book_id
WHERE Users.username LIKE '%%' AND Book_Genre.genre LIKE '%%'
AND Users.school_id = 920305
GROUP BY Users.username, first_name, last_name;

-- User

-- 1
;
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
WHERE books.title LIKE '%%' AND books.authors LIKE '%%' AND books.genres LIKE '%%' AND books.sch = 920305;

--2
;
select Book.book_id, Book.title, substring(bor_res_time, 1, 16), substring(returned_time, 1, 16) from Book join Bor_Res on Book.book_id = Bor_Res.book_id where username = "fred.weasley@gmail.com" and type = 'Borrowing';
select Book.book_id, Book.title, substring(bor_res_time, 1, 16) from Book join Bor_Res on Book.book_id = Bor_Res.book_id where username = "fred.weasley@gmail.com" and type = 'Reservation';
