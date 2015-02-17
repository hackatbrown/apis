//
//  MenuViewController.swift
//  RattyApp
//
//  Created by Nate Parrott on 2/16/15.
//  Copyright (c) 2015 Nate Parrott. All rights reserved.
//

import UIKit

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
        
        NSNotificationCenter.defaultCenter().addObserver(self, selector: "jumpToCurrentMeal", name: ShouldJumpToCurrentMealNotification, object: nil)
        
        pageTransitionTracker = PageTransitionTracker(pageViewController: pageViewController)
        pageTransitionTracker.trackingCallback = {
            [weak self] in
            self!.updateCurrentPage()
        }
        
        view.insertSubview(pageViewController.view, atIndex: 0)
        view.layer.insertSublayer(gradientLayer, atIndex: 0)
        
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
        
        view.alpha = 0
        jumpToCurrentMeal()
    }
    
    deinit {
        NSNotificationCenter.defaultCenter().removeObserver(self, name: ShouldJumpToCurrentMealNotification, object: nil)
    }
    
    var jumpedToTodayYet: Bool = false {
        didSet {
            UIView.animateWithDuration(0.3, animations: { () -> Void in
                self.view.alpha = 1
            })
        }
    }
    func jumpToCurrentMeal() {
        SharedDiningAPI().getMenu("ratty", date: NSDate()) { (let menusOpt, let errorOpt) -> () in
            let initialAppearance = !self.jumpedToTodayYet
            self.jumpedToTodayYet = true
            if let mealMenus = menusOpt {
                if let meal = SharedDiningAPI().indexOfNearestMeal(mealMenus) {
                    self.showDateAndMeal(NSDate(), meal: meal, animated: !initialAppearance)
                }
            }
        }
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
    }
    
    func pageViewController(pageViewController: UIPageViewController, didFinishAnimating finished: Bool, previousViewControllers: [AnyObject], transitionCompleted completed: Bool) {
        pageTransitionTracker.stopTracking()
        updateCurrentPage()
    }
    
    @IBOutlet var navContainer: UIView!
    
    // MARK: Navigation
    func jumpDays(days: Int) {
        showDateAndMeal(getShownDate().byAddingSeconds(NSTimeInterval(days * 24 * 60 * 60)), meal: getShownMeal())
    }
    
    func jumpToMeal(meal: Int) {
        showDateAndMeal(getShownDate(), meal: meal)
    }
    
    func showDateAndMeal(date: NSDate, meal: Int, animated: Bool = true) {
        if date != getShownDate() || meal != getShownMeal() {
            let isInFuture = getShownDate().compare(date) == .OrderedAscending || (getShownDate().compare(date) == .OrderedSame && getShownMeal() < meal)
            let pageVC = MenuTableViewController()
            pageVC.time = (date, meal)
            pageViewController.setViewControllers([pageVC], direction: isInFuture ? .Forward : .Reverse, animated: animated, completion: nil)
            if animated {
                UIView.animateWithDuration(0.25, animations: { () -> Void in
                    self.updateCurrentPage(supressGradientAnimation: false)
                    }, completion: nil)
            } else {
                self.updateCurrentPage(supressGradientAnimation: true)
            }
        }
    }
    
    func getShownDate() -> NSDate {
        return (pageViewController.viewControllers.first? as MenuTableViewController).time?.date ?? NSDate()
    }
    
    func getShownMeal() -> Int {
        return (pageViewController.viewControllers.first? as MenuTableViewController).time?.meal ?? 0

    }
    
    // MARK: Page transitions
    func updateCurrentPage(supressGradientAnimation: Bool = true) {
        var interpolatedMeal = CGFloat(getShownMeal())
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
        if !jumpedToTodayYet {
            return (UIColor(white: 0, alpha: 1), UIColor(white: 0, alpha: 1))
        }
        let colorPairs = [
            (UIColor(red: 0.078, green: 0.392, blue: 0.584, alpha: 1), UIColor(red: 0.988, green: 0.698, blue: 0.000, alpha: 1)),
            (UIColor(red: 0.322, green: 0.455, blue: 0.729, alpha: 1), UIColor(red: 0.749, green: 0.863, blue: 0.843, alpha: 1)),
            (UIColor(red: 0.145, green: 0.404, blue: 0.580, alpha: 1), UIColor(red: 0.071, green: 0.078, blue: 0.067, alpha: 1))
        ]
        if meal < 0 {
            meal += 3
        }
        let i1 = Int(floor(meal))
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
