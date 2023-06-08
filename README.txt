# librarydb
A college db project. To run the application, follow these steps:

1. Clone this repository to your system
2. Creating the database:
   Install MariaDB server on your system.
   In the MySQL CLI, run the following commands:
     create database giraffe
     ALTER DATABASE name CHARACTER SET='utf8'  COLLATE='utf8_bin';
     use giraffe
     source [your folder location]/dbsetup/Schema.sql
     source [your folder location]/dbsetup/Population.sql (to populate using our dummy data)
3. Setting up your python virtual environment
   Install the latest version of python from python.org, making sure that it gets added to your PATH environment variable.
   From a powershell, from inside the master folder of the clone of the repo, run the following command:
     python -m venv Giraffe
     ./Giraffe/Scripts/Activate.ps1
     pip install flask, Flask-MySQLdb, Flask-Session
4. Launching the app 
   From the same terminal as above, run:
     python app.py
   This will launch the app
5. Open your browser and go to localhost:3000
