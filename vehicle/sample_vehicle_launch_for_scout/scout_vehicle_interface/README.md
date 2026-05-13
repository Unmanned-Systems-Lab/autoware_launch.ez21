## 文件位置
```
|--autoware_for_scout
  |--src
    |--vehicle
      |--external
        |--scout_vehicle_interface
        |--scout_base
        |--scout_description
        |--scout_msgs
        |--ugv_sdk
```
scout的CMakelists和package.xml有部分更改
***
## 编译
- autoware_for_scout源文件编译
- 单独编译 scout的三个文件和ugv_sdk
```bash
#在 /autoware_for_scout 处
colcon build --packages-up-to scout_base scout_description scout_msgs ugv_sdk
```
- 单独编译 scout_vehicle_interface
```bash
colcon build --packages-up-to scout_vehicle_interface
```
***
## 使用
- 可以直接启动通讯节点
```bash 
ros2 launch scout_vehicle_interface interface_v2.launch.py
```

- 整体上已经include到另外一个launch文件中（vehicle_interface.launch.xml）
- 另外需要启动scout的节点。

- Scout和通讯节点同步启动
```bash
ros2 launch scout_vehicle_interface interface_scout.launch.py
```

- 启动纯跟踪
```bash
 ros2 launch autoware_launch autoware.launch.xml map_path:=$HOME/autoware_map_test vehicle_model:=scout_vehicle sensor_model:=scout_sensor_kit lateral_controller_mode:=pure_pursuit
```
- MPC
```bash
ros2 launch autoware_launch autoware.launch.xml map_path:=$HOME/autoware_map_test vehicle_model:=scout_vehicle sensor_model:=scout_sensor_kit lateral_controller_mode:=mpc
```
- Simulation
```bash
ros2 launch autoware_launch planning_simulator.launch.xml map_path:=$HOME/autoware_map_test vehicle_model:=scout_vehicle sensor_model:=scout_sensor_kit lateral_controller_mode:=mpc
```

- 编译&指定编译
```bash
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release --packages-select scout_vehicle_interface
```
***
## CAN通讯自动挂载设置
当前版本由于Nvidia烧录的内核没有直接与CAN相连，故采用外接，使用RX TX的端口 进行CAN通讯。
编写使用的脚本：(根据需求修改这些参数)
```bash
sudo vim /home/[你的用户名]/CAN_scripts/CAN.sh
#你也可以使用gedit
```
脚本的内容：
```bash
#!/bin/bash
sudo busybox devmem 0x0c303000 32 0x0000C400
sudo busybox devmem 0x0c303008 32 0x0000C458
sudo busybox devmem 0x0c303010 32 0x0000C400
sudo busybox devmem 0x0c303018 32 0x0000C458
sudo modprobe can
sudo modprobe can_raw
sudo modprobe mttcan
sudo ip link set down can0
sudo ip link set can0 type can bitrate 500000
sudo ip link set up can0
```
编辑并保存后设置权限：
```bash
sudo chmod +x /home/[你的用户名]/CAN_scripts/CAN.sh
```
使用systemd服务
```bash
sudo vim /etc/systemd/system/CAN.service
#也可以使用gedit
```

在文档中编辑
```txt
[Unit]
Description=CAN service
 
[Service]
ExecStart=/home/[你的用户名]/CAN_scripts/CAN.sh
 
[Install]
WantedBy=multi-user.target
```

保存并关闭该文件，然后启动该服务并将其设置为开机自启：
```bash
sudo systemctl daemon-reload
 
sudo systemctl start CAN.service
 
sudo systemctl enable CAN.service
```

如果要检查状态：
```bash
sudo systemctl status CAN.service
```

如果要停止服务：
```bash
sudo systemctl stop CAN.service
 
sudo systemctl disable CAN.service
```
***
## 部分参数
 - autoware launch 文件： control 里横向控制调为pure_pursuit;
 - control-pid: delay compensation = 0.5, pid=2.0,0.3,0.1.
## 部分操作
 - unhealthy 出现时查不了原因则直接屏蔽
 - 地图名称需要在仿真和launch文件内设置
 - angles/angles/  nebula_decoder 加ros绝对路径
 - multi_object_tracker cmakelists 加ros绝对路径
 - 安装时每一个操作都不要放过。
## 说明
 - 20241122：适配v1.0的autoware文件。
 - 20241203: 初步测试完毕。需要在pid横向最高级控制中加大delay_compensation这个参数(目前是1)。
 - 20241220: 完成固定版本安装
