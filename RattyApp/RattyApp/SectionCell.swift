//
//  SectionCell.swift
//  RattyApp
//
//  Created by Nate Parrott on 2/16/15.
//  Copyright (c) 2015 Nate Parrott. All rights reserved.
//

import UIKit

class SectionCell: UITableViewCell {
    
    var insets: UIEdgeInsets = UIEdgeInsetsZero {
        didSet {
            setNeedsLayout()
        }
    }
    
    var mainView: UIView? {
        willSet {
            if let m = mainView {
                m.removeFromSuperview()
            }
        }
        didSet {
            if let m = mainView {
                addSubview(m)
            }
        }
    }
    
    override func layoutSubviews() {
        super.layoutSubviews()
        if let m = mainView {
            m.frame = UIEdgeInsetsInsetRect(bounds, insets)
        }
    }
    
    var section: DiningAPI.MenuSection? {
        didSet {
            if let s = section {
                mainView = SectionCell.createStackViewForSection(s)
            }
        }
    }
    
    class func createStackViewForSection(section: DiningAPI.MenuSection) -> StackView {
        let sv = StackView()
        let header = MenuRow()
        header.label.text = section.name.uppercaseString
        header.label.textAlignment = .Center
        let views: [MenuRow] = [header] + section.items.map() {
            (let item) in
            let row = MenuRow()
            row.label.text = item
            return row
        }
        var i = 0
        for view in views {
            view.inset = UIEdgeInsetsMake(MenuSectionInset, MenuSectionInset, MenuSectionInset, MenuSectionInset)
            let alpha: CGFloat = (i == 0) ? 0.5 : (i % 2 == 0 ? 0.25 : 0.1)
            view.backgroundColor = UIColor(white: 1, alpha: alpha)
            i++
        }
        sv.views = views
        sv.backgroundColor = UIColor(white: 1, alpha: 0.25)
        return sv
    }
}
