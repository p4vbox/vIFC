class Context():

    # A list to store every context.
    contexts = []

    class ContextData():
        def __init__(self, id_key):
            self.id_key = id_key
            self.authenticated = False

    # Returns the contexts list.
    @classmethod
    def getContextList(self):
        return self.contexts

    # Returns the context associated with the peer identity key.
    @classmethod
    def getContext(self, id_key):
        for context in self.contexts:
            if context.id_key == id_key:
                return context

        print "\nContext associated with identity key {} not found!".format(id_key)
        return

    # Creates and appends a context.    
    @classmethod
    def createContext(self, id_key):
        self.contexts.append(self.ContextData(id_key))
        return

    # Deletes a context, if it exists in the list.
    @classmethod
    def deleteContext(self, id_key):
        index = 0
        for context in self.contexts:
            if context.id_key == id_key:
                del self.contexts[index]
                return
            index += 1

        print "\nContext associated with identity key {} not found!".format(id_key)
        return

    # Deletes every context in the list.
    @classmethod
    def purgeContexts(self):
        # Verifies if the list isn't empty.
        if not self.contexts:
            print "\nThere are no contexts in the list!"
        else:
            self.contexts.clear()
        return

    # Returns the authentication status of a client.
    @classmethod
    def isAuthenticated(self, id_key):
        for context in self.contexts:
            if context.id_key == id_key:
                return context.authenticated

        print "\nContext associated with identity key {} not found!".format(id_key)
        return

    # Changes the state of the authentication.
    @classmethod
    def authenticate(self, id_key):
        for context in self.contexts:
            if context.id_key == id_key:
                context.authenticated = True
                return

        print "\nContext associated with identity key {} not found!".format(id_key)
        return