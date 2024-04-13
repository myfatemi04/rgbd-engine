# RGBD Camera API

Author: Michael Fatemi

The RGBD Camera API provides functionality for working with RGBD (Red, Green, Blue, Depth) cameras, specifically designed for use with Azure Kinect cameras (K4A) and AprilTags for camera calibration.

## Installation

To install the RGBD Camera API, clone the repository and install the required dependencies using pip:

```bash
git clone https://github.com/myfatemi04/rgbd-engine.git
cd repository
pip install -r requirements.txt
```

## Usage

### 1. Camera Calibration

The API supports camera calibration using AprilTags. Use the `try_calibrate` method of the `RGBD` class to calibrate a camera:

```python
rgbd = RGBD()
rgbd.try_calibrate(camera_index, color_image)
```

### 2. Capturing RGBD Images

To capture RGBD images using the connected cameras, use the `capture` method of the `RGBD` class:

```python
color_images, point_clouds = rgbd.capture()
```

If a camera has not been calibrated, its corresponding `point_clouds[i]` will be `None`. Note that some RGBD pixels are "undefined" in the sense that the depth camera returned a depth of "0". These points are represented in `point_clouds` as the point `[-10000, -10000, -10000]`, because the point `[0, 0, 0]` is a valid point in robot frame.

### 3. Surface Normal Calculation

You can calculate surface normals from a point cloud image using the `get_normal_map` function:

```python
normal_map = get_normal_map(point_cloud_image)
surface_normal = normal_map[y, x]
```

The normal map consists of unit vectors. For pixel locations without a neighborhood of valid depth measurements, the normal map assigns a value of `[0, 0, 0]`.

### 4. Triangulation

The API supports triangulation of points between two calibrated cameras:

```python
triangulated_points = triangulate(camera1, camera2, camera1_positions, camera2_positions)
```

### 5. Exporting and Importing Calibration

This is currently not accessible from the `RGBD` class.

You can export the calibration parameters of a camera using the `export_calibration` method:

```python
calibration_data = camera.export_calibration()
```

And import calibration parameters using the `import_calibration` method:

```python
camera.import_calibration(calibration_data)
```

### 6. Closing Cameras

To close the cameras and release resources, use the `close` method of the `RGBD` class:

```python
rgbd.close()
```

## Dependencies

- OpenCV
- pyk4a
- apriltag
- numpy

## License

This API is released under the MIT License. See the LICENSE file for more details.

