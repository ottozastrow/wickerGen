import matplotlib.pyplot as plt


def plot_strands(strands):
    starttime = 0
    # endtime = Arena.divide_steps*2
    endtime = len(strands[0].x)
    
    # for strand in strands:
    #     plt.text(strand.x[-1], strand.y[-1], strand.knot_slot)
    #     plt.plot(strand.x[-1], strand.y[-1])
    counter = 0
    for strand in strands:
        plt.plot(strand.x[starttime:endtime], strand.y[starttime:endtime])
        counter += 1
        if counter == 4:
            break
    
    plt.show()


def plot_3d_strands(strands):
    import pandas as pd
    import plotly.express as px
    
    points = []
    assert(len(strands[0].x) > 0), "this strand has no history"
    for i in range(len(strands)):
        strand = strands[i]
        for t in range(len(strand.x)):
            points.append({'y':strand.y[t], 'x':strand.x[t], 'z':strand.z[t], 'color':i})
        
    df = pd.DataFrame(points)
    fig = px.line_3d(df, x='x', y='y', z='z', color="color")        
    fig.update_layout(
        scene = dict(aspectmode = "data", ))
    fig.show()
    fig.write_html("renderings/sample.html")