## Notes


TO DO:

* Add tests
* Research airflow of other scheduler to automate the running of the scraper

Research Questions:

1. I am currently using Poetry to manage dependencies. Is there a way to produce a requirements.txt file from the pyproject.toml or poetry.lock file? I want to dockerize this project but don't know how poetry interacts with docker, is there a simple fix for this?

2. Currently the output of the scraper gets written to a local database. How can I set up a database that is hosted via AWS? 

3. If the database is hosted on AWS, where does the script/process live? How can I make sure that the script is run routinely?
