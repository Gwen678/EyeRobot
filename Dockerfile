FROM dustynv/ros:foxy-desktop-l4t-r32.7.1

# Installation des dépendances Python pour Rosbridge
RUN pip3 install pymongo tornado

# Création du workspace
WORKDIR /ros2_ws
COPY ./src ./src

# Compilation du projet
RUN . /opt/ros/foxy/setup.sh && colcon build --symlink-install

# Commande par défaut au lancement
CMD ["bash"]
