//
//  NavigationView.swift
//  RattyApp
//
//  Created by Nate Parrott on 2/16/15.
//  Copyright (c) 2015 Nate Parrott. All rights reserved.
//

import UIKit

class NavigationView: UIView {

    @IBOutlet var breakfast: UIButton!
    @IBOutlet var lunch: UIButton!
    @IBOutlet var dinner: UIButton!
    @IBOutlet var prevDay: UIButton!
    @IBOutlet var nextDay: UIButton!
    
    lazy var mealIndicator: UIView = {
        let v = UIView()
        self.addSubview(v)
        v.backgroundColor = UIColor.whiteColor()
        return v
    }()
    
    // selectedMeal is a float so we can represent intermediate states during a gesture
    var selectedMeal: CGFloat = 0 {
        didSet {
            setNeedsLayout()
            layoutIfNeeded()
        }
    }
    var onSelectedMealChanged: (() -> ())?
    
    @IBAction func clickMeal(sender: UIButton) {
        UIView.animateWithDuration(0.25, animations: { () -> Void in
            switch sender {
            case self.breakfast: self.selectedMeal = 0
            case self.lunch: self.selectedMeal = 1
            case self.dinner: self.selectedMeal = 2
            default: self.selectedMeal = 0
            }
        }, completion: nil)
        if let cb = onSelectedMealChanged {
            cb()
        }
    }
    
    var onPrevDayClicked, onNextDayClicked: (() -> ())?
    @IBAction func clickDay(sender: UIButton) {
        var callback: (() -> ())?
        switch sender {
        case prevDay: callback = onPrevDayClicked
        case nextDay: callback = onNextDayClicked
        default: callback = nil
        }
        if let cb = callback {
            cb()
        }
    }
    
    override func layoutSubviews() {
        super.layoutSubviews()
        // position the meal indicator:
        let minX = breakfast.frame.origin.x
        let maxX = dinner.frame.origin.x
        var x = minX + (maxX - minX) * (selectedMeal / 2)
        if selectedMeal > 2 || selectedMeal < 0 {
            var coefficient = selectedMeal
            if coefficient > 2.5 {
                coefficient = coefficient - 3
            } else if coefficient < -0.5 {
                coefficient = 3 + coefficient
            }
            let flyDist = minX * 2.5
            if coefficient > 2 {
                x = maxX + flyDist * (coefficient - 2)
            } else {
                x = minX - flyDist * -coefficient
            }
        }
        mealIndicator.frame = CGRectMake(x, 0, lunch.frame.size.width, 2)
    }
}
