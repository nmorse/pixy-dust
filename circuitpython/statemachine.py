import asyncio

queue = []  
# add an element to the queue
def enqueue(item):
    global queue
    queue.append(item)
    # print("enqueue", item)
  
# remove an element from the queue
def dequeue():
    global queue
    if len(queue) > 0:
        item = queue.pop(0)
        print("dequeue", item)
        return item
    return None

def getEdge(transishes, msg):
    if msg in transishes:
        return transishes[msg]
    return None

def getNode(states, id):
    if id in states:
        return states[id]
    return None

async def state_change(state_machine):
    state_name = "first"
    state = getNode(state_machine["states"], state_name)
    print("state_change", state)
    state["enter"](state)
    while True and state != None:
        msg = dequeue()
        # print("dequeue", msg)
        if msg != None:
            t = getEdge(state_machine["transi"][state_name], msg)
            print("transition", t)
            if t != None:
                last_state_name = state_name
                if (t["to"] != state_name) and "exit" in state:
                    state["exit"](state)
                state_name = t["to"]
                state = getNode(state_machine["states"], state_name)
                if (last_state_name != state_name) and "enter" in state:
                    state["enter"](state)
                if (last_state_name == state_name) and "reenter" in state:
                    state["reenter"](state)
                
        await asyncio.sleep(0)
    print("Error: No state '", state_name, "' found")
