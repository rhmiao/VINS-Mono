#!/usr/bin/env python
# coding=utf-8

import sys, os, time
import rospy
import copy
from nav_msgs.msg import Odometry
from zmq_comm import *
from zmq_cfg import *
import threading

class vio_c(threading.Thread):
    def __init__(self):
        print('[TRK] vio_c.__init__()')
        threading.Thread.__init__(self)
        # 缺省配置
        self.init_pos=[0,0,0]
        self.pos_now=[0,0,0]
        self.quan_now = [0, 0, 0, 0]
        # 状态复位

        rospy.init_node('vio', anonymous=False)
        rospy.Subscriber('/vins_estimator/camera_pose', Odometry, self.vioCallback)

    def reset(self, param = None):
        rospy.init_node('vio', anonymous=False)
        rospy.Subscriber('/vins_estimator/camera_pose', Odometry, self.vioCallback)
        self.init_pos[0] = self.pos_now[0]
        self.init_pos[1] = self.pos_now[1]
        self.init_pos[2] = self.pos_now[2]

    def config(self, param):
        pass

    def get_result(self, param='dis'):
        pos_del = [0, 0, 0]
        if(param == 'dis'):
            pos_del[0] = self.pos_now[0] - self.init_pos[0]
            pos_del[1] = self.pos_now[1] - self.init_pos[1]
            pos_del[2] = self.pos_now[2] - self.init_pos[2]
            return pos_del
        if(param == 'dir'):
            return self.quan_now

    def vioCallback(self,data):
        self.pos_now[0] = data.pose.pose.position.x
        self.pos_now[1] = data.pose.pose.position.y
        self.pos_now[2] = data.pose.pose.position.z
        self.quan_now[0] = data.pose.pose.orientation.w
        self.quan_now[1] = data.pose.pose.orientation.x
        self.quan_now[2] = data.pose.pose.orientation.y
        self.quan_now[3] = data.pose.pose.orientation.z

    def execute(self, param=None):
        pass

    def stop(self):
        rospy.signal_shutdown("stop")

    def run(self):
        rospy.spin()


class zmq_vio_c(zmq_comm_svr_c):
    def __init__(self, name=name_vio, ip=ip_vio, port=port_vio):
        print('[TRK] zmq_positioning_c.__init__()')
        zmq_comm_svr_c.__init__(self, name, ip, port)  # 通信代理
        self.vio_eng = vio_c()  # vio引擎对象
        self.vio_eng.start()  # start ros thread
        return

    ## 远程调用的API
    def reset(self, param=None):
        print('[TRK] zmq_vio_c.reset()')
        return self.vio_eng.reset(param)

    def config(self, param=None):
        print('[TRK] zmq_vio_c.config()')
        return self.vio_eng.config(param)

    def query(self, param=None):
        print('[TRK] zmq_vio_c.query()')
        return self.vio_eng.query(param)

    def get_result(self, param=None):
        print('[TRK] zmq_vio_c.get_result()')
        return self.vio_eng.get_result(param)

    def execute(self, param=None):
        print('[TRK] zmq_vio_c.execute()')
        return self.vio_eng.execute(param)

if __name__ == '__main__':

    # 启动API调用的服务线程
    remote_vio_engine = zmq_vio_c()
    remote_vio_engine.start()