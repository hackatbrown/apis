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
        label = UILabel()
        iconVibrancy = UIVisualEffectView(effect: UIVibrancyEffect.notificationCenterVibrancyEffect())
        super.init(frame: CGRectZero)
        addSubview(icon)
        addSubview(label)
        
        addSubview(iconVibrancy)
        iconVibrancy.contentView.addSubview(icon)
        icon.image = iconForMenuName(section.name)
        icon.tintColor = UIColor.whiteColor()
        icon.contentMode = .ScaleAspectFit
        label.text = ", ".join(section.items)
        label.textColor = UIColor.whiteColor()
        label.numberOfLines = 0
    }
    
    override func layoutSubviews() {
        super.layoutSubviews()
        if let size = icon.image?.size {
            let width: CGFloat = 16
            let height = label.font.pointSize
            iconVibrancy.frame = CGRectMake(-WidgetLeftMargin, 7, width, height)
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
    var label: UILabel

    required init(coder aDecoder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
}
