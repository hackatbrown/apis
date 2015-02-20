//
//  MenuViewController.swift
//  RattyApp
//
//  Created by Nate Parrott on 2/16/15.
//  Copyright (c) 2015 Nate Parrott. All rights reserved.
//

import UIKit

enum Meal {
    case Index(i: Int)
    case Nearest
}

func arePositionsEqual(p1: (date: NSDate, meal: Meal), p2: (date: NSDate, meal: Meal)) -> Bool {
    let (date1: NSDate, meal1: Meal) = p1
    let (date2: NSDate, meal2: Meal) = p2
    var mealsEqual = false
    switch (meal1, meal2) {
    case (.Index(let i1), .Index(let i2)): mealsEqual = i1 == i2
    case (.Nearest, .Nearest): mealsEqual = true
    default: mealsEqual = false
    }
    return date1.compare(date2) == .OrderedSame && mealsEqual
}

class MenuViewController: UIViewController, UIPageViewControllerDataSource, UIPageViewControllerDelegate {
    
    lazy var pageViewController: UIPageViewController = {
        let pageVC = UIPageViewController(transitionStyle: .Scroll, navigationOrientation: .Horizontal, options: nil)
        pageVC.dataSource = self
        pageVC.delegate = self
        self.addChildViewController(pageVC)
        return pageVC
    }()
    var pageTransitionTracker: PageTransitionTracker!
    
    lazy var gradientLayer: CAGradientLayer = {
        let g = CAGradientLayer()
        return g
    }()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        let x = currentPosition
        self.currentPosition = x // trigger load
        
        NSNotificationCenter.defaultCenter().addObserver(self, selector: "jumpToCurrentMeal", name: ShouldJumpToCurrentMealNotification, object: nil)
        NSNotificationCenter.defaultCenter().addObserver(self, selector: "jumpToMeal:", name: JumpToMealAndDateNotification, object: nil)
        
        pageTransitionTracker = PageTransitionTracker(pageViewController: pageViewController)
        pageTransitionTracker.trackingCallback = {
            [weak self] in
            self!.updateCurrentPage()
        }
        
        // index 0 is the splash image view
        view.layer.insertSublayer(gradientLayer, atIndex: 1)
        view.insertSubview(pageViewController.view, atIndex: 2)
        
        navContainer.addSubview(navView)
        navView.onPrevDayClicked = {
            [unowned self] in
            self.jumpDays(-1)
        }
        navView.onNextDayClicked = {
            [unowned self] in
            self.jumpDays(1)
        }
        navView.onSelectedMealChanged = {
            [unowned self] in
            self.jumpToMeal(Int(self.navView.selectedMeal))
        }
        
        // update page view controller:
        let menuVC = MenuTableViewController()
        menuVC.time = (date: NSDate(), meal: 1)
        pageViewController.setViewControllers([menuVC], direction: .Forward, animated: false, completion: nil)
        
        updateCurrentPage()
        
        jumpToCurrentMeal()
        
        pageViewController.view.alpha = 0
        navView.userInteractionEnabled = false
        navView.alpha = 0.5
    }
    
    deinit {
        NSNotificationCenter.defaultCenter().removeObserver(self, name: ShouldJumpToCurrentMealNotification, object: nil)
    }
    
    var initialLoad: Bool = false {
        didSet {
            UIView.animateWithDuration(0.3, animations: { () -> Void in
                self.pageViewController.view.alpha = 1
                self.navView.alpha = 1
            })
            navView.userInteractionEnabled = true
        }
    }
    
    func jumpToCurrentMeal() {
        currentPosition = (date: NSDate(), meal: Meal.Nearest)
    }
    
    func jumpToMeal(notif: NSNotification) {
        currentPosition = (date: notif.userInfo!["date"]! as NSDate, meal: Meal.Index(i: notif.userInfo!["meal"]! as Int))
    }
    
    override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        pageViewController.view.frame = view.bounds
        navView.frame = navContainer.bounds
        
        gradientLayer.frame = view.bounds
    }
    
    func pageViewController(pageViewController: UIPageViewController, viewControllerBeforeViewController viewController: UIViewController) -> UIViewController? {
        if let (date, meal) = (viewController as MenuTableViewController).time {
            let prev = MenuTableViewController()
            if meal == 0 {
                prev.time = (date.byAddingSeconds(-24 * 60 * 60), 2)
            } else {
                prev.time = (date, meal-1)
            }
            return prev
        }
        return nil
    }
    
    func pageViewController(pageViewController: UIPageViewController, viewControllerAfterViewController viewController: UIViewController) -> UIViewController? {
        if let (date, meal) = (viewController as MenuTableViewController).time {
            let next = MenuTableViewController()
            if meal == 2 {
                next.time = (date.byAddingSeconds(24 * 60 * 60), 0)
            } else {
                next.time = (date, meal+1)
            }
            return next
        }
        return nil
    }
    
    func pageViewController(pageViewController: UIPageViewController, willTransitionToViewControllers pendingViewControllers: [AnyObject]) {
        updateCurrentPage()
        pageTransitionTracker.startTracking()
        
        if let tableVC = pendingViewControllers.first as MenuTableViewController? {
            tableVC.shouldReturnToToday = {
                [weak self] in
                self!.currentPosition = (date: NSDate(), meal: Meal.Nearest)
            }
        }
    }
    
    func pageViewController(pageViewController: UIPageViewController, didFinishAnimating finished: Bool, previousViewControllers: [AnyObject], transitionCompleted completed: Bool) {
        pageTransitionTracker.stopTracking()
        updateCurrentPage()
    }
    
    @IBOutlet var navContainer: UIView!
    
    // MARK: Navigation
    
    var currentPosition: (date: NSDate, meal: Meal) = (date: NSDate(), meal: Meal.Nearest) {
        didSet {
            switch currentPosition.meal {
            case .Nearest:
                // load the current date, then update this:
                let posAtStartOfLoad = currentPosition
                SharedDiningAPI().getMenu("ratty", date: NSDate()) { (let menusOpt, let errorOpt) -> () in
                    if arePositionsEqual(posAtStartOfLoad, self.currentPosition) {
                        if let mealMenus = menusOpt {
                            if let meal = SharedDiningAPI().indexOfNearestMeal(mealMenus) {
                                self.currentPosition = (date: NSDate(), meal: Meal.Index(i: meal))
                            }
                        }
                    }
                }
            case .Index(let mealIndex):
                let animate = initialLoad
                initialLoad = true
                if currentPosition.date != _showingDate() || mealIndex != _showingMealIndex() {
                    let isInFuture = _showingDate().compare(currentPosition.date) == .OrderedAscending || (_showingDate().compare(currentPosition.date) == .OrderedSame && _showingMealIndex() < mealIndex)
                    let pageVC = MenuTableViewController()
                    pageVC.time = (currentPosition.date, mealIndex)
                    pageViewController.setViewControllers([pageVC], direction: isInFuture ? .Forward : .Reverse, animated: animate, completion: nil)
                    if animate {
                        UIView.animateWithDuration(0.25, animations: { () -> Void in
                            self.updateCurrentPage(supressGradientAnimation: false)
                            }, completion: nil)
                    } else {
                        self.updateCurrentPage(supressGradientAnimation: true)
                    }
                }
            }
        }
    }
    
    func jumpDays(days: Int) {
        currentPosition = (date: currentPosition.date.byAddingSeconds(NSTimeInterval(days * 24 * 60 * 60)), meal: currentPosition.meal)
    }
    
    func jumpToMeal(meal: Int) {
        currentPosition = (date: currentPosition.date, meal: Meal.Index(i: meal))
    }
    
    private func _showingDate() -> NSDate {
        return (pageViewController.viewControllers.first? as MenuTableViewController).time?.date ?? NSDate()
    }
    
    private func _showingMealIndex() -> Int {
        return (pageViewController.viewControllers.first? as MenuTableViewController).time?.meal ?? 0
    }
    
    // MARK: Page transitions
    func updateCurrentPage(supressGradientAnimation: Bool = true) {
        switch currentPosition.meal {
        case .Index(i: _):
            currentPosition = (date: _showingDate(), meal: Meal.Index(i: _showingMealIndex()))
        case .Nearest: 1 + 1 // do nothing
        }
        
        var interpolatedMeal = CGFloat(_showingMealIndex())
        if pageTransitionTracker.isTracking {
            interpolatedMeal = CGFloat((pageTransitionTracker.trackingViewController! as MenuTableViewController).time.meal) + pageTransitionTracker.progress
        }
        navView.selectedMeal = interpolatedMeal
        
        gradientLayer.actions = supressGradientAnimation ? ["colors" as NSString: NSNull()] : nil
        
        let (color1, color2) = gradientForMeal(interpolatedMeal)
        gradientLayer.colors = [color1.CGColor, color2.CGColor]
        navView.backgroundColor = colorForMeal(interpolatedMeal)
    }
    
    func gradientForMeal(var meal: CGFloat) -> (UIColor, UIColor) {
        if !initialLoad {
            return (UIColor(white: 0, alpha: 0), UIColor(white: 0, alpha: 0))
        }
        let colorPairs = [
            (UIColor(red: 0.078, green: 0.392, blue: 0.584, alpha: 1), UIColor(red: 0.988, green: 0.698, blue: 0.000, alpha: 1)),
            (UIColor(red: 1.0, green:0.565297424793, blue:0.550667464733, alpha:1.0), UIColor(red: 1.0, green:0.745570778847, blue:0.0, alpha:1.0)),
            (UIColor(red: 0.88181167841, green:0.601593911648, blue:0.0619730427861, alpha:1.0), UIColor(red: 0.859640955925, green:0.223587602377, blue:0.290304690599, alpha:1.0))
        ]
        //             (UIColor(red: 0.463, green: 0.624, blue: 0.973, alpha: 1), UIColor(red: 0.674502670765, green:0.312217831612, blue:0.678681373596, alpha:1.0))
        if meal < 0 {
            meal += 3
        }
        let i1 = Int(floor(meal)) % 3
        let i2 = Int(ceil(meal)) % 3
        let mix = meal - floor(meal)
        let pair1 = colorPairs[i1]
        let pair2 = colorPairs[i2]
        return (pair1.0.mix(pair2.0, amount: mix), pair1.1.mix(pair2.1, amount: mix))
    }
    
    func colorForMeal(meal: CGFloat, dark: Bool = false) -> UIColor {
        let (c1, c2) = gradientForMeal(meal)
        return c1.mix(c2, amount: 0.5)
    }
    
    // MARK: View controller methods
    override func preferredStatusBarStyle() -> UIStatusBarStyle {
        return .LightContent
    }
    
    // MARK: Views
    lazy var navView: NavigationView = {
        let nav = UINib(nibName: "Navigation", bundle: nil).instantiateWithOwner(nil, options: nil)[0] as NavigationView
        return nav
        }()
}
