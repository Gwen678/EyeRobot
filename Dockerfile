FROM dustynv/ros:foxy-desktop-l4t-r32.7.1

# 1. Install Python dependencies
RUN pip3 install pymongo tornado

# 2. Setup workspace
WORKDIR /ros2_ws
COPY ./src ./src

# 3. Build (Using the absolute path to the setup file)
# We use SHELL to ensure everything following runs in bash
SHELL ["/bin/bash", "-c"]
RUN source /opt/ros/foxy/install/setup.bash && colcon build --symlink-install

# 4. Automate sourcing for the user
RUN echo "source /opt/ros/foxy/install/setup.bash" >> ~/.bashrc && \
    echo "source /ros2_ws/install/setup.bash" >> ~/.bashrc

CMD ["bash"]
