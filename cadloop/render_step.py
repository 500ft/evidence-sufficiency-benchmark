"""Render a STEP model with Z upright and a second view of its underside."""
import argparse
from pathlib import Path

import cadquery as cq
import numpy as np
import pyvista as pv


def render(source,target,title):
    shape=cq.importers.importStep(str(source)).val()
    points,triangles=shape.tessellate(0.12,0.12)
    mesh=pv.PolyData(np.asarray([p.toTuple() for p in points]),
                     np.asarray([[3,*t] for t in triangles],dtype=np.int64).ravel()).clean()
    edges=mesh.extract_feature_edges(feature_angle=35,boundary_edges=True,
                                     non_manifold_edges=False,manifold_edges=False)
    center=np.asarray(mesh.center)
    distance=max(mesh.length,1)*2
    plotter=pv.Plotter(off_screen=True,shape=(1,2),window_size=(1600,800))
    for column,above in [(0,True),(1,False)]:
        plotter.subplot(0,column);plotter.set_background('white')
        plotter.add_mesh(mesh,color='#b6c5d0',show_edges=False,
                         smooth_shading=True,split_sharp_edges=True,
                         ambient=0.35,diffuse=0.65,specular=0.15)
        plotter.add_mesh(edges,color='#23313b',line_width=1)
        offset=np.array([0.9,-1.2,0.9 if above else -0.9])*distance
        plotter.camera_position=[(center+offset).tolist(),center.tolist(),(0,0,1)]
        plotter.camera.parallel_projection=True
        plotter.reset_camera()
        plotter.add_text(title+('\nIsometric' if above else '\nUnderside - blind mounting holes'),
                         position='upper_left',font_size=12,color='#23313b')
        plotter.add_text('CONCEPT - NOT FOR FABRICATION',position='lower_left',font_size=10,color='#6e2531')
        plotter.add_axes()
    target=Path(target);target.parent.mkdir(parents=True,exist_ok=True)
    plotter.screenshot(str(target));plotter.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('source',type=Path);parser.add_argument('target',type=Path)
    parser.add_argument('--title',default='CAD concept')
    args=parser.parse_args()
    render(args.source,args.target,args.title)
