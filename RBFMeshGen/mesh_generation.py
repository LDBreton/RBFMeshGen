from .geometry_utils import MeshPoint, calculate_orientation, find_polygons, Border
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
from shapely import prepare
import random


class RBFMesh:
    """
    RBFMesh class for generating random points within polygons.

    Args:
        *borders: Variable length argument list of Border objects representing the borders of the polygons.
        abs_tol (float, optional): Absolute tolerance for geometric calculations. Defaults to 1e-04.

    Attributes:
        borders (list): List of Border objects representing the borders of the polygons.
        Points (list): List of generated MeshPoint objects.
        Boundary_Points (list): List of generated MeshPoint objects on the boundary.
        outer_polygons (list): List of outer Polygon objects.
        holes_polygons (list): List of hole Polygon objects.
        abs_tol (float): Absolute tolerance for geometric calculations.
    Methods:
        generate_points(num_points): Generates random points within the polygons.

        find_and_orient_polygons(abs_tol): Finds and calculate the orientation of the polygons for the given borders.
    """

    def __init__(self, *borders: Border, abs_tol=1e-04):
        self.borders = list(borders)
        self.Points = []
        self.Boundary_Points = []
        self.outer_polygons = []
        self.holes_polygons = []
        self.region_polygons = []
        self.abs_tol = abs_tol
        self.process_polygons()  # Process polygons during initialization

    def process_polygons(self):
        """
        Processes polygons to prepare them for point generation by classifying
        them into outer polygons and holes, and then refining them to ensure
        that they are properly nested and non-overlapping. This method sets up
        the initial geometric configuration by finding polygons based on the
        provided borders, classifying them based on orientation, and generating
        points along these borders.

        The method performs several key operations:
        1. Identifies and orients polygons based on the input borders, distinguishing
           between counter-clockwise (outer polygons) and clockwise (holes).
        2. Generates points along each border and collects these points, noting
           which are on boundary borders.
        3. Excludes nested polygons to simplify the outer boundary definitions.
        4. Subtracts hole polygons from outer polygons to finalize distinct regions.
        5. Creates a unified region from these polygons to filter boundary points
           accurately based on their proximity to the actual boundary.

        Modifies:
            self.outer_polygons: List of shapely.geometry.Polygon objects representing the outer boundaries.
            self.holes_polygons: List of shapely.geometry.Polygon objects representing the holes.
            self.region_polygons: List of shapely.geometry.Polygon objects representing the final regions
                                  after subtraction of holes from the outer polygons.
            self.Boundary_Points: List of MeshPoint objects that are confirmed to be on the boundary of the
                                  unified region, adjusted by the absolute tolerance.

        This setup is crucial for ensuring that the subsequent point generation by `generate_points`
        occurs within properly defined and non-overlapping geometric regions.
        """
        polygons, orientations = self.find_and_orient_polygons(self.abs_tol)

        # Generate points along borders and classify them
        polygons_with_points = []
        tentative_boundary_points = []

        for polygon in polygons:
            polygon_points = []
            for border in polygon:
                border_point = border.generate_points()
                if border.is_border:
                    tentative_boundary_points.extend(border_point)
                polygon_points.extend([(p.x, p.y) for p in border_point])  # Add to polygon definition
            polygons_with_points.append(polygon_points)

        # Filter out the holes based on orientation
        outer_polygons = [Polygon(poly) for poly, orientation in zip(polygons_with_points, orientations) if
                          orientation == 'CCW']
        self.holes_polygons = [Polygon(poly) for poly, orientation in zip(polygons_with_points, orientations) if
                               orientation == 'CW']

        # Step 1: Exclude nested polygons
        self.outer_polygons = exclude_nested_polygons(outer_polygons)
        self.outer_polygons = self.outer_polygons

        # Step 2: generate_regions
        self.region_polygons = generate_regions(self.outer_polygons, self.holes_polygons)

        # Unify the regions for boundary check
        unified_region = unary_union([p.buffer(0) for p in self.region_polygons])

        # Filter boundary points that are actually on the boundary of the unified region
        boundary_line = unified_region.boundary
        self.Boundary_Points = [p for p in tentative_boundary_points if
                                boundary_line.distance(Point(p.x, p.y)) < self.abs_tol]

    def generate_points(self, num_points, boundary_distance=1.0e-5):
        """-
        Generates random points within the polygons defined by the borders.

        Args:
            boundary_distance:  distance from generated point to the boundary
            num_points (int): Number of points to generate.

        Returns:
            list: List of generated MeshPoint objects.
        """
        # Step 1: Calculate points allocation
        points_allocation = calculate_point_allocation(self.region_polygons, num_points)

        # Step 2: Generate points
        self.Points.extend(generate_points_within_polygons(self.region_polygons, points_allocation, boundary_distance))

        return self.Points

    def find_and_orient_polygons(self, abs_tol=1e-6):
        """
        Finds and calculates the orientation of the polygons for the given borders.

        Args:
            abs_tol (float, optional): Absolute tolerance for geometric calculations. Defaults to 1e-6.

        Returns:
            tuple: Tuple containing the list of polygons and their orientations.
        """
        polygons = find_polygons(self.borders, abs_tol)
        orientations = [calculate_orientation(polygon) for polygon in polygons]
        return polygons, orientations


def exclude_nested_polygons(outer_polygons):
    """
    refactor the nested polygons into disjoint polygons.

    Args:
        outer_polygons (list): List of outer Polygon objects.

    Returns:
        list: List of outer Polygon objects with nested polygons excluded.
    """
    # Sort polygons by area in descending order to handle larger polygons first
    outer_polygons = sorted(outer_polygons, key=lambda p: abs(p.area), reverse=True)
    for i in range(len(outer_polygons)):
        for j in range(i + 1, len(outer_polygons)):
            if outer_polygons[i].contains(outer_polygons[j]):
                outer_polygons[i] = outer_polygons[i].difference(outer_polygons[j])
    return outer_polygons


def calculate_point_allocation(region_polygons, num_points):
    """
    Calculates the point allocation for each region_polygons based on their area.

    Args:
        region_polygons (list): List of outer Polygon objects.
        num_points (int): Number of points to allocate.

    Returns:
        list: List of integers representing the point allocation for each outer polygon.
    """
    total_area = sum(poly.area for poly in region_polygons)
    return [int((poly.area / total_area) * num_points) for poly in region_polygons]


def generate_regions(outer_polygons, hole_polygons):
    """
    Generates the regions by subtracting hole polygons from outer polygons.

    Args:
        outer_polygons (list): List of outer Polygon objects.
        hole_polygons (list): List of hole Polygon objects.

    Returns:
        list: List of modified outer Polygon objects.
    """
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


def generate_points_within_polygons(region_polygons, points_allocation, boundary_distance=1.0e-5):
    """
    Generates random points within the outer polygons.

    Args:
        region_polygons (list): List of outer Polygon objects.
        points_allocation (list): List of integers representing the point allocation for each outer polygon.
        boundary_distance (float, optional): Distance to buffer the polygons. Defaults to 1.0e-5.

    Returns:
        list: List of generated MeshPoint objects.
    """
    points = []
    total_points_generated = 0

    for i, (poly, num_pts) in enumerate(zip(region_polygons, points_allocation)):
        poly = poly.buffer(-boundary_distance)  # Apply a buffer to slightly shrink the polygon
        prepare(poly)  # Optional: prepare the polygon for faster operations if supported
        target_points_count = total_points_generated + num_pts
        min_x, min_y, max_x, max_y = poly.bounds

        while len(points) < target_points_count:
            x = random.uniform(min_x, max_x)
            y = random.uniform(min_y, max_y)
            point = Point(x, y)
            if poly.contains_properly(point):
                points.append(MeshPoint(x, y, f'region {i + 1}', False))

        total_points_generated += num_pts

    return points
