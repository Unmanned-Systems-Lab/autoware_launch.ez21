cmake_minimum_required(VERSION 3.8)
project(gnss_antenna_description)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)

find_package(ament_cmake_auto REQUIRED)

ament_auto_find_build_dependencies()
ament_auto_package(INSTALL_TO_SHARE
    urdf
    mesh
)

install(DIRECTORY  mesh  urdf 
  DESTINATION share/${PROJECT_NAME}
)

