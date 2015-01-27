//
//  DiningAPI.swift
//  BrownMenu
//
//  Created by Nate Parrott on 1/26/15.
//  Copyright (c) 2015 Nate Parrott. All rights reserved.
//

import UIKit

private let _DiningAPIShared = DiningAPI()

class DiningAPI: NSObject {
    class var Shared: DiningAPI {
        return _DiningAPIShared
    }
    struct Menu: Printable {
        let eatery: Eatery
        let startTime: NSDate
        let endTime: NSDate
        let foods: [String]
        static func FormatTime(time: NSDate) -> String {
            let formatter = NSDateFormatter()
            formatter.timeStyle = NSDateFormatterStyle.ShortStyle
            return formatter.stringFromDate(time)
        }
        var description: String {
            let nFoods = countElements(foods)
            let start = Menu.FormatTime(startTime)
            let end = Menu.FormatTime(endTime)
            return "\(eatery) menu (\(start) - \(end): \(nFoods) foods"
        }
        
        static func FromDict(dict: [String: AnyObject], eatery: Eatery) -> Menu {
            let dateComps = NSCalendar.autoupdatingCurrentCalendar().components(.CalendarUnitDay | .CalendarUnitMonth | .CalendarUnitYear, fromDate: NSDate())
            
            // find start time:
            dateComps.hour = dict["start_hour"] as? Int ?? 0
            dateComps.minute = dict["start_minute"] as? Int ?? 0
            let startTime = NSCalendar.autoupdatingCurrentCalendar().dateFromComponents(dateComps)!
            
            // find end time:
            dateComps.hour = dict["end_hour"] as? Int ?? 0
            dateComps.minute = dict["end_minute"] as? Int ?? 0
            let endTime = NSCalendar.autoupdatingCurrentCalendar().dateFromComponents(dateComps)!
            
            let foods = dict["food"] as? [String] ?? [String]()
            
            let menu = Menu(eatery: eatery, startTime: startTime, endTime: endTime, foods: foods)
            
            return menu
        }
    }
    
    struct Eatery: Printable {
        let name: String
        let displayName: String
        var description: String {
            return name
        }
    }
    
    private func get(endpoint: String, params: [String: String]?, callback: (([String: AnyObject]?) -> ())) {
        let components = NSURLComponents(string: "http://brown-apis.herokuapp.com")!
        var allParams = params ?? [String: String]()
        allParams["client_id"] = "test_client"
        components.path = endpoint
        components.queryItems = Array(map(allParams.keys) { (let key) in
            return NSURLQueryItem(name: key, value: allParams[key]!)
        })
        let request = NSURLRequest(URL: components.URL!)
        NSURLSession.sharedSession().dataTaskWithRequest(request, completionHandler: { (let dataOpt: NSData?, let response: NSURLResponse?, let error: NSError?) -> Void in
            if let data = dataOpt {
                if let obj = NSJSONSerialization.JSONObjectWithData(data, options: NSJSONReadingOptions.allZeros, error: nil) as? [String: AnyObject] {
                    callback(obj)
                } else {
                    callback(nil)
                }
            } else {
                callback(nil);
            }
        }).resume()
    }
    
    func getEateries(callback: (([Eatery]?) -> ())) {
        let eateries = ["ratty": "Ratty", "vdub": "V-Dub", "jos": "Jo's", "ivy": "Ivy Room", "andrews": "Andrews Commons", "blueroom": "Blue Room"]
        callback(Array(map(eateries.keys, { Eatery(name: $0, displayName: eateries[$0]!) })))
    }
    
    func getMenu(eatery: Eatery, callback: (([Menu]?) -> ())) {
        let currentDay = NSCalendar.autoupdatingCurrentCalendar().component(.CalendarUnitDay, fromDate: NSDate())
        
        get("/dining/menu", params: ["eatery": eatery.name, "day": "\(currentDay)"]) { (let dictOpt) -> () in
            if let dict = dictOpt {
                if let menuDicts = dict["menus"] as? [[String: AnyObject]] {
                    let menus = menuDicts.map({ Menu.FromDict($0, eatery: eatery) })
                    callback(menus)
                } else {
                    callback(nil)
                }
            } else {
                callback(nil)
            }
        }
    }
    
    func getMenusForEateries(callback: ([(Eatery, [Menu])]?) -> ()) {
        getEateries { (let eateriesOpt) -> () in
            if let eateries = eateriesOpt {
                var eateriesAndMenus: [(Eatery, [Menu])] = []
                var numFinished = [0] // wrap in array so we can access it inside the block
                for eatery in eateries {
                    self.getMenu(eatery, callback: { (let menusOpt) -> () in
                        if let menus = menusOpt {
                            eateriesAndMenus.append(eatery, menus)
                        } else {
                            eateriesAndMenus.append(eatery, [])
                        }
                        numFinished[0] = numFinished[0] + 1
                        if numFinished[0] == countElements(eateries) {
                            if countElements(eateries) == countElements(eateriesAndMenus) {
                                callback(eateriesAndMenus)
                            } else {
                                callback(nil)
                            }
                        }
                    })
                }
            } else {
                callback(nil)
            }
        }
    }
}
