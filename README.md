# MapleCoin

This is the source code of the Maple Coin Network for aspiring developers wishing to explore the world of the Maple Coin network and take part in it.

Instructions on how to use it:

1) Have python3 and Django already installed on your device along with the libraries from requirements.txt of the Mining Software (This step is integral!)

2) Running the server in a virtual environment is recommended to avoid issues and interference with other local projects.

3) Through Command Prompt (For Windows) or Terminal (For macOS), navigate to the project directory (Using "cd/path/to/files")

4) Run "py manage.py makemigrations" followed by "py manage.py migrate" for Windows Or "python3 manage.py makemigrations" followed by "python3 manage.py migrate" for macOS. This is to make sure that your local SQL database is in sync with the network database (Only structure, not entries)

5)Static Files and Media Files do not need to be collected on a local Django Server; it is done automatically.

6)Go to settings.py in the project directory and set "DEBUG = True"

7)Run the server by using the following command: "py manage.py runserver" for Windows; "python3 manage.py runserver" for macOS.

8)Set the Mining Software's global variable "networkSite = 'http://127.0.0.1:8000'" to use the mining software with the local Maple Coin Network

9)Visit the site on your local browser using the address: "http://127.0.0.1:8000"
