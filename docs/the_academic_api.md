# The Academic API
*Everything you need to know about the courses endpoint*
-- Harrison Pincket (hpincket) 2016-01-31

1. Usage Notes
2. Implementation Notes

Note: If I refer to the academic API as the courses API it is because I'm not
sure which name we will use. Sorry for any confusion.

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


**Endpoint: /courses/{Course Number}**

If Course Number is 'CSCI1380' then all sections/labs/conferences/etc. for
CSCI1380 are returned in a list.

If Course Number contains a dash as in 'CSCI1380-S01' then only that particular
section is returned.

**Endpoint: /instructors**

Newline separated. As of now this returns all instructors found in all courses
of the database, regardless of semester.

**Endpoint: /instructors/{Instructor Name}**

This might confuse some: the instructor name as presented in the above endpoint.
This will contain spaces, so the field must be encoded using something like
urllib2. "Broseph Carberry" --> Broseph%20Carberry"

Should default to current semester

**Endpoint: /departments**

Pretty straightforward. I include the description in the results because the
department codes aren't immediately obvious and this will let app builders make
nice menus.

**Endpoint: /departments/{Department Code}**

ex:
/departments/CSCI

**Endpoint: /during**

params:
day: a single character representing the day {MTWRFSU}
time: time in seconds since midnight

I thought this might be handy. 

I really tried to use DateTimeField, but it's just not built for 'time of day'.
Number of seconds is pretty usable, but let me know if you have a better way.

**Endpoint: /non-conflicting**

I think this endpoint is pretty neat. Users make a request with a list of
sections and retrieve a list of courses with any courses which conflict
excluded:

/non-conflicting?numbers=CSCI1380-S01,CSCI1760-S01,APMA1650-S02

Note: I think CSCI1380 (instead of CSCI1380-S01) should return an error since
we're not sure if we should exclude S01 or S02. Some classes have ~14 sections.

**Paging, wut's dis**

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

Max limit value: 42
Min limit value: 1

An invalid limit is changed to the nearest valid one.

When no more results are available the next field is "null"

Right now I don't specify a sort order of results. I think we should in case the
sort order changes between pages. I haven't checked for uniqueness in page
entries, but currently we don't have that guarantee.


**Specifying Semester**

The default is to only return course object offered in the 'current_semester'.
Right now users can specify another semester in some of the endpoints, but I
haven't added this to all of them. Semesters are currently in the form we used
for the scraper i.e. "Spring 2016", "Summer 2016", "Fall 2017". We also should
add an 'all' option in case users want access regardless of semester. This
can probably be done in the /api/courses.py: filter_semester(). I'll admit I
haven't yet fleshed out how filter_semester() and paginate() interact.



##Implementation

The academic API currently makes use of the following files:
* /api/scripts/selfservice_scraper.py
* /api/scripts/course_models.py
* /api/courses.py

**Paging**

Paging is usually implemented with an offset and limit. The limit defines how
many items to include. At first I implemented offset as 'number of items from
the start', but this becomes slower as offset increases. You would think this
could be handled by a db, but [here's](https://docs.mongodb.org/manual/reference/method/cursor.skip/)
evidence to the contrary. 

So we instead offset by id value. (If we sort the results, then we should offset
by that value). This makes for ugly urls, but provides a better runtime. The
user won't ever have to build one of these urls because it doesn't make sense to
request the 25th-50th courses. You see? They really just want some or all of
them.

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
Oh god, I thought I had fixed this part, one sec.
