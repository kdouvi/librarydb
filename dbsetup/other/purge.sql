-- drop everything, start over

drop table if exists
Evaluation,
Bor_Res,
Student,
Educator,
Operator,
Administrator,
Users,
Book_Author,
Book_Genre,
Keywords,
Book,
School;

drop trigger if exists
new_bor_res;

drop trigger if exists
returned_book;

drop trigger if exists
cancelled_res;

drop trigger if exists
update_book;

drop trigger if exists
new_user_who_dis;

drop trigger if exists
available_again;

drop event if exists
delete_week_old_res;

drop event if exists
token_giveinator_edu;

drop event if exists
token_giveinator_stu;