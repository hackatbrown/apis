//
//  MenuTableViewController.swift
//  RattyApp
//
//  Created by Nate Parrott on 2/16/15.
//  Copyright (c) 2015 Nate Parrott. All rights reserved.
//

import UIKit

let MenuSectionInset: CGFloat = 10

class MenuTableViewController: UITableViewController {
    
    override func viewDidLoad() {
        super.viewDidLoad()
        tableView.registerClass(SectionCell.self, forCellReuseIdentifier: "SectionCell")
        tableView.backgroundColor = UIColor.clearColor()
        tableView.separatorStyle = .None
        tableView.contentInset = UIEdgeInsetsMake(20, 0, 50 + MenuSectionInset, 0)
        tableView.scrollIndicatorInsets = tableView.contentInset
        tableView.indicatorStyle = .White
        tableView.showsVerticalScrollIndicator = false
        
        updateHeader()
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
    
    override func tableView(tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        // #warning Incomplete method implementation.
        // Return the number of rows in the section.
        return countElements(menu?.sections ?? [])
    }
    
    override func tableView(tableView: UITableView, heightForRowAtIndexPath indexPath: NSIndexPath) -> CGFloat {
        let size = CGSizeMake(tableView.bounds.size.width - MenuSectionInset * 2, CGFloat(MAXFLOAT))
        return SectionCell.createStackViewForSection(menu!.sections[indexPath.row]).sizeThatFits(size).height + MenuSectionInset
    }
    
    override func tableView(tableView: UITableView, cellForRowAtIndexPath indexPath: NSIndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCellWithIdentifier("SectionCell")! as SectionCell
        cell.backgroundColor = UIColor.clearColor()
        cell.insets = UIEdgeInsetsMake(MenuSectionInset / 2, MenuSectionInset, MenuSectionInset / 2, MenuSectionInset)
        cell.section = menu!.sections[indexPath.row]
        cell.selectionStyle = .None
        return cell
    }
}
