#!/usr/bin/env python

import rospy
import requests
import re
from actionlib import SimpleActionServer
from control_msgs.msg import JointTrajectoryAction, JointTrajectoryGoal, JointTrajectoryResult
from sensor_msgs.msg import JointState
from math import radians


class Robot001Manager(object):
    def __init__(self, ip_robot):
        self.ip_robot = ip_robot
        # pan tilt
        self.joint_states = [None, None]
        self.js_pub = rospy.Publisher('/joint_states',
                                      JointState,
                                      queue_size=5)
        self.as_ = SimpleActionServer('/robot_controller',
                                      JointTrajectoryAction,
                                      auto_start=False,
                                      execute_cb=self.goal_cb)
        self.as_.start()
        self.go_to_position(pan=0.0, tilt=0.0)
        rospy.Timer(rospy.Duration(0.02), self.js_pub_cb, oneshot=False)
        rospy.loginfo("We are started!")

    def js_pub_cb(self, params):
        js = JointState()
        js.header.stamp = rospy.Time.now()
        js.name = ['pan_joint', 'tilt_joint']
        if self.joint_states[0] is None:
            return
        js.position = self.joint_states
        self.js_pub.publish(js)

    def goal_cb(self, goal):
        #goal = JointTrajectoryGoal()
        rospy.loginfo("Goal: " + str(goal))
        pan_idx = goal.trajectory.joint_names.index('pan_joint')
        tilt_idx = goal.trajectory.joint_names.index('tilt_joint')
        for p in goal.trajectory.points:
            pan_pos = p.positions[pan_idx]
            tilt_pos = p.positions[tilt_idx]
            # self.go_to_position(pan=pan_pos, tilt=tilt_pos)
        self.as_.set_succeeded(JointTrajectoryResult())

    def go_to_position(self, pan, tilt):
        if pan >= 0.0:
            self.go_to_right(pan)
        elif pan < 0.0:
            self.go_to_left(pan)

        if tilt >= 0.0:
            self.go_to_up(tilt)
        elif tilt < 0.0:
            self.go_to_down(tilt)

    def update_joints(self, ret_text):
        result_d = re.search("Down=((\d+)\.(\d+))", ret_text)
        result_r = re.search("Right=((\d+)\.(\d+))", ret_text)
        try:
            pan = float(result_r.groups()[0])
            tilt = float(result_d.groups()[0])
            self.joint_states = [radians(pan), radians(tilt)]
        except AttributeError as e:
            rospy.logwarn("Attribute error when parsing: " + str(e))
            #self.go_to_position(pan=0.0, tilt=0.0)

    def go_to_left(self, qtty):
        if qtty < 0.0:
            qtty = qtty * -1.0
        r = requests.get('http://' + self.ip_robot +
                         '?l=' + str(int(qtty)))
        self.update_joints(r.text)

    def go_to_right(self, qtty):
        if qtty < 0.0:
            qtty = qtty * -1.0
        r = requests.get('http://' + self.ip_robot +
                         '?r=' + str(int(qtty)))
        self.update_joints(r.text)

    def go_to_up(self, qtty):
        if qtty < 0.0:
            qtty = qtty * -1.0
        r = requests.get('http://' + self.ip_robot +
                         '?u=' + str(int(qtty)))
        self.update_joints(r.text)

    def go_to_down(self, qtty):
        if qtty < 0.0:
            qtty = qtty * -1.0
        r = requests.get('http://' + self.ip_robot +
                         '?d=' + str(int(qtty)))
        self.update_joints(r.text)

if __name__ == '__main__':
    rospy.init_node('robot001_node')
    r = Robot001Manager("192.168.0.16")
    rospy.spin()

    # r.go_to_position(pan=30.0, tilt=0.0)
    # r.go_to_position(pan=-30.0, tilt=0.0)
    # r.go_to_position(pan=0.0, tilt=50.0)
    # r.go_to_position(pan=0.0, tilt=-60.0)

    # r = requests.get('http://192.168.0.16/?l=3')
    # print "Response was: " + str(r)
    # print r.text

    # TODO: Up, Left, Right, Down=X.XX for position
    # We should parse it
