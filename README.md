Brown University APIs
=====================

*Brought to you by the Brown APIs Team (Joe Engelman, Justin Brower, Anson Rosenthal)*

These APIs are currently a work-in-progress.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

BASE_PATH = "https://api.brown.edu"

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

**Note about errors:** When requests fail for any reason, an error will be returned in the form:  

    {'error': "Some (hopefully) informative error message."}

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

## Brown Shuttle

### Request Shuttle IDs
**Suffix**: "*/shuttle/id*"  
**Format**: None  
**Returns**: a list of shuttle IDs in the form {'ids':[id1, id2, id3, ...]}  
	*NOTE*: if there are no shuttles running, an empty list will be returned

### Request Shuttle Stops 
**Suffix**: "*/shuttle/stops*"  
**Format**: {'time':EVENING/DAYTIME/CURRENT}  
	where EVENING = 'evening', DAYTIME = 'daytime', CURRENT = 'current'  
**Returns**: a list of shuttle stops (name, coord) for given time of day in
	the form {'stops': [(stop1_name, stop1_loc), (stop2_name, stop2_loc), ...]}  
	*NOTE*: if there are no shuttles running, an empty list will be returned

### Request Shuttle Info 
**Suffix**: "*/shuttle/id/<SHUTTLE_ID>*" where SHUTTLE_ID is an ID of a shuttle  
**Format**: None  
**Returns**: a JSON dictionary full of shuttle information with the following data:  
	'id':				-> id of shuttle  
	'loc':				-> location of shuttle  
	'next_stop':		-> next stop for this shuttle  
	'eta_hour':			-> estimated hour of arrival for next stop  
	'eta_minute':		-> estimated minute of arrival for next stop  
	'occupancy':		-> current occupancy of shuttle  
	'speed':			-> speed of this shuttle  
	*NOTE*: if the shuttle is not currently operating, then a response of the form
		{'id':SHUTTLE_ID, 'loc':0} will be returned

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

## Brown Dining Services 

Dining constants: 	  

	RATTY = 'ratty'
	VDUB  = 'vdub'
	ACO	  = 'andrews'
	IVY	  = 'ivy'
	JOS   = 'jos'
	BLUE  = 'blueroom'

### Request Dining Menu
**Suffix**: "*/dining/menu*"  
**Format**: {'eatery':RATTY/VDUB/..., 'year':YEAR, 'month':MONTH, 'day':DAY, 'hour':HOUR, 'minute':MINUTE}  
**Returns**: a dictionary of section titles mapped to items in the form  
	{'eatery':RATTY/VDUB/..., 'year':YEAR, 'month':MONTH, 'day':DAY, 'start_hour':START_HOUR, 'start_minute':START_MINUTE, 'end_hour':END_HOUR, 'end_minute':END_MINUTE, 'food':[item1, item2, ...]} where each food item is a string  
	*NOTE*: if the eatery is closed, an error message is returned

### Request Dining Hours 
**Suffix**: "*/dining/hours*"  
**Format**: {'eatery':RATTY/VDUB/..., 'year':YEAR, 'month':MONTH, 'day':DAY}  
**Returns**: {'eatery':RATTY/VDUB/..., 'year':YEAR, 'month':MONTH, 'day':DAY, 'open_hour':OPEN_HOUR, 'open_minute':OPEN_MINUTE, 'close_hour':CLOSE_HOUR, 'close_minute':CLOSE_MINUTE}  

### Find Eatery Serving Specific Food 
**Suffix**: "*/dining/find*"  
**Format**: {'food':NAME_OF_FOOD}  
**Returns**: where NAME_OF_FOOD is served and when it's served in the form  
	{'food':NAME_OF_FOOD, 'results':[meal_info1, meal_info2, ...]} where meal_info is similar to the response for dining/menu, except without the 'food' field
	*NOTE*: NAME_OF_FOOD may be autocorrected to another string if it does not match any foods in the database

### Find Nutritional Info 
**Suffix**: "*/dining/nutrition*"  
**Format**: {'food':NAME_OF_FOOD}  
**Returns**: the nutritional information for NAME_OF_FOOD with the following data,  
	'food':NAME_OF_FOOD  
	'ingredients':[ingredient1, ingredient2, ...] 
	and these (self-explanatory) fields: 'portion_size', 'calories', 'fat', 'saturated_fat',
		'cholesterol', 'sodium', 'carbohydrates', 'fiber', 'protein'  
	*NOTE*: portion size is a string, calories is an integer representing calories,
		and all other measurements are in milligrams represented as floats  

### Find Open Eateries 
**Suffix**: "*/dining/open*"  
**Format**: {'year':YEAR, 'month':MONTH, 'day':DAY, 'hour':HOUR, 'minute':MINUTE}  
	*NOTE*: the current time will be used as a default  
**Returns**: a list of information for open eateries at requested time in the form
	{'open_eateries':[eatery_hours1, eatery_hours2, ...]} and where each eatery_hours is of the same form as the response to a dining/hours request

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

## Brown Get Portal (Student Accounts) 

### Login 
**Suffix**: "*/student/login*"  
**Format**: {'username':USERNAME, 'password':PASSWORD} where PASSWORD is encrypted  
**Returns**: a boolean to signify success and a token for future requests in the form
	{'logged':TRUE/FALSE, 'token':TOKEN}  

### Get Account Balances 
**Suffix**: "*/student/balance*"  
**Format**: {'token':TOKEN}  
**Returns**: a mapping of fields to balances with the following fields: 'club_plan',
	'meal_credits', 'flex_points', 'bear_bucks', 'paw_prints', 'guest_meals'  

### Get Transaction History 
**Suffix**: "*/student/transactions*"  
**Format**: {'token':TOKEN, 'start':{dictionary of start datetime, 'end':{dictionary of end datetime}} where start/end signify the span of time to get transaction data from  
**Returns**: a list of transactions {'transactions':[trans1, trans2, ...]} where each
	transaction is a mapping with the keys 'field', 'datetime', 'details', 'amt'
	corresponding to the columns on the get portal website  

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
