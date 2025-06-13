#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-02 16:57:29 (ywatanabe)"
# File: ./scitex_repo/src/scitex/io/_save_mp4.py

from matplotlib import animation


def _mk_mp4(fig, spath_mp4):
    axes = fig.get_axes()

    def init():
        return (fig,)

    def animate(i):
        for ax in axes:
            ax.view_init(elev=10.0, azim=i)
        return (fig,)

    anim = animation.FuncAnimation(
        fig, animate, init_func=init, frames=360, interval=20, blit=True
    )

    writermp4 = animation.FFMpegWriter(fps=60, extra_args=["-vcodec", "libx264"])
    anim.save(spath_mp4, writer=writermp4)
    print("\nSaving to: {}\n".format(spath_mp4))


# EOF
