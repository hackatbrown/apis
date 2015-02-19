//
//  MenuLoader.swift
//  RattyApp
//
//  Created by Nate Parrott on 2/18/15.
//  Copyright (c) 2015 Nate Parrott. All rights reserved.
//

import UIKit
import NotificationCenter

class MenuLoader: NSObject {
    private(set) var loading: Bool = false
    private(set) var erroredOnLastLoad: Bool = false
    private(set) var meals: [DiningAPI.MealMenu]?
    private(set) var mealsLoadedDate: NSDate?
    
    var onStateUpdated: (() -> ())?
    private func stateUpdated() {
        if let cb = onStateUpdated {
            cb()
        }
    }
    var onReload: (() -> ())?
    
    override init() {
        super.init()
        
        if let (meals, date) = getCachedMenu() {
            self.meals = meals
            self.mealsLoadedDate = date
        }
        
        reloadIfNeeded()
    }
    
    func isMenuStale() -> Bool {
        return mealsLoadedDate == nil || NSDate().dateByRemovingTime().compare(mealsLoadedDate!.dateByRemovingTime()) != .OrderedSame
    }
    
    var completionHandler: (NCUpdateResult -> ())?
    
    func reloadIfNeeded() {
        if isMenuStale() && !loading {
            loading = true
            erroredOnLastLoad = false
            self.stateUpdated()
            DiningAPI().getJsonForMenu("eatery", date: NSDate(), callback: { (let responseOpt, let errorOpt) -> () in
                self.erroredOnLastLoad = true
                if let resp = responseOpt {
                    self.cacheMenu(resp)
                    if let menusJson = resp["menus"] as? [[String: AnyObject]] {
                        let menus = menusJson.map({ DiningAPI.MealMenu(json: $0) })
                        self.meals = menus
                        self.mealsLoadedDate = NSDate()
                        self.erroredOnLastLoad = false
                    }
                }
                self.loading = false
                self.stateUpdated()
                if let cb = self.completionHandler {
                    self.completionHandler = nil
                    cb(self.erroredOnLastLoad ? .NewData : .Failed)
                }
                if let cb = self.onReload {
                    cb()
                }
            })
        } else {
            if let cb = self.completionHandler {
                self.completionHandler = nil
                cb(.NoData)
            }
        }
    }
    private func getCachedMenu() -> (meals: [DiningAPI.MealMenu], date: NSDate)? {
        if let data = NSData(contentsOfFile: cachePath) {
            if let r: AnyObject = NSJSONSerialization.JSONObjectWithData(data, options: nil, error: nil) {
                if let dict = r as? [String: AnyObject] {
                    if let menuJsons: AnyObject = dict["menus"] {
                        if let m = menuJsons as? [[String: AnyObject]] {
                            let meals = m.map({DiningAPI.MealMenu(json: $0)})
                            let time = NSUserDefaults.standardUserDefaults().doubleForKey("CachedMenuDate")
                            return (meals: meals, date: NSDate(timeIntervalSinceReferenceDate: time))
                        }
                    }
                }
            }
        }
        return nil
    }
    private func cacheMenu(jsonResponse: [String: AnyObject]) {
        let data = NSJSONSerialization.dataWithJSONObject(jsonResponse, options: nil, error: nil)!
        data.writeToFile(cachePath, atomically: true)
        NSUserDefaults.standardUserDefaults().setDouble(NSDate.timeIntervalSinceReferenceDate(), forKey: "CachedMenuDate")
    }
    private var cachePath: String {
        get {
            return (NSSearchPathForDirectoriesInDomains(.CachesDirectory, .UserDomainMask, true).first! as String).stringByAppendingPathComponent("MenuCache.json")
        }
    }
}
