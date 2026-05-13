cmake_minimum_required(VERSION 3.8)
project(scout_vehicle_interface)

find_package(ament_cmake_auto REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(autoware_vehicle_msgs REQUIRED)
find_package(autoware_control_msgs REQUIRED)
find_package(tier4_vehicle_msgs REQUIRED)
find_package(scout_msgs REQUIRED)

ament_auto_find_build_dependencies()

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
  set(CMAKE_CXX_STANDARD_REQUIRED ON)
  set(CMAKE_CXX_EXTENSIONS OFF)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

include_directories(
  include
)

add_executable(autoware_to_scout src/autoware_to_scout.cpp)
ament_target_dependencies(autoware_to_scout
rclcpp
autoware_control_msgs
geometry_msgs
std_msgs )

add_executable(scout_to_autoware src/scout_to_autoware.cpp)
ament_target_dependencies(scout_to_autoware
rclcpp
autoware_vehicle_msgs
tier4_vehicle_msgs
scout_msgs
geometry_msgs )

install(TARGETS
scout_to_autoware
autoware_to_scout
DESTINATION lib/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()

endif()

ament_auto_package(
  INSTALL_TO_SHARE
  launch
)
