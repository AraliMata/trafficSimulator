# Model design
import agentpy as ap
import random
import numpy as np

#Simulation time
from datetime import datetime
import time

#Agent definition
class Vehicle(ap.Agent):
    #Necesitamos
    #Tamaño de la imagen del vehículo en Unity 

    def setup(self):
        """ Initiate agent attributes. """
        self.velocity = [1, 0]
        self.stoppingGap = 2
        self.distanceFront = 2
        self.end = False
        self.trafficLightPassed = False
        self.isStopped = False
    
    def setup_pos(self, space):
        self.space = space
        self.pos = space.positions[self]

        if list(self.pos) == [0, 15]:
          self.road = 1
        elif list(self.pos) == [50, 35]:
          self.road = 2
        elif list(self.pos) == [15, 50]:
          self.road = 3
        elif list(self.pos) == [35, 0]:
          self.road = 4

        #self.road = road

    def update_velocity(self, trafficLight, sameRoadVehicles):
        tLpos = trafficLight.pos
        tLState = trafficLight.state

      
        velocities = [[1, 0], [-1, 0], [0, -1], [0, 1]]
        finalPos = [[50, 15], [0, 35], [15, 0], [35, 50]]
        
        if(list(self.pos) == finalPos[self.road-1]):
           self.end = True
           trafficLight.remove_vehicle()

        elif(not self.trafficLightPassed):
          idx = sameRoadVehicles.index(self)
          needsStop = False

          if(idx != 0):
            frontVehicle = sameRoadVehicles[idx - 1]
            diffFront = [frontVehicle.pos[0] - self.pos[0], self.pos[0] - frontVehicle.pos[0], self.pos[1] - frontVehicle.pos[1], frontVehicle.pos[1] - self.pos[1]]
            needsStop = True if diffFront[self.road - 1] <= self.distanceFront else False 

          difference = [tLpos[0] - self.pos[0], self.pos[0] - tLpos[0], self.pos[1] - tLpos[1], tLpos[1] - self.pos[1]]
            
          inTrafficLight = True if difference[self.road - 1] <= self.stoppingGap and difference[self.road - 1] > 0 else False 

          if difference[self.road - 1] < 0:
            self.trafficLightPassed = True

          if (tLState == 0 or tLState == 2) and (inTrafficLight or needsStop):
            self.velocity = [0, 0]
          else:
            self.velocity = velocities[self.road - 1] 

        else: # tLState == 0 para que aunque esté en rojo el semáforo, pueda avanzar en la dirección correcta si aún no se acerca
            self.velocity = velocities[self.road - 1] 
          
          

    def update_position(self): #Moving the agent to a new adjacent space
        """ Move to a new adjacent spot to clean it"""
        self.space.move_by(self, self.velocity)
        self.pos = self.space.positions[self]
    

        


#Cell agent
class TrafficLight(ap.Agent):

    def setup(self, default_state = 1):
        """ Initiate agent attributes. """  
        self.state = 0  #Rojo 0, Verde 1, Amarillo 2
        self.numberVehicles = 0
        self.stateTime = 50 #Hardcoded para visualizar que funciona el cambio de señal en semáforo
        self.waitingTime = 0
        self.priority = 0
        #Tiempo de espera
        #Densidad de autos
    
    def setup_state(self, state):
      self.state = state
   
    def setup_pos(self, space):
        self.space = space
        self.pos = space.positions[self]

    def add_vehicle(self):
        self.numberVehicles += 1

    def remove_vehicle(self):
        self.numberVehicles -= 1

    def update_signal(self, newSignal):
      self.state = newSignal
    
      if self.state == 0:
        self.waitingTime += 1
      elif self.state == 1:
        self.waitingTime = 0
      
      """if self.stateTime == 0:
        self.state = 0 if self.state == 1 else 1
        self.waitingTime = 0 if self.state == 1 else self.waitingTime
        self.stateTime = 13 # Se reinicia el ciclo"""
    
    def compute_priority(self):
      self.priority = 0.8 * self.numberVehicles + 0.2 * self.waitingTime






#Model definition
class ControlModel(ap.Model):

    def setup(self):
        # Parameters
        self.vehiclesNumber = self.p.vehiclesNumber
        self.trafficLightsNumber =  self.p.trafficLightsNumber
        
        self.initialTime = datetime.now()

        # Izquierda a derecha horizontal, derecha a izquierda  horizontal ,  Arriba a abajo vertical, Abajo a arriba vertical
        self.initPos= [[0,15], [50, 35], [15, 50], [35, 0]] 

        trafficLightsPositions = [[14.5,15.0], [35.5, 35], [35, 35.5], [15, 15.5]]

        # Create space and add agents in it
        self.space = ap.Space(self, shape=[self.p.size]*self.p.ndim)

        self.vehicles = ap.AgentList(self, self.vehiclesNumber, Vehicle)

        self.trafficLights = ap.AgentList(self, self.trafficLightsNumber, TrafficLight)

        self.space.add_agents(self.vehicles, self.initPos)
        self.space.add_agents(self.trafficLights, trafficLightsPositions)

        self.vehicles.setup_pos(self.space)
        self.trafficLights.setup_pos(self.space)

      
    def add_vehicle(self, roadNumber):
      newVehicle = ap.AgentList(self, 1, Vehicle)
      self.vehicles.append(newVehicle[0])
      self.space.add_agents([self.vehicles[-1]], [self.initPos[roadNumber - 1]])
      self.vehicles[-1].setup_pos(self.space)
      
   #No agregar vehiculos si hay carros en la posición donde se quiere agregar          

    def step(self):
        #Si se elimino el carro ya no puede estar en el json
        self.idRemovedVehicles = []
        
        self.trafficLights.compute_priority()
        
        maxPriority = 0
        maxIdx = 0
        for i in range(len(self.trafficLights)):
          if self.trafficLights[i].priority > maxPriority:
            maxPriority = self.trafficLights[i].priority
            maxIdx = i
        
        for i in range(len(self.trafficLights)):
          if(i == maxIdx):
            self.trafficLights[i].update_signal(1)
          else:
            self.trafficLights[i].update_signal(0)


        beforeTL1 = self.vehicles.select(self.vehicles.trafficLightPassed == False and self.vehicles.road == 1)
        beforeTL2 = self.vehicles.select(self.vehicles.trafficLightPassed == False and self.vehicles.road == 2)
        beforeTL3 = self.vehicles.select(self.vehicles.trafficLightPassed == False and self.vehicles.road == 3)
        beforeTL4 = self.vehicles.select(self.vehicles.trafficLightPassed == False and self.vehicles.road == 4)

        self.vehicles.select(self.vehicles.road == 1).update_velocity(self.trafficLights[0], beforeTL1)
        self.vehicles.select(self.vehicles.road == 2).update_velocity(self.trafficLights[1], beforeTL2)
        self.vehicles.select(self.vehicles.road == 3).update_velocity(self.trafficLights[2], beforeTL3)
        self.vehicles.select(self.vehicles.road == 4).update_velocity(self.trafficLights[3], beforeTL4)

        self.space.remove_agents(self.vehicles.select(self.vehicles.end))
        
        for agent in self.vehicles.select(self.vehicles.end):
          self.idRemovedVehicles.append(str(agent.id)) 
          self.vehicles.remove(agent)
        
        self.vehicles.update_position()

        #Agregar agentes aleatoriamente en caminos aleatorio
        add = random.randint(0, 20)
        if(add == 1):
          rndRoad = random.randint(1, 4)
          self.add_vehicle(rndRoad)
          self.trafficLights[rndRoad-1].add_vehicle()

        
    def formatJSON(self):
      count = 0
      stringJSON = '{ "TrafficLights":['
      for trafficLight in self.trafficLights:
        stringJSON += '{ "TrafficLightsId":' + str(trafficLight.id) + ', "State":' + str(trafficLight.state) + ', "Position":{"x":' + str(trafficLight.pos[0])+', "y": 0, "z":'+ str(trafficLight.pos[1])+ '}}'
        if count < len(self.trafficLights)-1:
          stringJSON += ","
        count += 1
      stringJSON += '], "Cars":['
      count = 0
      for vehicle in self.vehicles:
        stringJSON += '{ "CarId":' + str(vehicle.id) + ',"Position":{"x":'+str(vehicle.pos[0])+', "y": 0, "z":'+str(vehicle.pos[1])+ '}}'
        if count < len(self.vehicles)-1:
          stringJSON += ","
        count += 1
      
      stringJSON += '], "DeletedCars": [' + ','.join(self.idRemovedVehicles) + ']}'
      return stringJSON



    """def end(self):
        # Print results of simulation
        print("\nNumber of total movements done by agents: ", self.t * self.robotsNumber, " -> (", self.t," each)")
        print("\nTotal simulation time:", datetime.now() - self.initialTime)"""

#Parameters
#Size of grid
m = 5
n = 5       

parameters = {
    'm': m,
    'n': n,
    'ndim': 2,
    'size': 50,
    'vehiclesNumber': 4,
    'trafficLightsNumber': 4,
    'maxExecutionTime': 10,
    'k': 25,
    'initialDirtyPercentage': 0.3,
    'steps': 200, 
}

model = ControlModel(parameters)


