#!/usr/bin/env python3
import rclpy
import py_trees
import py_trees_ros
from py_trees.common import Status

# =========================================================
# COMPORTEMENTS DE LA MISSION (Inchangés)
# =========================================================
class GoToButton(py_trees.behaviour.Behaviour):
    def __init__(self, name="Go_To_Button"):
        super().__init__(name)
        self.target_reached = False
    def update(self):
        if self.target_reached:
            return Status.SUCCESS
        return Status.RUNNING

class PushButton(py_trees.behaviour.Behaviour):
    def __init__(self, name="Push_Button"):
        super().__init__(name)
        self.button_pushed = False
    def update(self):
        if self.button_pushed:
            return Status.SUCCESS
        return Status.RUNNING

class AlignWithWall(py_trees.behaviour.Behaviour):
    def __init__(self, name="Align_With_Wall"):
        super().__init__(name)
        self.is_aligned = False
    def update(self):
        if self.is_aligned:
            return Status.SUCCESS
        return Status.RUNNING

class ClimbDoor(py_trees.behaviour.Behaviour):
    def __init__(self, name="Climb_Door"):
        super().__init__(name)
        self.door_passed = False
    def update(self):
        if self.door_passed:
            return Status.SUCCESS
        return Status.RUNNING
    
class FindDuplo(py_trees.behaviour.Behaviour):
    def __init__(self, name="Find_Duplo"):
        super().__init__(name)
        self.duplo_found = False
    def update(self):
        if self.duplo_found:
            return Status.SUCCESS
        return Status.RUNNING

class EatDuplo(py_trees.behaviour.Behaviour):
    def __init__(self, name="Eat_Duplo"):
        super().__init__(name)
        self.duplo_eaten = False
    def update(self):
        if self.duplo_eaten:
            return Status.SUCCESS
        return Status.RUNNING

class GoToStart(py_trees.behaviour.Behaviour):
    def __init__(self, name="Go_To_Start"):
        super().__init__(name)
        self.at_start_zone = False
    def update(self):
        if self.at_start_zone:
            return Status.SUCCESS
        return Status.RUNNING

class Delivery(py_trees.behaviour.Behaviour):
    def __init__(self, name="Delivery"):
        super().__init__(name)
        self.delivered = False
    def update(self):
        if self.delivered:
            return Status.SUCCESS
        return Status.RUNNING


# =========================================================
# UTILITAIRE : Envelopper une action avec un Timeout tolérant
# =========================================================
def wrap_with_timeout(behaviour_node, duration_seconds):
    """ Enveloppe un nœud avec un timeout. 
    Si le temps expire, le nœud passe quand même à la suite (FailureIsSuccess).
    """
    # 1. On applique le garde-fou temporel
    timeout_node = py_trees.decorators.Timeout(
        child=behaviour_node,
        duration=duration_seconds,
        name=f"{behaviour_node.name}_Timeout"
    )
    
    # 2. Si le timeout expire (renvoie FAILURE), on transforme cet échec en SUCCESS
    # pour que la séquence parente passe à l'étape suivante.
    lenient_node = py_trees.decorators.FailureIsSuccess(
        child=timeout_node,
        name=f"{behaviour_node.name}_Skppable"
    )
    
    return lenient_node


# =========================================================
# CONSTRUCTION DE L'ARBRE (Avec durées configurables)
# =========================================================
def create_tree():
    root = py_trees.composites.Sequence(name="Mission_Principale", memory=True)
    
    # Définition de vos étapes avec leurs durées maximales respectives (en secondes)
    # Vous pouvez ajuster précisément chaque valeur ici.
    steps_with_timeouts = [
        (GoToButton(), 45.0),      # Max 45s pour atteindre le bouton
        (PushButton(), 15.0),      # Max 15s pour appuyer
        (AlignWithWall(), 30.0),    # Max 30s pour s'aligner au mur
        (ClimbDoor(), 20.0),       # Max 20s pour franchir la porte
        (GoToStart(), 60.0),       # Max x min pour aller à la zone de départ
        (Delivery(), 20.0)        # 
    ]
    
    # On applique dynamiquement les décorateurs à chaque action avant de l'ajouter à la séquence
    for action_node, duration in steps_with_timeouts:
        root.add_child(wrap_with_timeout(action_node, duration))
        
    return root


# =========================================================
# NŒUD ROS 2 PRINCIPAL
# =========================================================
def main(args=None):
    rclpy.init(args=args)
    
    tree = py_trees_ros.trees.BehaviourTree(
        root=create_tree(),
        unicode_tree_debug=True
    )

    tree.setup(node_name="autonomous_controller", timeout=15.0)
    
    try:
        tree.tick_tock(period_ms=50)
        rclpy.spin(tree.node)
    except KeyboardInterrupt:
        tree.node.get_logger().info('Arrêt du contrôleur.')
    finally:
        tree.shutdown()
        rclpy.shutdown()

if __name__ == '__main__':
    main()