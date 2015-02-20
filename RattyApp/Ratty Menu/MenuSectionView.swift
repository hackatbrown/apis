//
//  MenuView.swift
//  RattyApp
//
//  Created by Nate Parrott on 2/18/15.
//  Copyright (c) 2015 Nate Parrott. All rights reserved.
//

import UIKit

class MenuSectionView: UIView {
    init(section: DiningAPI.MenuSection) {
        icon = UIImageView()
        label = TextLabelWithAlternateContent()
        iconVibrancy = UIVisualEffectView(effect: UIVibrancyEffect.notificationCenterVibrancyEffect())
        super.init(frame: CGRectZero)
        addSubview(icon)
        addSubview(label)
        
        addSubview(iconVibrancy)
        iconVibrancy.contentView.addSubview(icon)
        icon.image = iconForMenuName(section.name)
        icon.tintColor = UIColor.whiteColor()
        icon.contentMode = .ScaleAspectFit
        label.label.textColor = UIColor.whiteColor()
        
        var strings: [String] = []
        for i in 0..<(countElements(section.items)+1) {
            var itemsToShow = Array(section.items[0..<i])
            let leftoverCount = countElements(section.items) - i
            if leftoverCount > 0 {
                itemsToShow.append("\(leftoverCount) more")
            }
            strings.append(", ".join(itemsToShow))
        }
        label.strings = strings
        label.maxHeight = label.label.font.pointSize * 2 + 5
        
    }
    
    override func layoutSubviews() {
        super.layoutSubviews()
        if let size = icon.image?.size {
            let width: CGFloat = 16
            let height = label.label.font.pointSize
            iconVibrancy.frame = CGRectMake(-WidgetLeftMargin, 2, width, height)
            icon.frame = iconVibrancy.bounds
        }
        label.frame = CGRectMake(0, 0, bounds.size.width, bounds.size.height)
    }
    
    override func sizeThatFits(size: CGSize) -> CGSize {
        var size = label.sizeThatFits(size)
        size.height += 10
        return size
    }
    
    func iconForMenuName(name: String) -> UIImage? {
        let map: [String: String] = ["bistro": "bistro", "chef's corner": "pizza", "daily sidebars": "salad", "grill": "burger", "roots & shoots": "tomato"]
        if let imageName = map[name] {
            return UIImage(named: imageName)?.imageWithRenderingMode(.AlwaysTemplate)
        } else {
            return nil
        }
    }
    
    var icon: UIImageView
    var iconVibrancy: UIVisualEffectView
    var label: TextLabelWithAlternateContent

    required init(coder aDecoder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
}
