from typing import Optional

import cv2
import numpy as np
import pyk4a


class Camera:
    def __init__(self, k4a: pyk4a.PyK4A):
        self.k4a = k4a
        # Camera parameters
        self.rvec_tvec = None
        self.extrinsic_matrix = None
        self.intrinsic_matrix = k4a.calibration.get_camera_matrix(pyk4a.CalibrationType.COLOR)
        self.distortion_coefficients = k4a.calibration.get_distortion_coefficients(pyk4a.CalibrationType.COLOR)
        self.original_calibration = True
        self.prev_capture: Optional[pyk4a.PyK4ACapture] = None

    def capture(self):
        self.prev_capture = self.k4a.get_capture()
        return self.prev_capture

    def infer_extrinsics(self, apriltag_points, apriltag_object_points):
        ret, rvec, tvec = cv2.solvePnP(apriltag_object_points, apriltag_points, self.intrinsic_matrix, self.distortion_coefficients)
        rotation_matrix, _ = cv2.Rodrigues(rvec)
        translation = tvec
        extrinsics = np.concatenate((rotation_matrix, translation), axis=1)

        self.rvec_tvec = (rvec, tvec)
        self.extrinsic_matrix = extrinsics

    def project_points(self, object_points):
        assert (self.extrinsic_matrix is not None) and (self.rvec_tvec is not None), "Camera extrinsic matrix has not been calibrated."
        
        rvec, tvec = self.rvec_tvec
        points, _jacobian = cv2.projectPoints(object_points, rvec, tvec, self.intrinsic_matrix, self.distortion_coefficients)
        points = points[:, 0, :]

        return points
    
    def undistort(self, image_points):
        # Note: This undoes the intrinsic matrix as well
        return cv2.undistortPoints(image_points.astype(np.float32), self.intrinsic_matrix, self.distortion_coefficients)
    
    # Useful for tasks where the AprilTag starts off occluded.
    def export_calibration(self):
        return {
            'rvec_tvec': self.rvec_tvec,
            'extrinsic_matrix': self.extrinsic_matrix,
            'intrinsic_matrix': self.intrinsic_matrix,
            'distortion_coefficients': self.distortion_coefficients,
        }

    def import_calibration(self, calibration):
        self.rvec_tvec = calibration.get('rvec_tvec', None)
        self.extrinsic_matrix = calibration.get('extrinsic_matrix', None)
        self.intrinsic_matrix = calibration.get('intrinsic_matrix', None)
        self.distortion_coefficients = calibration.get('distortion_coefficients', None)
        self.original_calibration = False

    def transform_sensed_points_to_robot_frame(self, pcd_xyz):
        """
        Transforms point clouds (can be Nx3 or HxWx3) from camera frame
        into robot frame, using the calibration created by the Apriltag.

        Returns None if the camera has not been calibrated yet.
        """
        if self.extrinsic_matrix is None:
            return None

        translation = self.extrinsic_matrix[[0, 1, 2], 3]
        rotation = self.extrinsic_matrix[:3, :3]

        # Flatten
        shape = pcd_xyz.shape
        pcd_xyz = pcd_xyz.reshape(-1, 3)

        # we change units from mm to meters
        pcd_xyz = pcd_xyz / 1000
        # untranslate and unrotate
        pcd_xyz = (rotation.T @ (pcd_xyz - translation).T).T

        # Unflatten
        pcd_xyz = pcd_xyz.reshape(*shape)

        return pcd_xyz

    def close(self):
        self.k4a.close()

def triangulate(camera1: Camera, camera2: Camera, camera1_positions: np.ndarray, camera2_positions: np.ndarray):
    assert camera1.extrinsic_matrix is not None, "Camera 1 extrinsic matrix has not been calibrated."
    assert camera2.extrinsic_matrix is not None, "Camera 2 extrinsic matrix has not been calibrated."
    camera1_undistorted = camera1.undistort(camera1_positions)
    camera2_undistorted = camera2.undistort(camera2_positions)
    # `undistort` undoes the intrinsic matrix
    # therefore here, you must pretend that the intrinsic matrix is the identity
    # the *_extrinsic_matrix parameters are supposed to be camera matrices (i.e. intrinsic @ extrinsic)
    # but we just use extrinsic to pretend that the intrinsic matrix is the identity
    # Shape: [4, n]
    # i.e., [{x, y, z, homogenous}, n]
    triangulated_homogenous = cv2.triangulatePoints(camera1.extrinsic_matrix, camera2.extrinsic_matrix, camera1_undistorted, camera2_undistorted)
    triangulated_homogenous = triangulated_homogenous.T
    # Divide xyz by homogenous points
    triangulated = triangulated_homogenous[:, :3] / triangulated_homogenous[:, -1]
    return triangulated
