//
//  MenuTableViewController.swift
//  RattyApp
//
//  Created by Nate Parrott on 2/16/15.
//  Copyright (c) 2015 Nate Parrott. All rights reserved.
//

import UIKit

let MenuSectionInset: CGFloat = 10

class MenuTableViewController: UIViewController, UITableViewDataSource, UITableViewDelegate {
    
    var tableView: UITableView!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        tableView = UITableView(frame: view.bounds, style: .Plain)
        view.addSubview(tableView)
        tableView.delegate = self
        tableView.dataSource = self
        
        tableView.registerClass(MenuItemCell.self, forCellReuseIdentifier: "MenuItemCell")
        tableView.backgroundColor = UIColor.clearColor()
        tableView.separatorStyle = .None
        tableView.contentInset = UIEdgeInsetsMake(20, 0, 50 + MenuSectionInset, 0)
        tableView.scrollIndicatorInsets = tableView.contentInset
        tableView.indicatorStyle = .White
        tableView.showsVerticalScrollIndicator = false
        
        updateHeader()
    }
    
    override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        tableView.frame = UIEdgeInsetsInsetRect(view.bounds, UIEdgeInsetsMake(0, MenuSectionInset, 0, MenuSectionInset))
    }
    
    func updateHeader() {
        let str = NSMutableAttributedString()
        
        let ordinaryFont = UIFont(name: "AvenirNext-Medium", size: 16)!
        let boldFont = UIFont(name: "Avenir-Black", size: 16)!
        let smallFont = UIFont(name: "AvenirNext-Medium", size: 12)!
        
        let daysFromToday = time.date.daysAfterToday()
        var relativeDateStringOpt: String?
        switch daysFromToday {
        case 0: relativeDateStringOpt = "Today"
        case 1: relativeDateStringOpt = "Tomorrow"
        case -1: relativeDateStringOpt = "Yesterday"
        default: relativeDateStringOpt = nil
        }
        
        if let relativeDateString = relativeDateStringOpt {
            let attributes: [NSObject: AnyObject] = [NSFontAttributeName as NSObject: boldFont as AnyObject]
            let a = NSAttributedString(string: relativeDateString + ", ", attributes: attributes)
            str.appendAttributedString(a)
        }
        
        let fmt = NSDateFormatter()
        fmt.dateFormat = "EEEE, M/d"
        let dateString = fmt.stringFromDate(time.date)
        let mealString = ["Breakfast", "Lunch", "Dinner"][time.meal]
        let timeText = "\(dateString) — \(mealString)"
        
        let timeAttributes: [NSObject: AnyObject] = [NSFontAttributeName as NSObject: ordinaryFont as AnyObject]
        str.appendAttributedString(NSAttributedString(string: timeText, attributes: timeAttributes))
        
        if daysFromToday != 0 {
            let backAttributes: [NSObject: AnyObject] = [NSFontAttributeName as NSObject: smallFont as AnyObject]
            str.appendAttributedString(NSAttributedString(string: "\nreturn to today", attributes: backAttributes))
        }
        let label = UILabel(frame: CGRectMake(0, 0, 100, 40))
        label.textAlignment = .Center
        label.textColor = UIColor.whiteColor()
        label.alpha = 0.6
        label.numberOfLines = 0
        label.attributedText = str
        label.addGestureRecognizer(UITapGestureRecognizer(target: self, action: "_returnToToday"))
        label.userInteractionEnabled = true
        
        tableView.tableHeaderView = label
    }
    
    var shouldReturnToToday: (() -> ())?
    func _returnToToday() {
        if let cb = shouldReturnToToday {
            cb()
        }
    }
    
    var time: (date: NSDate, meal: Int)! {
        didSet {
            if let (date, meal) = time {
                SharedDiningAPI().getMenu("ratty", date: date, callback: { (let menuOpts, let errorOpt) -> () in
                    if let menus = menuOpts {
                        if meal < countElements(menus) {
                            self.menu = menus[meal]
                        } else if meal == 2 && countElements(menus) == 2 {
                            // HACK: it's sunday, there's only 2 meals (breakfast + brunch),
                            // but since I'm too lazy to write a special UI for sunday, just show the Brunch
                            // meal as lunch AND dinner
                            self.menu = menus[1]
                        }
                    }
                })
            }
        }
    }
    
    var menu: DiningAPI.MealMenu? {
        didSet {
            if isViewLoaded() {
                tableView.reloadData()
            }
        }
    }

    // MARK: - Table view data source
    
    func numberOfSectionsInTableView(tableView: UITableView) -> Int {
        return countElements(menu?.sections ?? [])
    }
    
    func tableView(tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        let section = menu!.sections[section]
        return countElements(section.items) + 1
    }
    
    func tableView(tableView: UITableView, cellForRowAtIndexPath indexPath: NSIndexPath) -> UITableViewCell {
        let section = menu!.sections[indexPath.section]
        let cell = tableView.dequeueReusableCellWithIdentifier("MenuItemCell", forIndexPath: indexPath) as MenuItemCell
        cell.textLabel.textAlignment = indexPath.row == 0 ? .Center : .Left
        if indexPath.row == 0 {
            cell.textLabel.text = section.name.uppercaseString
        } else {
            cell.textLabel.text = section.items[indexPath.row - 1]
        }
        let alpha: CGFloat = (indexPath.row == 0) ? 0.5 : (indexPath.row % 2 == 0 ? 0.25 : 0.125)
        cell.backgroundColor = UIColor(white: 1, alpha: alpha)
        // cell.insets = UIEdgeInsetsMake(MenuSectionInset / 2, MenuSectionInset, MenuSectionInset / 2, MenuSectionInset)
        cell.selectionStyle = .None
        return cell
    }
    
    func tableView(tableView: UITableView, heightForFooterInSection section: Int) -> CGFloat {
        return MenuSectionInset
    }
    func tableView(tableView: UITableView, viewForFooterInSection section: Int) -> UIView? {
        return UIView()
    }
}
