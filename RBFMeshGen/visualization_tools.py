import matplotlib.pyplot as plt


def plot_each_polygon_separately(polygons):
    for i, polygon in enumerate(polygons):
        fig, ax = plt.subplots()  # Create a new figure and axes for each polygon
        x, y = polygon.exterior.xy  # Get the x and y coordinates of the polygon's exterior
        ax.fill(x, y, alpha=0.5)  # Fill the polygon with a semi-transparent color

        # Optionally plot the interiors (holes) if they exist
        for interior in polygon.interiors:
            x, y = interior.xy
            ax.fill(x, y, "k")  # Fill holes with black color

        ax.set_title(f'Polygon {i+1}')  # Title with polygon number
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_aspect('equal')  # Set aspect ratio to be equal to ensure the polygon is not distorted
        plt.show()

def plot_all_polygons_in_one_figure(polygons):
    fig, ax = plt.subplots()  # Create a single figure and axes object
    colors = plt.cm.viridis(np.linspace(0, 1, len(polygons)))  # Generate distinct colors

    for i, polygon in enumerate(polygons):
        x, y = polygon.exterior.xy  # Get the x and y coordinates of the polygon's exterior
        ax.fill(x, y, color=colors[i], alpha=0.5, label=f'Polygon {i+1}')  # Fill each polygon with a unique color

        # Optionally plot the interiors (holes) if they exist
        for interior in polygon.interiors:
            x, y = interior.xy
            ax.fill(x, y, "k")  # Fill holes with black color

    ax.set_title('All Polygons')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_aspect('equal')  # Set aspect ratio to be equal to ensure the polygons are not distorted
    ax.legend()  # Add a legend to identify each polygon
    plt.show()


def plot_points(points):
    # Prepare data for plotting
    x = [p.x for p in points]
    y = [p.y for p in points]
    labels = [p.label for p in points]
    is_border = [p.is_border for p in points]  # Extract border status

    # Define point sizes based on border status
    sizes = [5 if border else 2 for border in is_border]  # Larger size for border points

    # Unique labels and their corresponding colors
    unique_labels = list(set(labels))
    colors = plt.cm.get_cmap('viridis', len(unique_labels))

    # Create a color map from labels to colors
    color_map = {label: colors(i) for i, label in enumerate(unique_labels)}

    # Plotting
    fig, ax = plt.subplots()
    scatter = ax.scatter(x, y, c=[color_map[label] for label in labels], s=sizes, alpha=0.6)  # Use 's' for size

    # Create a legend with label colors
    legend_labels = {label: ax.plot([], [], marker="o", ls="", markersize=10, color=color_map[label])[0] for label in unique_labels}
    ax.legend(legend_labels.values(), legend_labels.keys(), title="Labels")

    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    plt.title('Random Mesh Points by Label')
    plt.axis('equal')  # Set equal scaling by changing axis limits
    plt.show()

def plot_borders_with_orientation(borders):
    plt.figure(figsize=(10, 8))
    
    for border in borders:
        final_p = border.end_point
        points = border.generate_points() + [MeshPoint(final_p[0],final_p[1])]
        x, y = zip(*[(p.x, p.y) for p in points])
        
        plt.plot(x, y, label=border.label)
        
        # Adding an arrow to show orientation
        # Selecting a point towards the middle of the border for the arrow
        mid_index = len(x) // 2
        plt.annotate('', xy=(x[mid_index + 1], y[mid_index + 1]), xytext=(x[mid_index], y[mid_index]),
                     arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8))
    
    plt.legend()
    plt.axis('equal')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Borders with Orientation')
    plt.show()
