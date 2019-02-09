"""Advanced demo using GOAP library

Ellipsis (...) is used to define an effect which can satisfy any precondition with the same name. This is used to provide a plugin architecture.
The value of the precondition is then used to update the world state when this action is completed.
In this example, the GoTo action receives the actual location from the precondition of GetAxe and CutTrees

reference("") is used to reference the resolved value of an ellipsis effect to a precondition. This permits symbolic
preconditions to be modified during planning.
In this example, the GoTo action exposes its dynamically received 'at_location' effect value to a precondition,
which in this demo is just a simple logger.
"""

import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from argparse import ArgumentParser
from goap.action import Action, reference, ActionStatus
from goap.planner import Goal, Planner, PlanStatus
from goap.director import Director
from time import time


class GoTo(Action):
    effects = {"at_location": ...}
    preconditions = {"seen_by_blackbird": reference("at_location")}

    def on_enter(self, world_state, goal_state):
        query = goal_state["at_location"]
        print("Going to find a {}".format(query))


class NosyBlackbird(Action):
    effects = {"seen_by_blackbird": ...}

    def on_enter(self, world_state, goal_state):
        query = goal_state["seen_by_blackbird"]
        print("A blackbird spotted me looking for a {}...".format(query))


class GetAxe(Action):
    effects = {"has_axe": True}
    preconditions = {"at_location": "axe"}

    def on_enter(self, world_state, goal_state):
        print("Collecting ye olde axe!")


class CutTrees(Action):
    effects = {"has_wood": True}
    preconditions = {"at_location": "forest", "has_axe": True}

    def __init__(self):
        self._start_time = None

    def on_enter(self, world_state, goal_state):
        print("Cutting trees for days!")
        self._start_time = time()

    def get_status(self, world_state, goal_state):
        elapsed = time() - self._start_time

        if elapsed < 2:
            return ActionStatus.running

        return ActionStatus.success

    def on_exit(self, world_state, goal_state):
        print("I has wood!")


class CutTreesGoal(Goal):
    priority = 1.0

    state = {"has_wood": True}


if __name__ == "__main__":
    parser = ArgumentParser(description="Run demo GOAP program")
    parser.add_argument("-graph", type=str)
    args = parser.parse_args()

    world_state = dict(at_location=None, has_axe=False, has_wood=False, seen_by_blackbird=None)

    actions = [a() for a in Action.__subclasses__()]
    goals = [g() for g in Goal.__subclasses__()]

    planner = Planner(actions, world_state)
    director = Director(planner, world_state, goals)

    plan = director.find_best_plan()
    print("Initial State:", world_state)
    print("Plan:", plan)
    print("----Running Plan" + "-" * 34)

    if args.graph:
        from goap.visualise import visualise_plan

        visualise_plan(plan, args.graph)

    while True:
        status = plan.update()
        if status != PlanStatus.running:
            break

    print("-" * 50)
    print("Final State:", world_state)
