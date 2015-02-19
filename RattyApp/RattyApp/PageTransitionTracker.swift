//
//  PageTransitionTracker.swift
//  RattyApp
//
//  Created by Nate Parrott on 2/16/15.
//  Copyright (c) 2015 Nate Parrott. All rights reserved.
//

import UIKit

class PageTransitionTracker: NSObject {
    init(pageViewController: UIPageViewController) {
        self.pageViewController = pageViewController
        super.init()
    }
    
    var pageViewController: UIPageViewController
    
    private(set) var trackingViewController: UIViewController?
    private var initialX: CGFloat?
    private var displayLink: CADisplayLink?
    
    private(set) var isTracking: Bool = false
    
    func startTracking() {
        if isTracking {
            return
        }
        isTracking = true
        trackingViewController = (pageViewController.viewControllers.first? as UIViewController)
        displayLink = CADisplayLink(target: self, selector: "_displayLink")
        displayLink!.addToRunLoop(NSRunLoop.mainRunLoop(), forMode: NSRunLoopCommonModes)
        initialX = getTrackingViewCenterX()
    }
    
    private func getTrackingViewCenterX() -> CGFloat {
        return (trackingViewController!.view.layer.presentationLayer() as CALayer).convertPoint(CGPointMake(CGRectGetMidX((trackingViewController!.view.layer.presentationLayer() as CALayer).bounds), 0), toLayer: pageViewController.view.layer).x
    }
    
    func stopTracking() {
        if isTracking {
            isTracking = false
            displayLink!.invalidate()
            displayLink = nil
            trackingViewController = nil
            progress = 0
        }
    }
    
    func _displayLink() {
        if trackingViewController == nil {
            return
        }
        progress = (initialX! - getTrackingViewCenterX()) / pageViewController.view.bounds.size.width
        if let cb = trackingCallback {
            cb()
        }
    }
    
    var progress: CGFloat = 0
    var trackingCallback: (() -> ())?
}
