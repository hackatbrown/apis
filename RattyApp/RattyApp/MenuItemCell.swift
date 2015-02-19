//
//  MenuItemCell.swift
//  RattyApp
//
//  Created by Nate Parrott on 2/19/15.
//  Copyright (c) 2015 Nate Parrott. All rights reserved.
//

import UIKit

class MenuItemCell: UITableViewCell {
    override init(style: UITableViewCellStyle, reuseIdentifier: String?) {
        super.init(style: style, reuseIdentifier: reuseIdentifier)
        textLabel.font = UIFont(name: "AvenirNext-Medium", size: 16)
        textLabel.textColor = UIColor.blackColor()
    }

    required init(coder aDecoder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
}
