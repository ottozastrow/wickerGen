import matplotlib.pyplot as plt
from graph import count_connections
from util_classes import *
from utils import *
import plotly.express as px
import pandas as pd
from copy import deepcopy





def plot_3d_strands(strands, save):
    points = []
    assert(len(strands[0].x) > 0), "this strand has no history"
    for i in range(len(strands)):
        strand = strands[i]
        for t in range(len(strand.x)):
            points.append({'y':strand.y[t], 'x':strand.x[t], 'z':strand.z[t], 'color':i%4, 'strand':i})
    
    df = pd.DataFrame(points)
    fig = px.line_3d(df, x='x', y='y', z='z', color="strand")

    fig.update_layout(
        scene = dict(aspectmode = "data", ))
    fig.show()
    fig.write_html("renderings/sample.html")


def write_obj_file(strands, path='generater_output.obj'):
    def pt_to_str(pts):
        return [str((round(pt, 5))) for pt in pts]

    with open(path, 'w') as ofile:
        vertex_count = 1
        for strand in strands:
            strand_points = points_list_from_strand_xyz(strand)
            for point in strand_points:
                line = "v " + " ".join(pt_to_str(point)) + "\n"
                ofile.write(line)
            indices = [str(i) for i in range(vertex_count, len(strand_points) + vertex_count)]
            vertex_count += len(strand_points)
            indices = "l " + " ".join(indices) + "\n"
            ofile.write(indices)
            
    print("wrote obj file to ", path)

def animations_to_dataframe(animation_steps):
    points = []

    for step_i in range(len(animation_steps)):
        strands = animation_steps[step_i]
        assert(len(strands[0].x) > 0), "this strand has no history"
        for i in range(len(strands)):
            strand = strands[i]
            
            for t in range(len(strand.x)):
                
                points.append({'y':strand.y[t], 'x':strand.x[t], 'z':strand.z[t], 
                               'color':i, 'animation_step': step_i})
                
    df = pd.DataFrame(points)
    
    return df

def strands_to_dataframe(strands, add_robots=False):
    points = []
    assert(len(strands[0].x) > 0), "this strand has no history"
    for i in range(len(strands)):
        strand = strands[i]
 
        for t in range(len(strand.x)):            
            points.append({'y':strand.y[t], 'x':strand.x[t], 'z':round_step_size(strand.z[t], 0.001), 
                            'color':i%2,  'strand':i})


    df = pd.DataFrame(points)
    
    return df


def plot_3d_animated_strands(animation_steps, save):
    df = animations_to_dataframe(animation_steps)

    fig = px.line_3d(df, x='x', y='y', z='z', color="color", 
                        animation_frame='animation_step', animation_group='color')
    fig.update_layout(
        scene = dict(aspectmode = "data", ))
    fig.show()
    if save:
        fig.write_html("renderings/sample_3d_animation.html")


def plot_animated_strands(strands, save):
    df = strands_to_dataframe(strands, add_robots=True)
    fig = px.scatter(df, x='x', y='y', color="color", 
                        animation_frame='z', animation_group='strand', height=1000, width=1000)          
    fig.update_layout(
        scene = dict(aspectmode = "data", ))
    fig.show()
    if save:
        fig.write_html("renderings/sample_2d_animation.html")


def calc_3d_robot_plane(strands, relative_time = 0.05):
    """ 
    relative_time: float between 0 and 1. cuts 3d model until that time. then shows robot pane 
    """
    minz, maxz = min_max_z_from_strands(strands)
    # note: z is vertical component of 3d coordinate. time is -z because we weave top-down
    cut_threshold = maxz - (maxz-minz)*relative_time
    steps = Arena.animation_steps
    slice_height = 0.01
    animation_steps = []
    for i in range(steps):
        new_strands = []
        for strand in strands:
            # stop if animation has more steps then strand
            if i>=len(strand.z):
                break
            threshold = cut_threshold - i * slice_height
            new_strand = deepcopy(strand)
            indexes = np.argwhere(strand.z < threshold)
            new_strand.z = np.delete(new_strand.z, indexes)
            new_strand.x = np.delete(new_strand.x, indexes)
            new_strand.y = np.delete(new_strand.y, indexes)

            if len(new_strand.x) > 0:
                new_strand.x[0], new_strand.y[0], new_strand.z[0] = compute_robobt_position(new_strand)
                                    
                new_strands.append(new_strand)
        animation_steps.append(new_strands)

    return animation_steps


def calc_2d_robot_plane(strands):
    new_strands = []
    for strand in strands:
        new_strand = Strand(strand.slot)
        # linear interpolation requires 2 entries
        if len(strand.x) > 2:
            for i in range(2, len(strand.x)-2):
                x,y,z = compute_robobt_position(strand, index=i)
                new_strand.x.append(x)
                new_strand.y.append(y)
                new_strand.z.append(z)
        new_strands.append(new_strand) 

    return new_strands
