# CMake generated Testfile for 
# Source directory: /ros2_ws/src/rosapi
# Build directory: /ros2_ws/build/rosapi
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(rosapi_test_stringify_field_types "/usr/bin/python3" "-u" "/opt/ros/foxy/install/share/ament_cmake_test/cmake/run_test.py" "/ros2_ws/build/rosapi/test_results/rosapi/rosapi_test_stringify_field_types.xunit.xml" "--package-name" "rosapi" "--output-file" "/ros2_ws/build/rosapi/ament_cmake_pytest/rosapi_test_stringify_field_types.txt" "--command" "/usr/bin/python3" "-u" "-m" "pytest" "/ros2_ws/src/rosapi/test/test_stringify_field_types.py" "-o" "cache_dir=/ros2_ws/build/rosapi/ament_cmake_pytest/rosapi_test_stringify_field_types/.cache" "--junit-xml=/ros2_ws/build/rosapi/test_results/rosapi/rosapi_test_stringify_field_types.xunit.xml" "--junit-prefix=rosapi")
set_tests_properties(rosapi_test_stringify_field_types PROPERTIES  LABELS "pytest" TIMEOUT "60" WORKING_DIRECTORY "/ros2_ws/build/rosapi" _BACKTRACE_TRIPLES "/opt/ros/foxy/install/share/ament_cmake_test/cmake/ament_add_test.cmake;118;add_test;/opt/ros/foxy/install/share/ament_cmake_pytest/cmake/ament_add_pytest_test.cmake;165;ament_add_test;/ros2_ws/src/rosapi/CMakeLists.txt;26;ament_add_pytest_test;/ros2_ws/src/rosapi/CMakeLists.txt;0;")
