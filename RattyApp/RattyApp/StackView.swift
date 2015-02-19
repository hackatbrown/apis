//
//  StackView.swift
//  BrownMenu
//
//  Created by Nate Parrott on 1/27/15.
//  Copyright (c) 2015 Nate Parrott. All rights reserved.
//

import UIKit

class StackView: UIView {
    var views: [UIView] = [] {
        willSet {
            for view in views {
                view.removeFromSuperview()
            }
        }
        didSet {
            for view in views {
                addSubview(view)
            }
        }
    }
    
    override func layoutSubviews() {
        var y: CGFloat = 0
        for view in views {
            let height = view.sizeThatFits(self.bounds.size).height
            view.frame = CGRectMake(0, y, self.bounds.size.width, height)
            y += height
            if hideOverflowViews {
                view.hidden = y > bounds.size.height
            }
        }
    }
    
    var hideOverflowViews: Bool = false
    
    override func sizeThatFits(size: CGSize) -> CGSize {
        var y: CGFloat = 0
        var maxW: CGFloat = 0
        for view in views {
            let viewSize = view.sizeThatFits(size)
            y += viewSize.height
            maxW = max(viewSize.width, maxW)
        }
        return CGSizeMake(maxW, y)
    }
}
