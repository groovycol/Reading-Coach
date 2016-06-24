# The Reading Coach

![capture](https://cloud.githubusercontent.com/assets/7019142/16339366/2a7e8d94-39d7-11e6-9584-1eeeabc3261f.PNG)

The Reading Coach is a web application that allows Parents and Teachers/Administrators to track the number of minutes a Student has read.

  - Parents or Caregivers can login to record and view the number of minutes their Student has read for the days in the program.
  - Parents can opt in to receive occasional text message reminders. 
  - Parents can also log minutes by sending a text message to the applications webhook phone number.
  - Teachers/Administrators can login to view the progress of all their Students
  - Teachers have the option to send a text message to the Student's family with messages of encouragement or practical advice

The Reading Coach came about as the brainchild of an elementary teacher in Berkeley, CA. After reading this [article](http://goo.gl/YIUrb5) in the New York Times demonstrating the power that text message reminders can have in helping people build habits, she envisioned an application that would send text reminders to parents during the 10 weeks of summer break. The text would remind them to get their student to read, and prompt them to log how many minutes they had read that day. In her vision, both parents and teachers would be able to see the student's recorded reading minutes in a browser, but busy parents could log their student's progress from a phone.[df1]

> Our most struggling readers make good progress during the school year. They make steady progress for 9 months, sometimes even outpacing their peers.  We expect our students grades 1 - 5 to do a daily reading log that tracks their reading, encouraging students to do at least 10 minutes and as much as 40 minutes OUTSIDE of school.  When teachers and families are both adhering to this expectation, students can make dramatic and quick gains. Over the summer, we want to be able to check in regularly with families to say "Keep it Up", "You're making a difference when you support your child in reading. When I learned how text messaging was supporting early language and literacy efforts with the Raising a Reader Program, I immediately saw how this could support families over the long 10 weeks of summer.


Version
----
1.0

Tech
----

The Reading Coach uses
* [Python](https://www.python.org/) - powerful programming language
* [Flask](http://flask.pocoo.org/) - web framework for Python
* [PostgreSQL](https://www.postgresql.org/) - The world's most advanced open source database
* [SQLAlchemy](http://www.sqlalchemy.org/) - Database toolkit for Python
* [Jinja2](http://jinja.pocoo.org/docs/dev/) - Templating language
* [Twilio](https://www.twilio.com/sms) - Programmable SMS RESTful API
* [Chart.js](http://www.chartjs.org/) - JavaScript library that renders charts
* [jQuery] - JavaScript library for manipulating the DOM
* [Ajax](https://developer.mozilla.org/en-US/docs/AJAX) - 
* [Twitter Bootstrap] - great UI boilerplate for modern web apps

And of course The Reading Coach itself is open source with a [public repository](https://github.com/groovycol/Reading-Coach)
 on GitHub.

To run the application
----

```
$ git clone [git-repo-url] readcoach

$ cd readcoach

$ virtualenv env

$ source env/bin/activate

$ pip install -r requirements.txt

$ python server.py
```

Version 2.0
----
- add a scheduler on the back end to manage sending text messages at user-specified intervals. 
- Add a way for Teachers/Administrators to add lists of recommended books
- display total number of minutes read on Student detail pages
- display the titles read on the Student detail pages
- implement a rewards system of badges and achievements for milestones reached

Author
----
Colleen Blakelock is a software engineer from Oakland, CA



[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)


   [dill]: <https://github.com/joemccann/dillinger>
   [git-repo-url]: <https://github.com/joemccann/dillinger.git>
   [john gruber]: <http://daringfireball.net>
   [@thomasfuchs]: <http://twitter.com/thomasfuchs>
   [df1]: <http://daringfireball.net/projects/markdown/>
   [markdown-it]: <https://github.com/markdown-it/markdown-it>
   [Ace Editor]: <http://ace.ajax.org>
   [node.js]: <http://nodejs.org>
   [Twitter Bootstrap]: <http://twitter.github.com/bootstrap/>
   [keymaster.js]: <https://github.com/madrobby/keymaster>
   [jQuery]: <http://jquery.com>
   [@tjholowaychuk]: <http://twitter.com/tjholowaychuk>
   [express]: <http://expressjs.com>
   [AngularJS]: <http://angularjs.org>
   [Gulp]: <http://gulpjs.com>

   [PlDb]: <https://github.com/joemccann/dillinger/tree/master/plugins/dropbox/README.md>
   [PlGh]:  <https://github.com/joemccann/dillinger/tree/master/plugins/github/README.md>
   [PlGd]: <https://github.com/joemccann/dillinger/tree/master/plugins/googledrive/README.md>
   [PlOd]: <https://github.com/joemccann/dillinger/tree/master/plugins/onedrive/README.md>
