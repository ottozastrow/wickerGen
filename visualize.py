import matplotlib.pyplot as plt
from graph import count_connections, get_knot_by_id
from util_classes import *
from utils import *
import plotly.express as px
import pandas as pd
from copy import deepcopy


color_map = {0:"black", 1:"navy", 2:"olive", 3:"lightgrey"}

def update_layout(fig):
    fig.update_layout(
        scene = dict(aspectmode = "data", xaxis=dict(visible=False, showline=False, showgrid=False),
                                          yaxis=dict(visible=False, showline=False, showgrid=False),
                                          zaxis=dict(showline=False, showgrid=False, showticklabels=False),
                                          zaxis_title=''))
    fig.update_layout(showlegend=False)


def plot_3d_strands(strands: list[Strand], save:bool):
    points = strands_to_dict_list(strands)
    df = pd.DataFrame(points)

    fig = px.line_3d(df, x='x', y='y', z='z', color="color", 
                     line_group="strand")#, color_discrete_map=color_map)
    update_layout(fig)
    
    fig.show()
    if save:
        fig.write_html("renderings/sample.html")


def write_obj_file(strands: list[Strand], path:str='generater_output.obj'):
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


def animations_to_dataframe(animation_steps: list[list[Strand]]):
    points = []
    for step_i in range(len(animation_steps)):
        points += strands_to_dict_list(animation_steps[step_i], animation_step=step_i)
    return points



def plot_3d_animated_strands(animation_steps: list[list[Strand]], save: bool):
    df = animations_to_dataframe(animation_steps)

    fig = px.line_3d(df, x='x', y='y', z='z', color="color", color_discrete_map=color_map,
                        animation_frame='animation_step', animation_group='strand', line_group="strand")
    update_layout(fig)
    
    fig.show()
    if save:
        fig.write_html("renderings/sample_3d_animation.html")


def plot_points(knots, links):
    edges_x, edges_z, edges_y, indexes = [], [], [], []
    index = 0

    for knot in knots:
        edges_x.append(knot.pos.x)
        edges_y.append(knot.pos.y)
        edges_z.append(knot.pos.z)
        indexes.append(index)
        index += 1

    df = pd.DataFrame(list(zip(edges_x, edges_y, edges_z, indexes)), columns =['x', 'y', 'z', 'index'])
    
    fig = px.line_3d(df, x='x', y='y', z='z', color="index")
    
    update_layout(fig)
    
    fig.show()

def plot_graph(knots, links):
    links_down, links_up = links
    counter = 0
    edges_x, edges_z, edges_y, line_group = [], [], [], []
    for index_knot_i in range(len(links_down)):
        for index_knot_j in links_down[index_knot_i]:
            knot_i = get_knot_by_id(index_knot_i, knots)
            knot_j = get_knot_by_id(index_knot_j, knots)
            edges_x += [knot_i.pos.x, knot_j.pos.x]
            edges_y += [knot_i.pos.y, knot_j.pos.y]
            edges_z += [knot_i.pos.z, knot_j.pos.z]
            line_group += [counter, counter]
            counter += 1

    df = pd.DataFrame(list(zip(edges_x, edges_y, edges_z, line_group)), columns =['x', 'y', "z", "line_group"])
    
    fig = px.line_3d(df, x='x', y='y', z='z', line_group="line_group")
    
    update_layout(fig)
    
    fig.show()


def strands_to_dict_list(strands: list[Strand], animation_step:int=0) -> list[dict]:
    """ 
    creates list of dicts (that can be used for visualization) from list of strands
    animation_step
    output used to generate a dataframe
    """
    points = []
    assert(len(strands[0].x) > 0), "this strand has no history"
    for i in range(len(strands)):
        strand = strands[i]
        for t in range(len(strand.x)):
            color = i
            if color < 4:
                color = 0
            elif 12 <= i < 16:
                color = 1
            elif len(strands) // 2 + 8 <= i < len(strands) // 2 + 12:
                color = 2
            else:
                color = 3
            points.append({'y':strand.y[t], 'x':strand.x[t], 'z':round_step_size(strand.z[t], 0.001), "size":0.01,
                            'color':color,  'strand':i, 'animation_step':animation_step, 'text':strand.slot})
    return points


def plot_animated_strands(strands, save):
    points = strands_to_dict_list(strands)
    df = pd.DataFrame(points)

    fig = px.scatter(df, x='x', y='y', color="color", size="size",
                     width=900, height= 900, 
                     hover_name="text", 
                     animation_frame='z', animation_group='strand', color_discrete_map=color_map)
    fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 30
    fig.update_layout({
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    })
    fig.update_layout(
        scene = dict(aspectmode = "data", ),showlegend=False,yaxis=dict(showgrid=False, visible=False), xaxis=dict(showgrid=False, visible=False))
    # update_layout(fig)
    fig.update_layout(showlegend=False)
    fig.update_traces(
    marker_coloraxis=None
    )
    fig.show()
    if save:
        fig.write_html("renderings/sample_2d_animation.html")


def calc_3d_robot_plane(strands:list[Strand], relative_time:float=0.10) -> list[list[Strand]]:
    """ 
    relative_time: float between 0 and 1. starts 3d animation from that relative vertical position  
    """
    minz, maxz = min_max_z_from_strands(strands)
    # note: z is vertical component of 3d coordinate. time is -z because we weave top-down
    cut_threshold = maxz - (maxz-minz)*relative_time

    slice_height = Arena.interpolate_steps_per_meter
    animation_steps = []
    for i in range(Arena.animation_steps):
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


def calc_2d_robot_plane(strands: list[Strand]) -> list[Strand]:
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
