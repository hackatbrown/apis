//
//  WordCloudView.swift
//  RattyApp
//
//  Created by Nate Parrott on 2/18/15.
//  Copyright (c) 2015 Nate Parrott. All rights reserved.
//

import UIKit

class WordCloudView: UIView {
    var words: [String] = [] {
        didSet {
            labels = words.map({
            (let word) -> UILabel in
                let label = UILabel()
                label.text = word
                label.font = UIFont.systemFontOfSize(UIFont.systemFontSize())
                label.textColor = UIColor.whiteColor()
                label.textAlignment = .Center
                return label
            })
        }
    }
    private var labels: [UILabel] = [] {
        willSet {
            for label in labels {
                label.removeFromSuperview()
            }
        }
        didSet {
            for label in labels {
                addSubview(label)
            }
        }
    }
    override func sizeThatFits(size: CGSize) -> CGSize {
        var maxCellsWide: Int = 0
        var maxCellsHigh: Int = 0
        for row in computeCellLayoutsAtSize(size) {
            var cellsWide: Int = 0
            for (label, cells) in row {
                cellsWide += cells
            }
            maxCellsWide = max(maxCellsWide, cellsWide)
            maxCellsHigh++
        }
        return CGSizeMake(CGFloat(maxCellsWide) * minCellWidth, CGFloat(maxCellsHigh) * cellHeight)
    }
    override func layoutSubviews() {
        super.layoutSubviews()
        let cellWidth = bounds.size.width / CGFloat(nCellsWideForWidth(bounds.size.width))
        for label in labels {
            label.hidden = true
        }
        var y: CGFloat = 0
        for row in computeCellLayoutsAtSize(bounds.size) {
            var x: CGFloat = 0
            for (label, cellsWide) in row {
                label.hidden = false
                label.frame = CGRectMake(x, y, cellWidth * CGFloat(cellsWide), cellHeight)
                x += cellWidth * CGFloat(cellsWide)
            }
            y += cellHeight
        }
    }
    // MARK: Layout
    private let minCellWidth: CGFloat = 45
    private let cellHeight: CGFloat = 20
    private func nCellsWideForWidth(width: CGFloat) -> Int {
        return Int(max(1, floor(width / minCellWidth)))
    }
    private func computeCellLayoutsAtSize(size: CGSize) -> [[(UILabel, Int)]] {
        if size.height == 0 {
            return []
        }
        let nCellsHigh = Int(floor(size.height / cellHeight))
        
        var rows = [[(UILabel, Int)]](count: nCellsHigh, repeatedValue: [])
        
        let cellsInRow = {
            (row: [(UILabel, Int)]) -> Int in
            return row.map({ $0.1 }).reduce(0, +)
        }
        
        let nCellsWide = nCellsWideForWidth(size.width)
        let cellWidth = size.width / CGFloat(nCellsWide)
        
        for label in labels {
            let padding = (cellHeight - label.font.pointSize)/2
            let width = padding * 2 + label.sizeThatFits(bounds.size).width
            let widthInCells = Int(ceil(width / cellWidth))
            
            for rowIndex in 0..<nCellsHigh {
                if cellsInRow(rows[rowIndex]) + widthInCells <= nCellsWide {
                    rows[rowIndex] += [(label, widthInCells)]
                    break
                }
            }
        }
        return rows
    }
}


