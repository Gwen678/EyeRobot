#!/usr/bin/env bash
# ==============================================================================
# EyeRobot Headless Launcher for Docker
# ==============================================================================
set -e

SERIAL_DEV="${1:-/dev/ttyUSB0}"
BAUD=115200

# Sourcing ROS 2 and Workspace
source /opt/ros/humble/setup.bash
source /EyeRobot/install/setup.bash

echo "🚀 Démarrage de l'infrastructure EyeRobot..."

# 1. Démarrer le micro-ROS agent (ESP32) en tâche de fond
echo "🔌 Connexion à l'ESP32 sur $SERIAL_DEV..."
ros2 run micro_ros_agent micro_ros_agent serial --dev "$SERIAL_DEV" -b $BAUD &
AGENT_PID=$!

sleep 2 # Laisser le temps à l'ESP32 de s'initialiser

# 2. Démarrer les publishers d'état et d'odométrie
echo "🤖 Démarrage du modèle 3D et de l'odométrie..."
XACRO_FILE=$(ros2 pkg prefix robot_description)/share/robot_description/urdf/Robot.xacro

ros2 run manual_controller state_estimator --ros-args -p debug_encoders:=false &
ESTIMATOR_PID=$!

ros2 run robot_state_publisher robot_state_publisher \
  --ros-args -p robot_description:="$(xacro "$XACRO_FILE")" &
RSP_PID=$!

ros2 run joint_state_publisher joint_state_publisher &
JSP_PID=$!

# Optionnel : Lancer le pont Foxglove pour pouvoir visualiser sur le PC Windows
# (Si le paquet ros-humble-foxglove-bridge est installé)
if command -v ros2 &> /dev/null && ros2 pkg list | grep -q foxglove_bridge; then
    echo "🦊 Lancement de Foxglove Bridge..."
    ros2 launch foxglove_bridge foxglove_bridge_launch.xml &
    FOX_PID=$!
else
    echo "⚠️ Foxglove Bridge non trouvé, visualisation à distance désactivée."
fi

# ==============================================================================
# Gestion propre de l'arrêt (Ctrl+C)
# ==============================================================================
cleanup() {
    echo ""
    echo "🛑 Arrêt des services..."
    kill $AGENT_PID $ESTIMATOR_PID $RSP_PID $JSP_PID $FOX_PID 2>/dev/null
    wait $AGENT_PID $ESTIMATOR_PID $RSP_PID $JSP_PID $FOX_PID 2>/dev/null
    echo "✅ Robot arrêté proprement."
    exit 0
}

trap cleanup SIGINT SIGTERM

echo ""
echo "==================================================="
echo "✅ Système prêt ! Robot actif en tâche de fond."
echo "   - Connectez-vous via Foxglove Studio (ws://IP:8765)"
echo "   - Ouvrez un AUTRE terminal Docker pour lancer la télécommande (teleop)"
echo "   - Appuyez sur Ctrl+C ici pour tout éteindre."
echo "==================================================="

# Bloquer le script ici et afficher les logs en direct
wait
