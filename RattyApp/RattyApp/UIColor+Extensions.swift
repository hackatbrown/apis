//
//  UIColor+Extensions.swift
//  RattyApp
//
//  Created by Nate Parrott on 2/17/15.
//  Copyright (c) 2015 Nate Parrott. All rights reserved.
//

import UIKit

extension UIColor {
    func rgba() -> (CGFloat, CGFloat, CGFloat, CGFloat) {
        var r: CGFloat = 0
        var g: CGFloat = 0
        var b: CGFloat = 0
        var a: CGFloat = 0
        var w: CGFloat = 0
        if getRed(&r, green: &g, blue: &b, alpha: &a) {
            return (r,g,b,a)
        } else if getWhite(&w, alpha: &a) {
            return (w,w,w,a)
        } else {
            return (0,0,0,0)
        }
    }
    
    func mix(color: UIColor, amount: CGFloat) -> UIColor {
        let (r,g,b,a) = rgba()
        let (r2,g2,b2,a2) = color.rgba()
        let mix: (CGFloat,CGFloat,CGFloat) -> CGFloat = { $0 * (1 - $2) + $1 * $2 }
        return UIColor(red: mix(r,r2,amount), green: mix(g,g2,amount), blue: mix(b,b2,amount), alpha: mix(a,a2,amount))
    }
}
