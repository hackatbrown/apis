
Prefix everything with /academic. /courses/CSCI-1380 becomes
/academic/courses/CSCI1380.

**Endpoint: /courses**

Defaults to an iterator of all courses

Optional parameter: `numbers`: comma separated list of course and/or section
numbers. This serves as a way to request a given set of coures (instead of each
one individually).

ex: `/courses?numbers=CSCI1380-S01,CSCI1670-S01,CSCI0160`

Notice how both sections and courses are allowed. If the course number lacks a dash then all sections/labs/conferences are included in the results.

Optional Parameter: `semester`, defaults to the current semester

**Endpoint: /courses/{Course Number}**

Returns information about a specific course

If Course Number is 'CSCI1380' then all sections/labs/conferences/etc. for
CSCI1380 are returned in a list.

```
/courses/CSCI1380
```

If Course Number contains a dash as in 'CSCI1380-S01' then only that particular
section is returned.

```
/courses/CSCI1380-S01
```

Optional Parameter: `semester`, defaults to the current semester

**Endpoint: /instructors**

Returns a list of all instructors found in all courses of the database, regardless of semester.

Note: `semester` has no effect on this endpoint.

**Endpoint: /instructors/{Instructor Name}**

Returns all the courses taught be an instructor

This will contain spaces, so the field must be encoded using something like
urllib2. "Josiah Q. Carberry" --> Josiah%20Q%2E%20Carberry"

Optional Parameter: `semester`, defaults to the current semester

**Endpoint: /departments**

Returns all departments with their name and code

Note: `semester` has no effect on this endpoint.

**Endpoint: /departments/{Department Code}**

ex: `/departments/CSCI`

Optional Parameter: `semester`, defaults to the current semester

**Endpoint: /during**

Parameters:

*   day: a single character representing the day {MTWRFSU}
*   time: time in seconds since midnight

Optional Parameter: `semester`, defaults to the current semester

**Endpoint: /non-conflicting**

Make a request with a list of sections and retrieve a list of courses with any conflicting courses excluded:

/non-conflicting?numbers=CSCI1380-S01,CSCI1760-S01,APMA1650-S02

Optional Parameter: `semester`, defaults to the current semester

Note: CSCI1380 (instead of CSCI1380-S01) should return an error since we're not sure if we should exclude S01 or S02. Some classes have ~14 sections. In other words, you must include the specific section, even if there is only one section of the course.

##Paging

To make requests more efficient, this API uses a paging system to return small chunks of results at a time. Any endpoints with paged responses will contain the following:

*   href: The url which the user requested
*   items: a list of certain number of course objects
*   limit: the max number of results included in items
*   offset: the page offset (identifies a specific page)
*   next: a pre-built url which will return the next page using the same limit

Max limit value: 42. (i.e. limit = 9001 becomes limit = 42)

Min limit value: 1 (i.e. limit = -1 becomes limit 1)

When no more results are available the next field is "null"

##Specifying a Semester

The default is to only return course object offered in the 'current_semester' (otherwise, future calls might return duplicate course results from previous years).
Endpoints which return courses provide the option of filtering the results.
Semesters are currently in the form "Season YYYY". i.e. "Spring 2016", "Summer 2016", "Fall 2015".  Setting `semester` to 'all' does exactly what you think. Capitalization is important.
