//
//  API.swift
//  RattyApp
//
//  Created by Nate Parrott on 2/16/15.
//  Copyright (c) 2015 Nate Parrott. All rights reserved.
//

import UIKit

extension NSDate {
    func getDateComponents() -> (day: Int, month: Int, year: Int) {
        let cal = NSCalendar.currentCalendar()
        let comps = cal.components(.MonthCalendarUnit | .DayCalendarUnit | .YearCalendarUnit, fromDate: self)
        return (day: comps.day, month: comps.month, year: comps.year)
    }
    func byAddingSeconds(seconds: NSTimeInterval) -> NSDate {
        return NSDate(timeIntervalSinceReferenceDate: timeIntervalSinceReferenceDate + seconds)
    }
    func abbreviatedWeekday() -> String {
        let fmt = NSDateFormatter()
        fmt.dateFormat = "EEE"
        return fmt.stringFromDate(self)
    }
    func dateByRemovingTime() -> NSDate {
        let comps = NSDateComponents()
        (comps.day, comps.month, comps.year) = getDateComponents()
        comps.hour = 0
        comps.minute = 0
        return NSCalendar.currentCalendar().dateFromComponents(comps)!
    }
    func daysAfterToday() -> Int {
        return Int((dateByRemovingTime().timeIntervalSinceReferenceDate - NSDate().dateByRemovingTime().timeIntervalSinceReferenceDate) / (24 * 60 * 60))
    }
}

private var _SharedAPI: DiningAPI?
func SharedDiningAPI() -> DiningAPI {
    // TODO: use dispatch_once
    if _SharedAPI == nil {
        _SharedAPI = DiningAPI()
    }
    return _SharedAPI!
}

func distanceOfDateFromDateRange(date: NSDate, rangeStart: NSDate, rangeEnd: NSDate) -> NSTimeInterval {
    if date.compare(rangeStart) == .OrderedAscending {
        return rangeStart.timeIntervalSinceReferenceDate - date.timeIntervalSinceReferenceDate
    } else if rangeEnd.compare(date) == .OrderedAscending {
        return date.timeIntervalSinceReferenceDate - rangeEnd.timeIntervalSinceReferenceDate
    } else {
        return 0
    }
}

class DiningAPI: NSObject {
    
    struct Time : Printable, Equatable {
        var hour, minute: Int
        func convertToDateOnDate(date: NSDate) -> NSDate {
            let comps = NSCalendar.currentCalendar().components(.CalendarUnitDay | .CalendarUnitMonth | .CalendarUnitYear, fromDate: date)
            comps.hour = hour
            comps.minute = minute
            return NSCalendar.currentCalendar().dateFromComponents(comps)!
        }
        var description: String {
            return NSString(format: "%d:%02d", hour, minute)
        }
    }
    
    struct MealMenu : Printable {
        var startTime, endTime: Time
        var sections: [MenuSection]
        init(json: [String: AnyObject]) {
            startTime = Time(hour: (json["start_hour"]! as Int), minute: (json["start_minute"]! as Int))
            endTime = Time(hour: (json["end_hour"]! as Int), minute: (json["end_minute"]! as Int))
            let sectionNames = ["bistro", "chef's corner", "daily sidebars", "grill", "roots & shoots"]
            sections = sectionNames.map({
                (name: String) -> MenuSection? in
                if let items = json[name] as? [String] {
                    return MenuSection(name: name, items: items)
                } else {
                    return nil
                }}).filter({ $0 != nil }).map({ $0! })
        }
        var description: String {
            return "Menu from \(startTime) — \(endTime): " + " ".join(sections.map({ $0.description }))
        }
    }
    
    struct MenuSection : Printable {
        var name: String
        var items: [String]
        var description: String {
            return name.uppercaseString + "\n" + "\n".join(items) + "\n"
        }
    }
    
    func get(endpoint: String, params: [String: String]?, allowCached: Bool, callback: (response: [String: AnyObject]?, error: NSError?) -> ()) {
        
        let comps = NSURLComponents()
        comps.scheme = "https"
        comps.host = "api.students.brown.edu"
        comps.path = endpoint
        var allParams = params ?? [String: String]()
        allParams["client_id"] = "hackathon"
        comps.queryItems = Array(map(allParams.keys, {
            (key: String) in
            return NSURLQueryItem(name: key, value: allParams[key]!)
        }))
        // println("call: \(comps.URL!)")
        let req = NSMutableURLRequest(URL: comps.URL!)
        if let cached = NSURLCache.sharedURLCache().cachedResponseForRequest(req) {
            if let response = NSJSONSerialization.JSONObjectWithData(cached.data, options: nil, error: nil) as? [String: AnyObject] {
                callback(response: response, error: nil)
            } else {
                callback(response: nil, error: nil)
            }
        } else {
            AppDelegate.Shared().incrementNetworkActivityCount()
            NSURLSession.sharedSession().dataTaskWithRequest(req, completionHandler: { (let dataOpt: NSData?, let response: NSURLResponse?, let errorOpt: NSError?) -> Void in
                dispatch_async(dispatch_get_main_queue(), { () -> Void in
                    AppDelegate.Shared().decrementNetworkActivityCount()
                    if let data = dataOpt {
                        if let responseDict = NSJSONSerialization.JSONObjectWithData(data, options: nil, error: nil) as? [String: AnyObject] {
                            NSURLCache.sharedURLCache().storeCachedResponse(NSCachedURLResponse(response: response!, data: data), forRequest: req)
                            
                            //let s = NSString(data: data, encoding: NSUTF8StringEncoding)
                            //println("RESP: \(s)")
                            callback(response: responseDict, error: nil)
                        } else {
                            callback(response: nil, error: nil)
                        }
                    } else {
                        callback(response: nil, error: errorOpt)
                    }
                })
            }).resume()
        }
    }
    
    func getMenu(eatery: String, date: NSDate, callback: ([MealMenu]?, NSError?) -> ()) {
        let (day, month, year) = date.getDateComponents()
        let params: [String: String] = [
            "eatery": "ratty",
            "month": "\(month)",
            "day": "\(day)",
            "year": "\(year)"
        ]
        get("/dining/menu", params: params, allowCached: true) { (responseOpt, errorOpt) -> () in
            if let response = responseOpt {
                if let menusJson = response["menus"] as? [[String: AnyObject]] {
                    let menus = menusJson.map({ MealMenu(json: $0) })
                    callback(menus, errorOpt)
                } else {
                    callback(nil, nil)
                }
            } else {
                callback(nil, errorOpt)
            }
        }
    }
    
    func indexOfNearestMeal(meals: [MealMenu]) -> Int? {
        let now = NSDate()
        if let meal = meals.sorted({ (let m1, let m2) -> Bool in
            let d1 = distanceOfDateFromDateRange(now, m1.startTime.convertToDateOnDate(now), m1.endTime.convertToDateOnDate(now))
            let d2 = distanceOfDateFromDateRange(now, m2.startTime.convertToDateOnDate(now), m2.endTime.convertToDateOnDate(now))
            return d1 < d2
        }).first {
            for i in 0..<countElements(meals) {
                if meals[i].startTime == meal.startTime {
                    return i
                }
            }
            return nil
        } else {
            return nil
        }
    }
}

func ==(lhs: DiningAPI.Time, rhs: DiningAPI.Time) -> Bool {
    return lhs.hour == rhs.hour && lhs.minute == rhs.minute
}

