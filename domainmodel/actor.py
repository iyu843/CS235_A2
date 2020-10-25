class Actor:
    def __init__(self, actor_full_name: str):
        self.colleague_set = set()
        # defines an attribute
        if actor_full_name == "" or type(actor_full_name) is not str:
            self.__actor_full_name = None
        else:
            self.__actor_full_name = actor_full_name.strip()

    @property
    def actor_full_name(self) -> str:
        return self.__actor_full_name

    def __repr__(self):
        # defines the unique string representation of the object
        return f"<Actor {self.__actor_full_name}>"

    def __eq__(self, other):
        # check for equality of two Actor object instances by comparing the actor_full names
        return self.__actor_full_name == other.__actor_full_name

    def __lt__(self, other):
        # implement a sorting order defined by the name
        return self.__actor_full_name < other.__actor_full_name

    def __hash__(self):
        # defines which attribute is used for computing a hash value as used in set or dictionary keys
        return hash(self.__actor_full_name)

    def add_actor_colleague(self, colleague):
        # if an actor colleague was on the cast for the same movie as this actor,
        # we allow for the colleague to be added to this actor's set of colleagues
        self.colleague_set.add(colleague)

    def check_if_this_actor_worked_with(self, colleague):
        # this method checks if a given colleague Actor has worked with the actor at least once in the same movie
        return colleague in self.colleague_set
