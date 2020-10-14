#!/usr/bin/env python
# coding=utf-8
# Copyright (c) 2020 kedacom
# OpenATC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
# http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

# @file    config.py
# @author  harry
# @date    2020.9.7

"""
一些配置参数
"""

# SUMO相关配置
sumocfg = ''  # SUMO配置文件
steplength = 0  # 仿真步长 s
sumoterminals = "3"
cinductionloopid = ''  # 路网中心检测器id, 用于订阅检测器数据
radius = 0  # 订阅范围半径

# 接收信号灯数据的UDP端口
tlsport = 0

#######################################################
# 仿真路网相关信息
# 仅在.net.xml及.det.xml文件 改变时重新生成
######################################################
junctions = list()
# 路口及其包含车道id
junction_lanes = dict()
# 路口及其包含检测器id
junction_detectors = dict()

######################################################
# 仿真路口关联设备信息、通道配置
# sumo初始化时从 sumo\devices.csv 读入生成
######################################################
devices = dict()
devices2junction = dict()
addrs = dict()
junction_channels = dict()
channelsList = dict()
junction_linknum = dict()
junction_groupnum = dict()
