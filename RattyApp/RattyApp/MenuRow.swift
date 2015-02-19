//
//  MenuRow.swift
//  BrownMenu
//
//  Created by Nate Parrott on 1/27/15.
//  Copyright (c) 2015 Nate Parrott. All rights reserved.
//

import UIKit

class MenuRow: UIView {
    
    var inset: UIEdgeInsets = UIEdgeInsetsZero
    lazy var label: UILabel = {
        let label = UILabel()
        self.addSubview(label)
        label.numberOfLines = 0
        label.font = UIFont(name: "AvenirNext-Medium", size: 16)
        label.textColor = UIColor.blackColor()
        return label
    }()
    
    override func layoutSubviews() {
        super.layoutSubviews()
        label.frame = UIEdgeInsetsInsetRect(bounds, inset)
    }
    
    override func sizeThatFits(size: CGSize) -> CGSize {
        let labelWidth = size.width - inset.left - inset.right
        let labelSize = label.sizeThatFits(CGSizeMake(labelWidth, size.height))
        return CGSizeMake(labelSize.width + inset.left + inset.right, labelSize.height + inset.top + inset.bottom)
    }
}
