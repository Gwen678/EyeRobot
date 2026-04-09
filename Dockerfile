FROM dustynv/ros:foxy-desktop-l4t-r32.7.1

RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg 
# 1. On installe juste ce qui est facile et rapide
RUN apt-get update && apt-get install -y libusb-1.0-0-dev python3-pip && \
    pip3 install depthai opencv-python
FROM dustynv/ros:foxy-desktop-l4t-r32.7.1

# 1. Install Python dependencies
RUN pip3 install pymongo tornado depthai
# 2. On prépare le workspace (SANS le dossier depthai-ros en C++)
WORKDIR /ros2_ws
COPY ./src ./src

# 3. On build le reste (LiDAR, Rosbridge, etc.)
SHELL ["/bin/bash", "-c"]
RUN source /opt/ros/foxy/install/setup.bash && colcon build --symlink-install

RUN echo "source /opt/ros/foxy/install/setup.bash" >> ~/.bashrc && \
    echo "source /ros2_ws/install/setup.bash" >> ~/.bashrc

CMD ["bash"]
