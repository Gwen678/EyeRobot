# CMake generated Testfile for 
# Source directory: /ros2_ws/src/angles/angles
# Build directory: /ros2_ws/build/angles
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(angles_utest "/usr/bin/python3" "-u" "/opt/ros/humble/share/ament_cmake_test/cmake/run_test.py" "/ros2_ws/build/angles/test_results/angles/angles_utest.gtest.xml" "--package-name" "angles" "--output-file" "/ros2_ws/build/angles/ament_cmake_gtest/angles_utest.txt" "--command" "/ros2_ws/build/angles/angles_utest" "--gtest_output=xml:/ros2_ws/build/angles/test_results/angles/angles_utest.gtest.xml")
set_tests_properties(angles_utest PROPERTIES  LABELS "gtest" REQUIRED_FILES "/ros2_ws/build/angles/angles_utest" TIMEOUT "60" WORKING_DIRECTORY "/ros2_ws/build/angles" _BACKTRACE_TRIPLES "/opt/ros/humble/share/ament_cmake_test/cmake/ament_add_test.cmake;125;add_test;/opt/ros/humble/share/ament_cmake_gtest/cmake/ament_add_gtest_test.cmake;86;ament_add_test;/opt/ros/humble/share/ament_cmake_gtest/cmake/ament_add_gtest.cmake;93;ament_add_gtest_test;/ros2_ws/src/angles/angles/CMakeLists.txt;25;ament_add_gtest;/ros2_ws/src/angles/angles/CMakeLists.txt;0;")
add_test(utest "/usr/bin/python3" "-u" "/opt/ros/humble/share/ament_cmake_test/cmake/run_test.py" "/ros2_ws/build/angles/test_results/angles/utest.xunit.xml" "--package-name" "angles" "--output-file" "/ros2_ws/build/angles/ament_cmake_pytest/utest.txt" "--command" "/usr/bin/python3" "-u" "-m" "pytest" "/ros2_ws/src/angles/angles/test/utest.py" "-o" "cache_dir=/ros2_ws/build/angles/ament_cmake_pytest/utest/.cache" "--junit-xml=/ros2_ws/build/angles/test_results/angles/utest.xunit.xml" "--junit-prefix=angles")
set_tests_properties(utest PROPERTIES  LABELS "pytest" TIMEOUT "60" WORKING_DIRECTORY "/ros2_ws/build/angles" _BACKTRACE_TRIPLES "/opt/ros/humble/share/ament_cmake_test/cmake/ament_add_test.cmake;125;add_test;/opt/ros/humble/share/ament_cmake_pytest/cmake/ament_add_pytest_test.cmake;169;ament_add_test;/ros2_ws/src/angles/angles/CMakeLists.txt;33;ament_add_pytest_test;/ros2_ws/src/angles/angles/CMakeLists.txt;0;")
subdirs("gtest")
