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
        
        updateHeader()
    }
    
    func updateHeader() {
        let label = UILabel(frame: CGRectMake(0, 0, 100, 40))
        label.textAlignment = .Center
        label.font = UIFont(name: "AvenirNext-Medium", size: 16)
        label.textColor = UIColor.whiteColor()
        label.alpha = 0.6
        
        let fmt = NSDateFormatter()
        fmt.dateFormat = "EEEE, M/d"
        let dateString = fmt.stringFromDate(time.date)
        let mealString = ["Breakfast", "Lunch", "Dinner"][time.meal]
        label.text = "\(dateString) — \(mealString)"
        
        tableView.tableHeaderView = label
    }
    
    var time: (date: NSDate, meal: Int)! {
        didSet {
            if let (date, meal) = time {
                SharedDiningAPI().getMenu("ratty", date: date, callback: { (let menuOpts, let errorOpt) -> () in
                    if let menus = menuOpts {
                        if meal < countElements(menus) {
                            self.menu = menus[meal]
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
