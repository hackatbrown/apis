//
//  MenuView.swift
//  RattyApp
//
//  Created by Nate Parrott on 2/18/15.
//  Copyright (c) 2015 Nate Parrott. All rights reserved.
//

import UIKit

class MenuView: UIView {
    
    override init() {
        sections = StackView()
        sections.hideOverflowViews = true
        super.init(frame: CGRectZero)
        addSubview(sections)
    }

    required init(coder aDecoder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    let maxHeight: CGFloat = 200
    
    override func sizeThatFits(size: CGSize) -> CGSize {
        var size = sections.sizeThatFits(size)
        size.height = min(maxHeight, size.height)
        return size
    }
    
    override func layoutSubviews() {
        super.layoutSubviews()
        sections.frame = bounds
    }
    
    var sections: StackView
    
    var menu: DiningAPI.MealMenu? {
        didSet {
            if let theMenu = menu {
                sections.views = theMenu.sections.map({ MenuSectionView(section: $0) })
            } else {
                sections.views = []
            }
        }
    }
}
