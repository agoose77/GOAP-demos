"""Basic demo using GOAP library

Ellipsis (...) is used to define an effect which can satisfy any precondition with the same name. This is used to provide a plugin architecture.
The value of that precondition is then used to update the world state when this action is completed.
In this example, the GoTo action receives the actual location from the precondition of GetAxe and CutTrees
"""
from argparse import ArgumentParser
from typing import Optional
from goap.action import Action, ActionStatus, StateType
from goap.planner import Goal, Planner, PlanStatus
from goap.director import Director
from time import time


class GoTo(Action):
    effects = {"at_location": ...}

    def on_enter(self, world_state: StateType, goal_state: StateType):
        query = goal_state["at_location"]
        print("Going to find a {}".format(query))


class GetAxe(Action):
    effects = {"has_axe": True}
    preconditions = {"at_location": "axe"}

    def on_enter(self, world_state: StateType, goal_state: StateType):
        print("Collecting ye olde axe!")


class CutTrees(Action):
    effects = {"has_wood": True}
    preconditions = {"at_location": "forest", "has_axe": True}

    def __init__(self):
        self._start_time: Optional[float] = None

    def on_enter(self, world_state: StateType, goal_state: StateType):
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
    state = {"has_wood": True}


if __name__ == "__main__":
    parser = ArgumentParser(description="Run demo GOAP program")
    parser.add_argument("-graph", type=str)
    args = parser.parse_args()

    world_state = dict(at_location=None, has_axe=False, has_wood=False)

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

    while plan.update() == PlanStatus.running:
        continue

    print("-" * 50)
    print("Final State:", world_state)
