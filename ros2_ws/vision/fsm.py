import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import Point, PoseStamped
from std_msgs.msg import String # Pour un éventuel topic de contrôle de pince

class EyeRobotFSM(Node):
    def __init__(self):
        super().__init__('eyerobot_fsm_node')

        # === Définition des États ===
        # États : SEARCH_1, PICK_UP_1, SEARCH_2, PICK_UP_2, GO_TO_DUMP, DUMP, RETURN_HOME, IDLE
        self.state = "SEARCH_1"
        self.get_logger().info("--- Machine à États Initialisée. État: SEARCH_1 ---")

        # === Mémoire du Robot ===
        self.lego_count = 0
        self.lego_1_pose = None # PointStamped
        self.lego_2_pose = None # PointStamped

        # === Coordonnées Fixes (à adapter à ta carte !) ===
        self.dump_pose = self.create_pose(-1.0, 2.0) # Zone de dépôt
        self.home_pose = self.create_pose(0.0, 0.0) # Zone de départ

        # === Action Client pour Nav2 ===
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        # === Abonnement aux Legos (Coordonnées déjà dans 'map' !) ===
        # Ce topic doit être publié par ta caméra/transform après calcul
        self.create_subscription(Point, '/eyerobot/vision/lego_markers_map', self.lego_callback, 10)

        # === Timer pour surveiller la FSM (boucle de contrôle) ===
        timer_period = 0.5 # Vérifier toutes les demi-secondes
        self.timer = self.create_timer(timer_period, self.fsm_loop)

    def create_pose(self, x, y):
        """Helper pour créer rapidement une PoseStamped simple"""
        pose = PoseStamped()
        pose.header.frame_id = "map"
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.orientation.w = 1.0 # Orientation face à la carte
        return pose

    # === Callbacks ===
    def lego_callback(self, point_msg):
        """Reçoit les coordonnées géographiques d'un Lego détecté"""
        if self.state == "SEARCH_1":
            self.lego_1_pose = self.create_pose(point_msg.x, point_msg.y)
            self.state = "PICK_UP_1"
            self.get_logger().info(">>> Lego 1 repéré ! Coordonnées mémorisées.")
        
        elif self.state == "SEARCH_2":
            self.lego_2_pose = self.create_pose(point_msg.x, point_msg.y)
            self.state = "PICK_UP_2"
            self.get_logger().info(">>> Lego 2 repéré ! Coordonnées mémorisées.")

    def fsm_loop(self):
        """Boucle principale de la Machine à États (vérifie l'avancement)"""
        if self.state == "IDLE":
            pass # Mission terminée

        elif self.state == "PICK_UP_1":
            # On envoie le goal une seule fois
            if self.send_goal(self.lego_1_pose):
                self.state = "WAITING_FOR_ARRIVAL"
                self.next_state_after_arrival = "SEARCH_2"
                self.lego_count = 1

        elif self.state == "PICK_UP_2":
            if self.send_goal(self.lego_2_pose):
                self.state = "WAITING_FOR_ARRIVAL"
                self.next_state_after_arrival = "GO_TO_DUMP"
                self.lego_count = 2

        elif self.state == "GO_TO_DUMP":
            if self.send_goal(self.dump_pose):
                self.state = "WAITING_FOR_ARRIVAL"
                self.next_state_after_arrival = "DUMP"

        elif self.state == "DUMP":
            self.get_logger().info("Action: Vidage des blocs (simulation)...")
            # Ici : Action client vers ta pince/bennant
            rclpy.spin_once(self, timeout_sec=2.0) # Simuler 2s de vidage
            self.lego_count = 0
            self.lego_1_pose = None
            self.lego_2_pose = None
            self.state = "RETURN_HOME"

        elif self.state == "RETURN_HOME":
            if self.send_goal(self.home_pose):
                self.state = "WAITING_FOR_ARRIVAL"
                self.next_state_after_arrival = "IDLE"

        elif self.state == "WAITING_FOR_ARRIVAL":
            # Cet état est passif, il attend que self.nav_goal_handle arrive à destination
            pass

    # === Interaction avec Nav2 Action Client ===
    def send_goal(self, pose):
        """Envoie un point de navigation à Nav2"""
        self.get_logger().info(f"Envoi du Goal de navigation : x={pose.pose.position.x}, y={pose.pose.position.y}")
        self.nav_client.wait_for_server()
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = pose
        self.send_goal_future = self.nav_client.send_goal_async(goal_msg, feedback_callback=self.feedback_callback)
        self.send_goal_future.add_done_callback(self.goal_response_callback)
        return True # Goal envoyé avec succès (pas forcément accepté)

    def feedback_callback(self, feedback_msg):
        # facultatif : on pourrait afficher la distance restante
        pass

    def goal_response_callback(self, future):
        """Callback appelé quand Nav2 accepte ou refuse le goal"""
        self.nav_goal_handle = future.result()
        if not self.nav_goal_handle.accepted:
            self.get_logger().warn("Goal Refusé par Nav2 !")
            self.state = "SEARCH_1" # Ou un état d'erreur
            return
        self.get_logger().info("Goal Accepté par Nav2. Déplacement en cours...")
        self.nav_goal_handle.get_result_async().add_done_callback(self.goal_result_callback)

    def goal_result_callback(self, future):
        """Callback appelé quand Nav2 ARRIVE (ou échoue) à destination"""
        result = future.result()
        if result.status == 4: # Status 4 = SUCCEEDED
            self.get_logger().info(">>> Arrivé à destination !")
            self.state = self.next_state_after_arrival
        else:
            self.get_logger().error(f"Navigation échouée (Status: {result.status})")
            self.state = "SEARCH_1" # Retour à zéro par sécurité

def main(args=None):
    rclpy.init(args=args)
    node = EyeRobotFSM()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
