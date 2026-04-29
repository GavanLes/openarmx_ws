# OpenArmX Bringup 与 Hardware 文档说明

## 1. 文档目标
本文用于说明两个核心包的职责分工与协作关系：
- `openarmx_bringup`
- `openarmx_hardware`

可作为系统讲解、培训和二次开发的入门材料。

## 2. 总体分层
在 OpenArmX ROS 2 架构中，这两个包分别处于不同层级：
- `openarmx_bringup`：启动与控制器编排层
- `openarmx_hardware`：底层硬件接口层（ros2_control hardware plugin）

一句话理解：
- Bringup 负责“把系统按正确模式启动并连接起来”
- Hardware 负责“把控制命令真正发到电机，并回读状态”

## 3. openarmx_bringup 作用
`openarmx_bringup` 主要做系统启动、控制器选择、参数透传、接口组织。

### 3.1 核心职责
1. 启动 `ros2_control_node`（controller_manager）
2. 按参数选择并拉起控制器（trajectory 或 forward）
3. 配置双臂/夹爪控制器及命名空间版本
4. 管理运行参数（CAN 口、MIT/CSP、fake hardware 等）
5. 提供统一的控制话题与动作接口约定

### 3.2 关键文件
- `openarmx_bringup/launch/openarmx.bimanual.launch.py`
  - 总入口 launch
  - 启动 `robot_state_publisher` 与 `controller_manager`
  - 根据 `robot_controller` 启动左右控制器
- `openarmx_bringup/config/v10_controllers/openarmx_v10_bimanual_controllers.yaml`
  - 双臂控制器配置（非命名空间）
- `openarmx_bringup/config/v10_controllers/openarmx_v10_bimanual_controllers_namespaced.yaml`
  - 双臂控制器配置（命名空间）

### 3.3 控制模式示意
- `joint_trajectory_controller`
  - 面向 MoveIt 轨迹执行（Action）
- `forward_position_controller`
  - 面向实时位置指令（Topic `/left_forward_position_controller/commands` 等）

## 4. openarmx_hardware 作用
`openarmx_hardware` 是 `ros2_control` 的 `SystemInterface` 插件实现，负责真实硬件通信。

### 4.1 核心职责
1. 导出状态接口（position/velocity/effort）
2. 导出命令接口（position/velocity/effort）
3. 在 `read()` 中读取电机状态并更新 ROS 侧状态
4. 在 `write()` 中把控制命令转换为底层电机命令并发送
5. 支持 MIT/CSP 两种控制模式

### 4.2 关键文件
- `openarmx_hardware/openarmx_hardware.xml`
  - 插件注册：`openarmx_hardware/OpenArmX_v10HW`
- `openarmx_hardware/include/openarmx_hardware/v10_simple_hardware.hpp`
  - 硬件类声明与参数定义
- `openarmx_hardware/src/v10_simple_hardware.cpp`
  - 生命周期、read/write、接口导出、CAN 下发实现

## 5. 两个包如何协作
### 5.1 运行链路（forward_position_controller 场景）
1. 外部节点发布 `/left_forward_position_controller/commands`
2. forward 控制器接收目标值并写入 command interface
3. `openarmx_hardware` 在 `write()` 读取 command interface
4. 按 MIT 或 CSP 协议通过 CAN 下发到电机

### 5.2 关键边界
- 在 ROS 图中你能看到 topic 到 controller
- controller 到 hardware 的调用属于 ros2_control 内部机制，通常不会以普通 topic 显示

## 6. 开发与排障建议
1. 改启动行为、切控制器、改接口映射：优先看 `openarmx_bringup`
2. 改电机参数、CAN 下发、状态读取：优先看 `openarmx_hardware`
3. 先确认控制器已激活，再查硬件 `write()` 是否执行
4. MIT/CSP 行为不同，问题定位时先确认 `control_mode`

## 7. 常用命令
```bash
# 启动双臂（默认）
ros2 launch openarmx_bringup openarmx.bimanual.launch.py

# 查看控制器状态
ros2 control list_controllers

# forward 模式下发送左臂位置命令
ros2 topic pub /left_forward_position_controller/commands \
  std_msgs/msg/Float64MultiArray \
  "data: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.02]" --once
```

## 8. 与 MoveIt 的关系
- `openarmx_bringup` + `openarmx_hardware` 负责控制执行链路
- MoveIt 包（`openarmx_bimanual_moveit_config`）负责规划层
- 常见流程：MoveIt 规划轨迹 -> trajectory controller -> hardware write -> 电机执行

