#!/bin/bash

echo "--- Nettoyage des anciens processus ---"
pkill -f foxglove_bridge
pkill -f sllidar_node
pkill -f map_server
pkill -f amcl
pkill -f lifecycle_manager
sleep 2

echo "--- Démarrage de la localisation ---"

# 1. Transformations statiques
ros2 run tf2_ros static_transform_publisher 0 0 0.15 0 0 0 base_link laser &

# 2. Lidar (Si le port USB est déjà utilisé, il échouera, donc on fait un petit break)
ros2 launch sllidar_ros2 sllidar_a1_launch.py serial_port:=/dev/ttyUSB0 &
sleep 5 

# 3. Foxglove
ros2 run foxglove_bridge foxglove_bridge &

# 4. Map Server (On utilise des guillemets pour éviter l'erreur de parsing)
ros2 run nav2_map_server map_server --ros-args -r __node:=map_server -p yaml_filename:=/home/eyerobot/CleanTest/EyeRobot/vision/maps/map.yaml &

# 5. AMCL
ros2 run nav2_amcl amcl --ros-args -r __node:=amcl -p scan_topic:=/scan -p map_topic:=/map &

# 6. Lifecycle Manager (Syntaxe corrigée avec guillemets autour de la liste)
ros2 run nav2_lifecycle_manager lifecycle_manager --ros-args -p node_names:="['map_server', 'amcl']" -p autostart:=true &

echo "--- Système lancé. Vérifie Foxglove ! ---"
