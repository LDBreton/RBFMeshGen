import numpy as np
from .geometry_utils import MeshPoint, Border, is_close, calculate_orientation,find_polygons
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
from shapely import prepare
import random



class RandomMesh:
    def __init__(self, *borders,abs_tol=1e-04):
        self.borders = borders
        self.Points = []
        self.Boundary_Points = []
        self.outer_polygons = []
        self.holes_polygons = []
        self.abs_tol=1e-04

    def generate_points(self, num_points):
        polygons, orientations = self.find_and_orient_polygons(self.abs_tol)

        # Generate points along borders and classify them
        polygons_with_points = []
        for polygon in polygons:
            polygon_points = []
            for border in polygon:
                border_point = border.generate_points()
                if border.is_border:
                   self.Boundary_Points.extend(border_point)
                polygon_points.extend([(p.x, p.y) for p in border_point])  # Add to polygon definition
            polygons_with_points.append(polygon_points)

        # Filter out the holes based on orientation
        outer_polygons = [Polygon(poly) for poly, orientation in zip(polygons_with_points, orientations) if orientation == 'CCW']
        hole_polygons = [Polygon(poly) for poly, orientation in zip(polygons_with_points, orientations) if orientation == 'CW']
        

        # Step 1: Exclude nested polygons
        outer_polygons = exclude_nested_polygons(outer_polygons)
        self.outer_polygons = outer_polygons
        self.holes_polygons = hole_polygons

        # Step 2: generate_regions
        region_poly = generate_regions(outer_polygons,hole_polygons)

        # Step 3: Calculate points allocation
        points_allocation = calculate_point_allocation(region_poly, num_points)

        # Step 4: Generate points
        self.Points.extend(generate_points_within_polygons(region_poly, points_allocation))

        return self.Points

    def find_and_orient_polygons(self,abs_tol=1e-6):
        polygons = find_polygons(self.borders,abs_tol)
        orientations = [calculate_orientation(polygon) for polygon in polygons]
        return polygons, orientations


def exclude_nested_polygons(outer_polygons):
    # Sort polygons by area in descending order to handle larger polygons first
    outer_polygons = sorted(outer_polygons, key=lambda p: abs(p.area), reverse=True)
    for i in range(len(outer_polygons)):
        for j in range(i + 1, len(outer_polygons)):
            if outer_polygons[i].contains(outer_polygons[j]):
                outer_polygons[i] = outer_polygons[i].difference(outer_polygons[j])
    return outer_polygons

def calculate_point_allocation(outer_polygons, num_points):
    total_area = sum(poly.area for poly in outer_polygons)
    return [int((poly.area / total_area) * num_points) for poly in outer_polygons]


def generate_regions(outer_polygons, hole_polygons):
    # Iterate over each outer polygon by index
    for i, poly in enumerate(outer_polygons):
        # Attempt to subtract each hole one by one
        for hole in hole_polygons:
            # Try subtracting the hole from the current polygon
            test_diff = poly.difference(hole)

            # Only update the polygon if the resulting polygon is valid and not empty
            if not test_diff.is_empty and test_diff.is_valid:
                poly = test_diff  # Update the poly to the newly modified polygon

        # Assign the modified or unmodified polygon back to the list
        outer_polygons[i] = poly

    return outer_polygons


def generate_points_within_polygons(outer_polygons, points_allocation,boundary_distance = 1.0e-5):
    points = []
    n_points = 0
    int_poly_lable = 10

    for poly, num_pts in zip(outer_polygons, points_allocation):
        poly = poly.buffer(-boundary_distance)
        prepare(poly)
        n_points += num_pts
        minx, miny, maxx, maxy = poly.bounds
        int_poly_lable += 1
        while len(points) < n_points:
            x = random.uniform(minx, maxx)
            y = random.uniform(miny, maxy)
            point = Point(x, y)
            if poly.contains_properly(point):
                points.append(MeshPoint(x, y, int_poly_lable, False))
    return points
