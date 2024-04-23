import numpy as np
import random
from shapely import Point, Polygon, LineString, prepare


import matplotlib.pyplot as plt

class MeshPoint:
    def __init__(self, x, y, label = 0, is_border = True):
        self.x = x
        self.y = y
        self.label = label
        self.is_border = is_border
        
class Border:
    def __init__(self, parametric_function, label, t_start, t_end, is_border=True):
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
        mid_t = (self.t_start + self.t_end) / 2
        return self.parametric_function(mid_t)

    def generate_points(self):
        t_values = np.linspace(self.t_start, self.t_end, abs(self.n_segments) + 1, endpoint=True)
        points = [MeshPoint(x, y, self.label, self.is_border) for x, y in [self.parametric_function(t) for t in t_values]]
        return points[:-1] if not self.reverse else points[::-1][:-1]     
        
def find_next_border(current_end, remaining_borders,abs_tol=1e-6):
  first_candidate = None
  found_multiple = False

  for border in remaining_borders:
      if is_close(border.start_point, current_end,abs_tol):
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
    distance = np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    return distance < tolerance


def find_polygons(borders,tolerance=1e-6):
    standalone_polygons = []
    polygon_groups = []
    open_borders = []

    # Separate standalone polygons and open borders
    for border in borders:
        if is_close(border.start_point,border.end_point,tolerance):
            standalone_polygons.append([border])
        else:
            open_borders.append(border)


    # Form polygons from connected borders
    while open_borders:
        current = open_borders.pop(0)
        polygon = [current]
        found_multiple, next_border = find_next_border(current.end_point, open_borders,tolerance)
        if found_multiple: open_borders.append(current)

        while next_border:
            current = next_border
            open_borders.remove(current)
            polygon.append(current)
            found_multiple, next_border = find_next_border(current.end_point, open_borders,tolerance)
            if found_multiple: open_borders.append(current)
  
            # Close the loop if it connects back to the start
            if next_border and is_close(next_border.end_point,polygon[0].start_point,tolerance):
                polygon.append(next_border)
                #open_borders.remove(next_border)
                break

        if is_close(polygon[0].start_point,polygon[-1].end_point,tolerance):
            polygon_groups.append(polygon)

    return standalone_polygons + polygon_groups


def calculate_orientation(list_border):
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
