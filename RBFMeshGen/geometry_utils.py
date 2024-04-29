import numpy as np


class MeshPoint:
    def __init__(self, x: float, y: float, label=0, is_border=True):
        """
        Represents a point in the mesh.

        Args:
            x (float): The x-coordinate of the point.
            y (float): The y-coordinate of the point.
            label (int or string, optional): The label of the point. Defaults to 0.
            is_border (bool, optional): Indicates if the point is on the border. Defaults to True.
        """
        self.x = x
        self.y = y
        self.label = label
        self.is_border = is_border


class Border:
    def __init__(self, parametric_function, label, t_start, t_end, is_border=True):
        """
        Represents a border in the mesh.

        Args:
            parametric_function (function): The parametric function that defines the border.
            label (str or int): The label of the border.
            t_start (float): The start parameter value of the border.
            t_end (float): The end parameter value of the border.
            is_border (bool, optional): Indicates if the border is a boundary. Defaults to True.
        """
        self.parametric_function = parametric_function
        self.label = label
        self.t_start = t_start
        self.t_end = t_end
        # Calculate start and end points using the parametric function
        self.start_point = parametric_function(t_start)
        self.end_point = parametric_function(t_end)
        self.is_border = is_border
        self.n_segments = None
        self.reverse = False  # Attribute to control direction

    def __call__(self, n):
        """
        Sets the number of segments for the border.

        Args:
            n (int): The number of segments.

        Returns:
            Border: The updated Border object.
        """
        self.n_segments = n
        self.reverse = n < 0  # Set reverse flag based on the sign of n
        # Reverse start and end if n is negative
        if self.reverse:
            self.start_point = self.parametric_function(self.t_end)
            self.end_point = self.parametric_function(self.t_start)
        else:
            self.start_point = self.parametric_function(self.t_start)
            self.end_point = self.parametric_function(self.t_end)
        return self

    def get_midpoint(self):
        """
        Calculates the midpoint of the border.

        Returns:
            tuple: The coordinates of the midpoint.
        """
        mid_t = (self.t_start + self.t_end) / 2
        return self.parametric_function(mid_t)

    def generate_points(self):
        """
        Generates mesh points along the border.

        Returns:
            list: A list of MeshPoint objects representing the generated points.
        """
        t_values = np.linspace(self.t_start, self.t_end, abs(self.n_segments) + 1, endpoint=True)
        points = [
            MeshPoint(x, y, self.label, self.is_border)
            for x, y in [self.parametric_function(t) for t in t_values]
        ]
        return points[:-1] if not self.reverse else points[::-1][:-1]


def find_next_border(current_end, remaining_borders, abs_tol=1e-6):
    """
    Finds the next border connected to the current end point.

    Args:
        current_end (tuple): The coordinates of the current end point.
        remaining_borders (list): A list of Border objects representing the remaining borders.
        abs_tol (float, optional): The absolute tolerance for distance comparison. Defaults to 1e-6.

    Returns:
        tuple: A tuple containing a boolean indicating if multiple candidates were found and the first candidate border.
    """
    first_candidate = None
    found_multiple = False

    for border in remaining_borders:
        if is_close(border.start_point, current_end, abs_tol):
            if first_candidate is None:
                first_candidate = border
            else:
                # As soon as a second candidate is found, stop checking further
                found_multiple = True
                break

    if first_candidate:
        return found_multiple, first_candidate
    else:
        return found_multiple, None


def is_close(point1, point2, tolerance=1e-6):
    """
    Checks if two points are close to each other within a given tolerance.

    Args:
        point1 (tuple): The coordinates of the first point.
        point2 (tuple): The coordinates of the second point.
        tolerance (float, optional): The tolerance for distance comparison. Defaults to 1e-6.

    Returns:
        bool: True if the points are close, False otherwise.
    """
    distance = np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    return distance < tolerance


def find_polygons(borders: list[Border], tolerance=1e-6):
    """
    Finds polygons formed by connected borders.

    Args:
        borders (list[Border]): A list of Border objects representing the borders.
        tolerance (float, optional): The tolerance for distance comparison. Defaults to 1e-6.

    Returns:
        list: A list of lists, where each inner list represents a group of connected borders forming a polygon.
    """
    standalone_polygons = []
    polygon_groups = []
    open_borders = []

    # Separate standalone polygons and open borders
    for border in borders:
        if is_close(border.start_point, border.end_point, tolerance):
            standalone_polygons.append([border])
        else:
            open_borders.append(border)

    # Form polygons from connected borders
    while open_borders:
        current = open_borders.pop(0)
        polygon = [current]
        found_multiple, next_border = find_next_border(current.end_point, open_borders, tolerance)
        if found_multiple:
            open_borders.append(current)
        while next_border:
            current = next_border
            open_borders.remove(current)
            polygon.append(current)
            found_multiple, next_border = find_next_border(current.end_point, open_borders, tolerance)
            if found_multiple:
                open_borders.append(current)
            # Close the loop if it connects back to the start
            if next_border and is_close(next_border.end_point, polygon[0].start_point, tolerance):
                polygon.append(next_border)
                break

        if is_close(polygon[0].start_point, polygon[-1].end_point, tolerance):
            polygon_groups.append(polygon)

    return standalone_polygons + polygon_groups


def calculate_orientation(list_border):
    """
    Calculates the orientation of a list of borders that are assume to form a polygon.

    Args:
        list_border (list): A list of Border objects representing the borders.

    Returns:
        str: The orientation of the borders, either 'CCW' (counter-clockwise) or 'CW' (clockwise).
    """
    total_area = 0
    for border in list_border:
        start_point = border.start_point
        midpoint = border.get_midpoint()
        end_point = border.end_point
        points = [start_point, midpoint, end_point]

        # Calculate area using the shoelace formula
        for i in range(len(points)-1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            total_area += (x1 * y2 - y1 * x2)
    return 'CCW' if total_area / 2.0 > 0 else 'CW'
