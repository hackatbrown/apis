# The Academic API
*Everything you need to know about the courses endpoint*
-- Harrison Pincket (hpincket) 2016-01-31

1. Usage Notes
2. Implementation Notes

The academic API will provide access to Brown University course data as seen on
selfservice.banner.edu, as well as Critical Review data (provided to us by Guo).

The Banner portion of the API is nearly complete and has the following
endpoints.

##Endpoints

Prefix everything with /academic. /courses/CSCI-1380 becomes
/academic/courses/CSCI1380.

| Method | Endpoint | Usage | Returns | 
|---|---|---|---|
|GET|/courses|Get courses|paging object of courses|
|GET|/courses/{Course Number}|Get all sections for this course number|paging object of courses|
|GET|/courses/{Section Number}|Get a specific section| course object|
|GET|/instructors|Get a list of instructors|Returns instructor full names each on a separate line|
|GET|/instructors/{Instructor Name}|Get all course objects taught by this professor|Returns a paging object of courses|
|GET|/departments|Get a list of departments | Returns a list of dept codes and descriptions|
|GET|/departments/{Department Code}| Gets all course objects in the given dept| A paging object of courses|
|GET|/during|Given a day and time in 'seconds since midnight', returns all courses in session then| Returns a paging object of courses|
|GET|/non-conflicting|Get courses which don't conflict with the given course list|Returns a paging object of courses|

**Endpoint: /course**

Defaults to an iterator of all courses.

Optional parameter: `numbers`: comma separated list of course and/or section
numbers. This serves as a way to request a given set of coures (instead of each
one individually).

TODO: Do we want to rename `numbers`?

ex: /courses?numbers=CSCI1380-S01,CSCI1670-S01,CSCI0160

Notice how both sections and courses are allowed. If the course number lacks a
dash then all sections/labs/conferences are included in the results.

Optional Parameter: `semester`, defaults to the current semester

**Endpoint: /courses/{Course Number}**

If Course Number is 'CSCI1380' then all sections/labs/conferences/etc. for
CSCI1380 are returned in a list.

```/courses/CSCI1380```

If Course Number contains a dash as in 'CSCI1380-S01' then only that particular
section is returned.

```/courses/CSCI1380-S01```

Optional Parameter: `semester`, defaults to the current semester

**Endpoint: /instructors**

Newline separated. As of now this returns all instructors found in all courses
of the database, regardless of semester.

Note: `semester` has no effect on this endpoint.

**Endpoint: /instructors/{Instructor Name}**

This might confuse some: the instructor name as presented in the above endpoint.
This will contain spaces, so the field must be encoded using something like
urllib2. "Broseph Carberry" --> Broseph%20Carberry"

Should default to current semester

Optional Parameter: `semester`, defaults to the current semester

**Endpoint: /departments**

Pretty straightforward. I include the description in the results because the
department codes aren't immediately obvious and this will let app builders make
nice menus.

Note: `semester` has no effect on this endpoint.

**Endpoint: /departments/{Department Code}**

ex:
/departments/CSCI

Optional Parameter: `semester`, defaults to the current semester

**Endpoint: /during**

params:
day: a single character representing the day {MTWRFSU}
time: time in seconds since midnight

Optional Parameter: `semester`, defaults to the current semester

I really tried to use DateTimeField, but it's just not built for 'time of day'.
Number of seconds is pretty usable, but let me know if you have a better way.

**Endpoint: /non-conflicting**

Users make a request with a list of sections and retrieve a list of courses with
any courses which conflict excluded:

/non-conflicting?numbers=CSCI1380-S01,CSCI1760-S01,APMA1650-S02

Optional Parameter: `semester`, defaults to the current semester

Note: I think CSCI1380 (instead of CSCI1380-S01) should return an error since
we're not sure if we should exclude S01 or S02. Some classes have ~14 sections.

**Paging, wut dis**

We're going to have a lot of information and we don't want to transfer it all
across at once (otherwise we could just provide a db dump). So here's what it
looks like:

|Value|Contents|
| ---- | -----|
| href | The url which the user requested |
| items | a list of certain number of course objects |
| limit | the max number of results included in items|
| offset | this is actually the mongoid last returned (more on this later). As a user you won't mess with this|
| next | A pre-built url which will return the next page using the same limit|

Max limit value: 42. limit = 9001 becomes limit = 42.

Min limit value: 1. limit = -1 becomes limit 1.

When no more results are available the next field is "null"

Update: The results are now sorted by the \_id field.

TODO: We can add a `previous` field to contains the previous url, but this
requires an extra call to the database to determine the offset. I don't think a
previous field is necessary, but it is possible.

**Specifying Semester**

The default is to only return course object offered in the 'current_semester'.
Endpoints which return courses provide the option of filtering the results.
Semesters are currently in the form "Season YYYY". i.e. "Spring 2016",
"Summer 2016", "Fall 2017".  Setting `semester` to 'all' does exactly what you
think.


##Implementation

The academic API currently makes use of the following files:
* /api/scripts/selfservice_scraper.py
* /api/scripts/coursemodels.py
* /api/courses.py

**Paging**

Paging is usually implemented with an offset and limit. The limit defines how
many items to include. At first I implemented offset as 'number of items from
the start', but this becomes slower as offset increases. You would think this
could be handled by a db, but [here's](https://docs.mongodb.org/manual/reference/method/cursor.skip/)
evidence to the contrary. 

So we instead offset by id value. (If we sort the results, then we should offset
by that value). This makes for ugly urls, but provides a better runtime. The
user won't ever have to build one of these urls because we provide a next field,
and it doesn't make sense to request a particular offset. We answer the
question, "What are the next 10 courses?" instead of "What are courses 30-39?"
You see? They really just want some or all of them.

Paging is implemented in /api/courses.py in paginate(). Briefly,
* `query_args` is by default a mongoengine query dictionary. This can be unpacked
  into the mongoengine default objects query set. As a countermeasure to
  spahgetti code we convert this to a raw query.
* `params`, a dictionary of parameters to include in the `next` url of the
  result. For example, require the same day and time in the next page. The limit
  and offset parameters are handled by the paginate() function.
* If `raw` is True, then `query_args` is already in a raw state and we don't
  need to convert it.
 
There's a little mess with the '$gt' field, this is to make sure we don't
overwrite any '\_id' specification essential to the query.


**Implementation of non-conflicting**

This method has two modes.

1. The fast mode uses a precomputed list of non-conflicting courses. Given a
   course we can get a list of courses which don't collide with it. This is
   stored in the nonconflict_entry collection in mongo. These are written by the
   selfservice scraper. The answer for the list of given courses is simply the
   set intersection of all the courses.
2. The slower mode doesn't rely on precomputation, but instead finds a set of
   courses which conflict with each course, performs a set union, and finally
   takes the difference from the universe (of courses). This is notably slower.

When the api is just starting up it won't have the necessary nonconflict_entries
to perform the first method. While this happens the api will default to the
second option. This will almost never happen, but this way we don't have to
worry about it. The only other time this matters if when a new course is added
mid-semester. Once the new course is added to the database, this endpoint will
revert to the old method until conflicts are recalculated.

###The Scraper

This is where 90% of the work is done. It's pretty nasty. 

From a computer with a running Mongo instance and appropriate MONGO_URI variable, run:
```
(venv)$ python3 -m api.scripts.selfservice_scraper.py --user-and-pass <Username> <Password>
```

Running multiple times will update the existing courses. Courses are uniquely
defined by full\_number and semester fields. 


**High Level Overview**: The scraper does a number of things:

1. Access Banner using a given username and password
2. Iterate through the next two or three semesters
3. Iterate through all departments
4. Visit each course on each page of results for the given department and
   semester
5. Extract information from the page and place it into a BannerCourse object
6. Perform some last minute field filling from given informaiton
7. Save it to the database.

This is all done with beautifulsoup4 and requests. The requests Session object
handles credentials and cookies. bs4 handles parsing. Beware, Banner is a mess.
I've done my best to ensure this code doesn't break, but be warned. 

To make the whole process faster we use python threads and a work Queue. The
main thread adds each course to the work queue and the worker threads request
course pages and extract content. (If you're wondering about the Global
Interpreter Lock, it doesn't bottleneck us in this case because our work is IO
bound. Otherwise ignore this parenthetical.) 

Finally, in an utterly expected bit of garbage we have a quadruply nested for
loop to determine course conflicts. Each course receives it's own entry in a
separate document whose sole purpose is to store this information.

**Some Bits of Code in More Detail**

**File Lock**
At the bottom of the file we use fcntl.lockf() to establish a lock on an
arbitrary file called 'selfservice_scraper.pid'. We do this to ensure that only
one version of the scraper is run at a time. Concurrent instances may lead to
duplicate courses in the database due to the scripts ability to add or update
existing documents.

**CourseExtractionWorker**
From the days of yore I included an option to download the data to files or add
to mongo. Some information is passed into the worker, but most is extracted with
the _extract_course() function which returns a BannerCourse object.

###Course Models
Two Documents:
BannerCourse - what is given to the user
NonconflictEntry - used to track conflicting courses (stores precomputation)

The rest are embedded documents in BannerCourse
