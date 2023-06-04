-- TABLES

create table if not exists School (
    school_id int unsigned not null,
    school_name varchar(64) not null,
    principal_name varchar(64) not null,
    principal_surname varchar(64) not null,
    operator_name varchar(64) default null,
    operator_surname varchar(64) default null,
    email varchar(64) not null unique check (email like('%_@_%._%')),
    street varchar(64) not null,
    street_number smallint unsigned not null,
    city varchar(64) not null,
    zip_code mediumint unsigned not null check ( zip_code < 100000 ),
    phone_number bigint unsigned not null check ( phone_number < 10000000000 ),
    primary key (school_id)
) engine = InnoDB;


create table if not exists Book (
    book_id int unsigned not null unique auto_increment,
    school_id int unsigned not null,
    ISBN char(13) not null check (ISBN rlike('[0-9]{13}')),
    title varchar(64) not null,
    page_count int unsigned not null,
    lang varchar(64) not null,
    publisher varchar(64) not null,
    summary varchar(2000) not null,
    available_copies int not null,
    primary key (school_id, ISBN),
    constraint fk_book_school_id foreign key (school_id) references School (school_id) on delete restrict on update cascade
) engine = InnoDB;

create table if not exists Keywords (
    book_id int unsigned not null,
    keyword varchar(64) not null,
    primary key (book_id, keyword),
    constraint fk_keyword_book_id foreign key (book_id) references Book (book_id) on delete cascade on update cascade
) engine = InnoDB;

create table if not exists Book_Genre (
    book_id int unsigned not null,
    genre varchar(64) not null,
    primary key (book_id, genre),
    constraint fk_genre_book_id foreign key (book_id) references Book (book_id) on delete cascade on update cascade
) engine = InnoDB;

create table if not exists Book_Author (
    pk_book_author int unsigned not null auto_increment,
    book_id int unsigned not null,
    first_name varchar(64) not null,
    last_name varchar(64),
    primary key (pk_book_author),
    constraint fk_author_book_id foreign key (book_id) references Book (book_id) on delete cascade on update cascade
) engine = InnoDB;


create table if not exists Users(
    username varchar(64) not null,
    school_id int unsigned not null,
    phone_number bigint unsigned not null check ( phone_number < 10000000000 ),
    first_name varchar(64) not null,
    last_name varchar(64) not null,
    password varchar(64) not null,
    user_type enum(
        'Student',
        'Educator',
        'Operator',
        'Administrator'
    ) not null,
    date_of_birth date not null,
    primary key (username),
    constraint fk_user_school_id foreign key (school_id) references School (school_id) on delete restrict on update cascade
) engine = InnoDB;

create table if not exists Educator (
    username varchar(64) not null,
    token tinyint unsigned default 1,
    primary key (username),
    constraint fk_educator_username foreign key (username) references Users (username) on delete cascade on update cascade
) engine = InnoDB;

create table if not exists Student (
    username varchar(64) not null,
    token tinyint unsigned default 2,
    primary key (username),
    constraint fk_student_username foreign key (username) references Users (username) on delete cascade on update cascade
) engine = InnoDB;

create table if not exists Bor_Res (
    book_id int unsigned not null,
    username varchar(64) not null,
    bor_res_time timestamp default current_timestamp not null,
    returned_time timestamp null default null,
    type enum('Borrowing', 'Reservation', 'Pending Res') not null,
    primary key (bor_res_time, username),
    constraint fk_borres_book_id foreign key (book_id) references Book (book_id) on delete cascade on update cascade,
    constraint fk_borres_username foreign key (username) references Users (username) on delete cascade on update cascade
) engine = InnoDB;


create table if not exists Evaluation (
    book_id int unsigned not null,
    username varchar(64) not null,
    evaluation_date date not null default current_date,
    Likert_rating enum(
        'Sussy',
        'Meh',
        "It's aight",
        'Pretty lit',
        'Bussin ong'
    ) not null,
    review varchar(2000) null,
    primary key (book_id, username),
    constraint fk_eval_book_id foreign key (book_id) references book (book_id) on delete restrict on update cascade,
    constraint fk_eval_username foreign key (username) references users (username) on delete restrict on update cascade
) engine = InnoDB;


-- INDEXES


-- when searching books that belong to a school
create index fk_book_school_id_idx on Book (school_id);
-- when searching for a book by ISBN
create index fk_book_ISBN_idx on Book (ISBN);
--  when searching for the keywords, genres, authors of a book
create index fk_keyword_book_id_idx on Keywords (book_id);
create index fk_genre_book_id_idx on Book_Genre (book_id);
create index fk_author_book_id_idx on Book_Author (book_id);
-- when searching for the users of a school
create index fk_user_school_id_idx on Users (school_id);
-- When searching for the reservations of a user or book respectively
create index fk_borres_username_idx on Bor_Res (username);
create index fk_borres_book_id_idx on Bor_Res (book_id);


-- TRIGGERS


delimiter $
create trigger new_bor_res
before insert on Bor_Res
for each row
begin
    if (select count(1) from Users where username = new.username 
        and school_id <> (select school_id from Book where book_id = new.book_id)) then 
        signal sqlstate '45000'
        set message_text = 'You picked the wrong school, fool';
    end if;
    -- has borrowing overdue
    if (select count(1) from Bor_Res 
        where username = new.username 
        and returned_time is null
        and timestampdiff(minute, bor_res_time, new.bor_res_time)>20160)
      then
        signal sqlstate '45000'
        set message_text = 'Return your old book first, you must';
    end if;
    -- no tokens
    if (select count(1) from 
        (select username, token from Student where username = new.username 
        union
        select username, token from Educator where username = new.username)
        as tokens
        where tokens.token = 0) then
        signal sqlstate '45000'
        set message_text = 'No tokens, see ya next week';
    end if;
    -- already has it
    if (select count(1) from Bor_Res
        where Bor_Res.username = new.username and Bor_Res.book_id = new.book_id and returned_time is null
               and (Bor_Res.type <> 'Reservation' or new.type <> 'Borrowing' )) then
        signal sqlstate '45000'
        set message_text = 'Double trouble';
    end if;
    if (new.type = 'Borrowing' and new.returned_time is null) then
        if ((select available_copies from Book where Book.book_id = new.book_id) > 0) then
            update Book set available_copies = available_copies - 1 where book_id = new.book_id;
        else
            signal sqlstate '45000'
            set message_text = 'No available copies';
        end if;
    else if (new.type = 'Reservation') then
        if ((select available_copies from Book where Book.book_id = new.book_id) <= 0) then
            set new.type = 'Pending Res';            
        end if; 
        update Book set available_copies = available_copies - 1 where book_id = new.book_id;  
    end if;
    end if;
    if ((new.type <> 'Borrowing' or 
        (select count(1) from Bor_Res where Bor_Res.username = new.username and Bor_Res.book_id = new.book_id and Bor_Res.type = 'Reservation') = 0)
        and new.returned_time is null) then
        update Student set token = token - 1 where username = new.username;
        update Educator set token = token - 1 where username = new.username;
    end if;
end $
delimiter ;

delimiter $
create trigger returned_book
after update on Bor_Res
for each row
begin
if (new.returned_time is not null) then
    update Book set available_copies = available_copies + 1 where book_id = new.book_id;
end if;
end$ 
delimiter ;

delimiter $
create trigger cancelled_res
after delete on Bor_Res
for each row
begin
if (old.type <> 'Borrowing') then
    update Book set available_copies = available_copies + 1 where book_id = old.book_id;
    if ((weekday(current_date) >= weekday(date(old.bor_res_time)))
        and timestampdiff(minute, old.bor_res_time, current_timestamp) < 10080) then
        if ((select user_type from users where username = old.username) = 'Student') then
            update Student set token = token + 1 where username = old.username;
        else
            update Educator set token = token + 1 where username = old.username;
        end if;
    end if;
end if;
end $
delimiter ;

delimiter $
create trigger update_book
before insert on Book
for each row
begin
if ((select count(1) from Book where Book.ISBN = new.ISBN and Book.school_id = new.school_id) = 1) then
    if (new.title is not null) then
        update Book set Book.title = new.title where Book.ISBN = new.ISBN and Book.school_id = new.school_id;
    end if;
    if (new.page_count is not null) then
        update Book set Book.page_count = new.page_count where Book.ISBN = new.ISBN and Book.school_id = new.school_id;
    end if;
    if (new.lang is not null) then
        update Book set Book.lang = new.lang where Book.ISBN = new.ISBN and Book.school_id = new.school_id;
    end if;
    if (new.publisher is not null) then
        update Book set Book.publisher = new.publisher where Book.ISBN = new.ISBN and Book.school_id = new.school_id;
    end if;
    if (new.summary is not null) then
        update Book set Book.summary = new.summary where Book.ISBN = new.ISBN and Book.school_id = new.school_id;
    end if;
    if (new.available_copies is not null) then
        update Book set Book.available_copies = new.available_copies where Book.ISBN = new.ISBN and Book.school_id = new.school_id;
    end if;
end if;
end $
delimiter ;

delimiter $
create trigger new_user_who_dis
after insert on Users
for each row
begin
    if (new.user_type = 1) then
        insert into Student values (new.username, default);
    else if (new.user_type = 2) then
        insert into Educator values (new.username, default);
    else if (new.user_type = 3) then
        if (select count(1) from Users where school_id = new.school_id and user_type = 'Operator' and username <> new.username) then
            delete from Users where username = new.username; 
            signal sqlstate '45000'  
            set message_text = 'Operator already exists for this school';
        end if;
        update school set operator_name = new.first_name, operator_surname = new.last_name where school_id = new.school_id;
end if;
end if;
end if;      
end $
delimiter ;

delimiter $
create trigger available_again
after update on Book
for each row
begin
if (new.available_copies > old.available_copies and old.available_copies <= 0) then
    if (select count(1) from Bor_Res where type = 'Pending Res' and book_id = new.book_id) then
        update Bor_Res set type = 'Reservation' where (Bor_Res.book_id = new.book_id) and 
                                                       bor_res_time = (select min(bor_res_time) from Bor_Res where type = 'Pending Res' and book_id = new.book_id);
    end if;
end if;
end $
delimiter ;


-- EVENTS


delimiter $
create event delete_week_old_res 
on schedule 
every 1 day_hour 
do begin
delete from Bor_Res where (type = 'Reservation' AND timestampdiff(minute, bor_res_time, now())>10080);
end $
delimiter ;

delimiter $
create event token_giveinator_edu 
on schedule 
every 1 week
starts current_date + interval(7 - weekday(current_date)) day 
do begin
update Educator set token = 1;
end $
delimiter ;

delimiter $
create event token_giveinator_stu 
on schedule 
every 1 week
starts current_date + interval(7 - weekday(current_date)) day 
do begin
update Student set token = 2;
end $
delimiter ;