from pytest import Item
from werkzeug.utils import import_string, ImportStringError
import logging
import threading
import time
try:
    from Queue import Queue, Empty
except ImportError as e:
    from queue import Queue, Empty

LOG = logging.getLogger(__name__)
COMMUNICATION = Queue()

class TEST_STATUS:
    SUCCESS = 0
    FAILURE = 1
    UNDEFINED = 2
    COMPLETED = 3

class SuccessfulCompletion(Exception):
    pass

class Scenario(object):
    """
    Scenario - a sequence of acts.
    """
    def __init__(self, parent, app_factory, monkeypatch, acts, global_next=None):
        self.acts = []
        self.act_results = {}
        self.current_act = 0
        self.starting_point = None
        self.exit_point     = None
        self.success_criteria = None
        self.parent = parent
        self.global_next = global_next

        self.app_factory = app_factory
        self.monkeypatch = monkeypatch.MonkeyPatch()

        for i, act in enumerate(acts):
            if hasattr(Act, "from_parent"):
                self.add_act(Act.from_parent(self.parent, name="act-{}".format(i),
                                scenario=self, act_info=act, last=(i == len(acts)-1)))
            else:
                self.add_act(Act(name="act-{}".format(i), parent=self.parent, scenario=self, 
                    act_info=act, last=(i==len(acts)-1) ))
    
    def add_act(self, act):
        self.acts.append(act)
        self.act_results[act.name] = TEST_STATUS.UNDEFINED
    
    def next_test(self):
        """
        Label current act as a success and proceed to next test by removing current patches
        and activating next act.
        """
        self.act_results[self.acts[self.current_act].name] = TEST_STATUS.SUCCESS
        self.monkeypatch.undo()
        self.current_act += 1
        if self.current_act == len(self.acts):
            return TEST_STATUS.COMPLETED
        self.acts[self.current_act].activate(self.monkeypatch)

    def runtest(self, act_name):
        """
        Gets called by the called tests.
        When the first test gets called - the whole test gets run. 
        For the other ones - just check the stored values to pass/fail - so the user can tell exactly which 
        test had failed.
        
        To run the test - activate mocks of the first act.
        Run the application in new thread.
        Mocked values will communicate to queue if they have succeeded or not.
        New mocks happen automatically in different thread. We can just read the results.
        """
        if self.current_act > 0:
            return self.act_results[act_name]

        self.acts[0].activate(self.monkeypatch)
        exit_cond = False
        thread = threading.Thread(target=self.app_factory())
        # thread.daemon = True
        thread.start()
        while not COMMUNICATION.empty() or (thread.isAlive() and not exit_cond):
            try:
                comm = COMMUNICATION.get(block=True, timeout=3)
            except Empty:
                continue
            exit_cond = False
            if comm["COMMAND"] == "NEXT":
                res = self.next_test()
                if res and res == TEST_STATUS.COMPLETED:
                    exit_cond = True
                    continue
                comm = COMMUNICATION.get(block=True, timeout=3)
            elif comm["COMMAND"] == "RAISED":
                self.acts[self.current_act].history[comm["ORIGIN"]] = True
            
        if not exit_cond:
            self.act_results[self.current_act] = TEST_STATUS.FAILURE
        
        assert not thread.isAlive()
        return self.act_results[act_name]


class Act(Item):
    """
    Act - tests before next act.

    exit_point - function that tells Scenario to switch to the next Act
    actors - list of points to mock
    """
    def __init__(self, name=None, parent=None, scenario=None, act_info=None, last=False):
        super(Act, self).__init__(name, parent)
        self.history = {}
        self.name = name
        self.scenario = scenario
        self.entry_point = None
        self.exit_point = None
        self.last = last
        self.next_point = self.parse_next_point(act_info) or scenario.global_next
        assert self.next_point, "Without global next-point, there needs to be one defined per scenario."
        self.add_next_point(act_info, self.next_point)

        self.actors = self.parse_actors(self, act_info, self.last)
    
    @staticmethod
    def add_next_point(data, next_point):
        if not data.get('next-point'):
            data['next-point'] = next_point

    @staticmethod
    def parse_next_point(data):
        return data.get("next-point")

    @staticmethod
    def parse_actors(act, data, last_act):
        actors = []
        for actor in data:
            LOG.debug(actor)
            if actor == 'next-point':
                if not last_act:
                    actors.append(NextActor(act, actor, data[actor]))
                else:
                    actors.append(LastActor(act, actor, data[actor]))
            else:
                actors.append(Actor(act, actor, data[actor]))
        return actors

    def activate(self, monkeypatch):
        for actor in self.actors:
            self.history[actor.source.__name__] = False
            actor.activate(monkeypatch)
    
    def runtest(self):
        current_act_success = self.scenario.runtest(self.name)
        if current_act_success == TEST_STATUS.SUCCESS:
            assert True
        elif current_act_success == TEST_STATUS.UNDEFINED:
            assert False, "Test wasn't reached due to previously failed test."
        elif current_act_success == TEST_STATUS.FAILURE:
            assert False, "Act was not completed."

class BaseActor(object):
    def __init__(self, act):
        self.act = act
    
    def activate(self, monkeypatch):
        raise NotImplementedError("To be a proper actor you need to activate monkeypatches")

class Actor(BaseActor):
    """
    Actor is an element - a class or a function involved in an Act.
    There are functions or classes that get monkeypatched to run the test.
    """

    ACTOR_EXEC = 'exc'

    def __init__(self, act, source, sub):
        super(Actor, self).__init__(act)

        path = source.strip().split(".")
        assert len(path)>1, "Provide attribute to monkeypatch"
        assert len(sub) == 1, "Only 1 substitution per act available for the same method"
        sub = sub[0]

        self.source = import_string(".".join(path[:-1]))
        self.source_attr = path[-1]
        try:
            self.sub = import_string(sub.get(self.ACTOR_EXEC).split(',')[0].strip())
        except ImportStringError as e:
            import sys
            if sys.version_info.major < 3:
                import __builtin__ as builtins
            else:
                import builtins
            attempt = getattr(builtins, sub.get(
                self.ACTOR_EXEC).split(',')[0].strip())
            if not attempt:
                raise e
            self.sub = attempt
        extra_msg = sub.get(self.ACTOR_EXEC).split(',')[1:]
        if len(extra_msg) == 0:
            self.sub_message = ["Actor raises an error {}".format(sub.get(self.ACTOR_EXEC).split(',')[0])]
        else:
            self.sub_message = extra_msg
    
    def activate(self, monkeypatch):
        monkeypatch.setattr(self.source, self.source_attr, raise_factory(self.sub, self.sub_message))


class NextActor(BaseActor):
    ACTOR_EXEC = 'exc'

    def __init__(self, act, source, sub):
        super(NextActor, self).__init__(act)
        assert source == "next-point", "Next Actor erroneously initialized."

        source = sub
        if isinstance(sub, dict):
            source = sub.get(self.ACTOR_EXEC)
        path = source.strip().split(".")

        self.original_method = import_string(source)
        self.source = import_string(".".join(path[:-1]))
        self.source_attr = path[-1]


    def activate(self, monkeypatch):
        monkeypatch.setattr(self.source, self.source_attr, next_factory(self.original_method, self.act))


class LastActor(NextActor):
    """
    Last NextActor that submits next and exits the application.
    """
    def activate(self, monkeypatch):
        monkeypatch.setattr(self.source, self.source_attr, last_factory(self.act))


def raise_factory(exc, message):
    def raise_exception(*args, **kwargs):
        COMMUNICATION.put(
            {
                "COMMAND": "RAISED",
                "ORIGIN": exc.__name__
            }
        )
        raise exc(*message)
    return raise_exception

def exit_factory():
    raise SuccessfulCompletion("Completed the whole method")

def next_factory(next_method, act):
    def next_act(*args, **kwargs):
        COMMUNICATION.put(
            {
                "COMMAND": "NEXT",
                "ACT": act.name
            }
        )
        # This way Queue won't become empty until next-processed gets 
        COMMUNICATION.put(
            {
                "COMMAND": "NEXT-PROCESSED",
                "ACT": act.name
            }
        )
        # Wait until next is processed and monkeypatches are adjusted
        while not COMMUNICATION.empty():
            time.sleep(0.5)
        next_method()
    return next_act

def last_factory(act):
    def next_act(*args, **kwargs):
        COMMUNICATION.put(
            {
                "COMMAND": "NEXT",
                "ACT": act.name
            }
        )
        
        import sys
        sys.exit(0)
    return next_act
