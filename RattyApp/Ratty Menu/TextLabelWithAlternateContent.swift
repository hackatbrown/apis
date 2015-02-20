//
//  TextLabelWithAlternateContent.swift
//  RattyApp
//
//  Created by Nate Parrott on 2/19/15.
//  Copyright (c) 2015 Nate Parrott. All rights reserved.
//

import UIKit

class TextLabelWithAlternateContent: UIView {
    lazy var label: UILabel = {
        let l = UILabel()
        l.numberOfLines = 0
        self.addSubview(l)
        return l
    }()
    override func layoutSubviews() {
        super.layoutSubviews()
        label.text = _stringForSize(bounds.size)
        let size = label.sizeThatFits(bounds.size)
        label.frame = CGRectMake(0, 0, size.width, size.height)
        let c = _sizeForString(label.text!, maxSize: bounds.size)
        // println("height that fits: \(size.height); height: \(bounds.size.height); calculated height: \(c.height)")
    }
    var strings: [String] = [] {
        didSet {
            setNeedsLayout()
        }
    }
    private var _stringsByLength: [String] {
        get {
            return strings.sorted({ countElements($0) > countElements($1) })
        }
    }
    private func _applyLabelAttributesToStringForLayout(string: String) -> NSAttributedString {
        let pStyle = NSParagraphStyle.defaultParagraphStyle().mutableCopy() as NSMutableParagraphStyle
        pStyle.lineBreakMode = .ByWordWrapping
        let attrs: [NSObject: AnyObject] = [NSFontAttributeName as NSObject: label.font! as AnyObject, NSParagraphStyleAttributeName as NSObject: pStyle as AnyObject]
        return NSAttributedString(string: string, attributes: attrs)
    }
    private func _sizeForString(string: String, maxSize: CGSize) -> CGSize {
        let oldText = label.text
        label.text = string
        let sizeForString = label.sizeThatFits(maxSize)
        label.text = oldText
        return sizeForString
        // return _applyLabelAttributesToStringForLayout(string).boundingRectWithSize(maxSize, options: .UsesLineFragmentOrigin, context: nil).size
    }
    private func _stringForSize(size: CGSize) -> String {
        for s in _stringsByLength {
            let sizeNeeded = _sizeForString(s, maxSize: size)
            if sizeNeeded.width <= size.width && sizeNeeded.height <= size.height {
                return s
            }
        }
        return ""
    }
    override func sizeThatFits(size: CGSize) -> CGSize {
        let string = _stringForSize(size)
        var textSize = _sizeForString(string, maxSize: size)
        textSize.height = min(maxHeight, textSize.height)
        return textSize
    }
    var maxHeight: CGFloat = 9999999
}
