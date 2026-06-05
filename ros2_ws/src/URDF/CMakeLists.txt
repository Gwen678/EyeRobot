cmake_minimum_required(VERSION 3.8)
project(robot_description)

find_package(ament_cmake REQUIRED)

# Install the description so $(find Robot_description) and package:// URIs
# resolve at runtime (xacro includes, mesh references in RViz).
install(
  DIRECTORY urdf meshes
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
