#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-19 10:06:43 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/utils/_show_grid_async.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

async def show_grid_async(page):
    from . import show_popup_message_async

    await show_popup_message_async(page, "Showing Grid...")
    await page.evaluate(
        """() => {
        const canvas = document.createElement('canvas');
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        canvas.style.pointerEvents = 'none';
        canvas.style.zIndex = '9999';
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        const ctx = canvas.getContext('2d');
        ctx.font = '12px Arial';

        for (let xx = 0; xx < canvas.width; xx += 20) {
            ctx.strokeStyle = xx % 100 === 0 ? 'red' : '#ffcccc';
            ctx.lineWidth = xx % 100 === 0 ? 1 : 0.5;
            ctx.beginPath();
            ctx.moveTo(xx, 0);
            ctx.lineTo(xx, canvas.height);
            ctx.stroke();
            if (xx % 100 === 0) {
                ctx.fillStyle = 'red';
                ctx.fillText(xx, xx + 5, 15);
            }
        }

        for (let yy = 0; yy < canvas.height; yy += 20) {
            ctx.strokeStyle = yy % 100 === 0 ? 'red' : '#ffcccc';
            ctx.lineWidth = yy % 100 === 0 ? 1 : 0.5;
            ctx.beginPath();
            ctx.moveTo(0, yy);
            ctx.lineTo(canvas.width, yy);
            ctx.stroke();
            if (yy % 100 === 0) {
                ctx.fillStyle = 'red';
                ctx.fillText(yy, 5, yy + 15);
            }
        }

        document.body.appendChild(canvas);
    }"""
    )

# EOF
