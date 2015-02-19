//
//  MealPicker.swift
//  RattyApp
//
//  Created by Nate Parrott on 2/18/15.
//  Copyright (c) 2015 Nate Parrott. All rights reserved.
//

import UIKit

class MealPicker: UIView {
    
    override init() {
        func createMealLabels() -> [UILabel] {
            let meals = ["breakfast", "lunch", "dinner"]
            return meals.map() {
                (meal: String) in
                let label = UILabel()
                label.text = meal.uppercaseString
                label.textColor = UIColor.whiteColor()
                label.textAlignment = .Center
                label.font = UIFont.boldSystemFontOfSize(13)
                label.userInteractionEnabled = true
                return label
            }
        }
        vibrancyView = UIVisualEffectView(effect: UIVibrancyEffect.notificationCenterVibrancyEffect())
        mealLabels = createMealLabels()
        highlightedMealLabels = createMealLabels()
        super.init(frame: CGRectZero)
        
        addSubview(vibrancyView)
        for v in mealLabels {
            vibrancyView.contentView.addSubview(v)
            v.addGestureRecognizer(UITapGestureRecognizer(target: self, action: "tappedMeal:"))
        }
        for v in highlightedMealLabels {
            addSubview(v)
        }
    }
    
    override func layoutSubviews() {
        super.layoutSubviews()
        vibrancyView.frame = bounds
        
        let minWidth = sizeThatFits(bounds.size).width
        let leftMargin = max(0, bounds.size.width - minWidth - 20)
        let viewWidth = (bounds.size.width - leftMargin)/3
        for viewArray in [mealLabels, highlightedMealLabels] {
            var x = leftMargin
            for view in viewArray {
                view.frame = CGRectMake(x, 0, viewWidth, bounds.size.height)
                x += viewWidth
            }
        }
    }
    
    func tappedMeal(sender: UITapGestureRecognizer) {
        selectedMeal = find(mealLabels, sender.view! as UILabel)!
        if let cb = onSelectedMealChanged {
            cb()
        }
    }
    
    var selectedMeal: Int = 0 {
        didSet {
            for v in highlightedMealLabels {
                v.hidden = true
            }
            highlightedMealLabels[selectedMeal].hidden = false
        }
    }
    var onSelectedMealChanged: (() -> ())?

    required init(coder aDecoder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    var mealLabels: [UILabel]
    var highlightedMealLabels: [UILabel]
    var vibrancyView: UIVisualEffectView
    
    override func sizeThatFits(size: CGSize) -> CGSize {
        let width = maxElement(mealLabels.map({ $0.sizeThatFits(size).width })) * CGFloat(countElements(mealLabels))
        return CGSizeMake(width, mealLabels[0].sizeThatFits(size).height + 10)
    }
}
