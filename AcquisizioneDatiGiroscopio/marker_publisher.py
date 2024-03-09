import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from tf2_ros import TransformBroadcaster
from tf2_geometry_msgs import TransformStamped
from visualization_msgs.msg import Marker
import csv
import math
from datetime import datetime

class PositionMarkerPublisher(Node):

    def __init__(self, file_path, pose_topic, marker_topic):
        super().__init__('position_marker_publisher')
        self.publisher_pose = self.create_publisher(PoseStamped, pose_topic, 10)
        self.publisher_marker = self.create_publisher(Marker, marker_topic, 10)
        self.broadcaster_ = TransformBroadcaster(self)
        timer_period = 0.2  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0
        self.file_path = file_path
        self.position_data = self.read_position_data()

    def read_position_data(self):
        try:
            with open(self.file_path, 'r') as file:
                lines = file.readlines()[1:]  # Skip the header line
                data = []
                for line in lines:
                    parts = line.split()
                    timestamp = parts[0] + ' ' + parts[1]
                    position_x = float(parts[2])
                    position_y = float(parts[3])
                    roll = float(parts[5])
                    pitch = float(parts[6])
                    yaw=float(parts[7])
                    data.append({'timestamp': timestamp, 'position_x': position_x, 'position_y': position_y,
                                 'roll': roll, 'pitch': pitch, 'yaw': yaw})
                return data
        except FileNotFoundError:
            self.get_logger().error(f"File not found: {self.file_path}")
            return []

    def timer_callback(self):
        if self.i < len(self.position_data):
            pose_msg = PoseStamped()

            # Convert timestamp to seconds and nanoseconds
            timestamp_str = self.position_data[self.i]['timestamp']
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")

            pose_msg.header.stamp.sec = int(timestamp.timestamp())
            pose_msg.header.stamp.nanosec = int((timestamp.microsecond % 1000000) * 1000)
            
            pose_msg.header.frame_id = "base_link"

            # Set position based on position data
            pose_msg.pose.position.x = float(self.position_data[self.i]['position_x'])
            pose_msg.pose.position.y = float(self.position_data[self.i]['position_y'])
            pose_msg.pose.position.z = 0.0

            # Set orientation based on angles
            quaternion = self.euler_to_quaternion(
                self.position_data[self.i]['roll'],
                self.position_data[self.i]['pitch'],
                self.position_data[self.i]['yaw']
                #0.0  # Assuming yaw is 0.0 since it's not available in the file
            )
            pose_msg.pose.orientation.x = quaternion[0]
            pose_msg.pose.orientation.y = quaternion[1]
            pose_msg.pose.orientation.z = quaternion[2]
            pose_msg.pose.orientation.w = quaternion[3]

            self.publisher_pose.publish(pose_msg)
            self.get_logger().info(f'Publishing Pose: "{pose_msg}"')

            # Publish static transform from base_link to imu
            self.publish_static_transform(pose_msg)

            # Publish position as marker
            self.publish_position_marker(pose_msg)

            self.i += 1
        else:
            self.get_logger().info('Finished publishing all position data.')

    def publish_position_marker(self, pose_msg):
        marker = Marker()
        marker.header.frame_id = "base_link"
        marker.header.stamp = pose_msg.header.stamp
        marker.type = Marker.SPHERE
        marker.action = Marker.ADD
        marker.pose.position.x = pose_msg.pose.position.x
        marker.pose.position.y = pose_msg.pose.position.y
        marker.pose.position.z = 0.0       
        marker.pose.orientation.x = pose_msg.pose.orientation.x
        marker.pose.orientation.y = pose_msg.pose.orientation.y   
        marker.pose.orientation.z = pose_msg.pose.orientation.z             
        #marker.pose.position.x=0.0
        
        #marker.pose.position.y=0.0
        #marker.pose.position.z=0.0
        marker.pose.orientation.w=0.0
        marker.scale.x = 0.01
        marker.scale.y = 0.01
        marker.scale.z = 0.01
        marker.color.a = 1.0
        marker.color.r = 1.0
        marker.color.g = 0.0
        marker.color.b = 0.0

        self.publisher_marker.publish(marker)

    def publish_static_transform(self, pose_msg):
        transform_stamped = TransformStamped()
        transform_stamped.header.stamp = pose_msg.header.stamp
        transform_stamped.header.frame_id = "base_link"
        transform_stamped.child_frame_id = "pose"

        # Use Vec3 for translation
        transform_stamped.transform.translation.x = pose_msg.pose.position.x
        transform_stamped.transform.translation.y = pose_msg.pose.position.y
        transform_stamped.transform.translation.z = pose_msg.pose.position.z

        # Use Quaternion for rotation
        transform_stamped.transform.rotation = pose_msg.pose.orientation

        self.broadcaster_.sendTransform(transform_stamped)

    def euler_to_quaternion(self, roll, pitch, yaw):
        #yaw = 0.0
        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)

        w = cy * cr * cp + sy * sr * sp
        x = cy * sr * cp - sy * cr * sp
        y = cy * cr * sp + sy * sr * cp
        z = sy * cr * cp - cy * sr * sp

        return [x, y, z, w]

def main(args=None):
    rclpy.init(args=args)
    file_path = 'datigriglia.txt'
    pose_topic = 'pose_data_topic'
    marker_topic = 'position_marker_topic'
    position_marker_publisher = PositionMarkerPublisher(file_path, pose_topic, marker_topic)

    try:
        rclpy.spin(position_marker_publisher)
    except KeyboardInterrupt:
        pass

    position_marker_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
