//
//  TodayViewController.swift
//  Ratty Menu
//
//  Created by Nate Parrott on 2/18/15.
//  Copyright (c) 2015 Nate Parrott. All rights reserved.
//

import UIKit
import NotificationCenter

func IncrementNetworkActivityCount() {
    
}

func DecrementNetworkActivityCount() {
    
}

let WidgetLeftMargin: CGFloat = 25

class TodayViewController: UIViewController, NCWidgetProviding {

    var loader = MenuLoader()
    
    var stack: StackView!
    var mealPicker: MealPicker!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        stack = StackView()
        view.addSubview(stack)
        
        mealPicker = MealPicker()
        mealPicker.onSelectedMealChanged = {
            [weak self] in
            var meal = self!.mealPicker.selectedMeal
            if countElements(self!.loader.meals!) == 2 && meal == 2 {
                meal = 1
            }
            self!.dateOfSelectedMeal = NSDate()
            self!.selectedMeal = meal
        }
        
        loader.onStateUpdated = {
            [weak self] in
            self!.updateUI()
        }
        loader.onReload = {
            [weak self] in
            if let meals = self!.loader.meals {
                self!.selectedMeal = DiningAPI().indexOfNearestMeal(meals)!
            }
        }
        loader.onReload!()
        
        stack.addGestureRecognizer(UITapGestureRecognizer(target: self, action: "openApp"))
        
        updateUI()
        
    }
    
    var dateOfSelectedMeal: NSDate?
    var selectedMeal: Int = 0 {
        didSet {
            mealPicker.selectedMeal = selectedMeal
            updateUI()
        }
    }
    
    func updateUI() {
        if loader.loading || loader.erroredOnLastLoad {
            let label = UILabel()
            label.textColor = UIColor.whiteColor()
            label.text = loader.loading ? "Loading..." : "Couldn't load menu"
            stack.views = [label]
        } else if let menus = loader.meals {
            let menuView = MenuView()
            menuView.menu = menus[selectedMeal]
            stack.views = [menuView, mealPicker]
        } else {
            stack.views = [] // this really shouldn't be reached...
        }
        preferredContentSize = stack.sizeThatFits(CGSizeMake(view.bounds.size.width - WidgetLeftMargin, 300))
    }
    
    override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        stack.frame = CGRectMake(WidgetLeftMargin, 0, view.bounds.size.width - WidgetLeftMargin, view.bounds.size.height)
    }
    
    func widgetMarginInsetsForProposedMarginInsets(defaultMarginInsets: UIEdgeInsets) -> UIEdgeInsets {
        return UIEdgeInsetsMake(defaultMarginInsets.top + 8, defaultMarginInsets.left - WidgetLeftMargin, defaultMarginInsets.bottom - 16, defaultMarginInsets.right + 6)
    }
    
    func widgetPerformUpdateWithCompletionHandler(completionHandler: ((NCUpdateResult) -> Void)?) {
        loader.completionHandler = completionHandler
        loader.reloadIfNeeded()
    }
    
    func openApp() {
        var url = "ratty://menu"
        if let date = loader.mealsLoadedDate {
            let meal = selectedMeal
            let date = date.timeIntervalSince1970
            url = "ratty://menu?date=\(date)&meal=\(meal)"
        }
        extensionContext!.openURL(NSURL(string: url)!, completionHandler: nil)
    }
}
