import numpy

import matplotlib.pyplot as plt

# handle event, in event execute procedure
class time_routine:

     
    def __init__(self,tau, h, belta):
        
        # master time and also current time
        self.master_time = 0.0
        
        
        # for new arrival usage
        self.next_arrival_time = 0.0
        self.next_complexity = 0.0
                        
        # three event times change the system
        # new field arrives encoder index = 0, 
        # encode finished/ arrives storage server index = 1,
        # storage process finished/ leave system index =2         
        # create events list table, no matter values are, initial will cover them
        self.events_list = []
          
        # for statistics usage
        # at new_arrival method count new generate field
        self.arrived_field_count = 0
        # record storage server process time in total
        self.storage_server_active_time = 0.0 
        # the final stored frame
        self.frame_stored = 0
          
          
        self.tau = tau
        self.h = h
        self.belta = belta
        
        # ! create system ! 
        self.machine = system(self, self.belta)
        
        
          
    # poisson generator, suppose on another class, but, anyway
    def poisson(self,num):
        # give me poisson
        return numpy.random.exponential(num) 

    # one arrival time will and must schedule next arrival time
    def new_arrival(self):
            
        # next interarrival time
        self.next_arrival_time = self.poisson(self.tau)
        # next complexity
        self.next_complexity = self.poisson(self.h)
        # calculae number of arrival field
        self.arrived_field_count += 1
           
    # update events list   
    def update_events_list(self, event_type, event_time):
        
        self.events_list[event_type] = event_time
           
    def schedule_next_event(self):
        # set clock to the nearest event
        self.master_time = min(self.events_list)
             
        # time  that arrives encoder
        if(self.events_list.index(self.master_time) == 0):
                
            # arrange next arrive
            self.new_arrival()
            
            # calculate next arrival time
            master_arrival_time = self.master_time + self.next_arrival_time
            # update next arrival time
            self.update_events_list(0, master_arrival_time)
            # call encoder procedure
            self.machine.enter_enc_queue(self.next_complexity, self)
            
        # time that encode finish and arrives storage server
        elif(self.events_list.index(self.master_time) == 1): 
                       
            
            # namely, arrange new field go into processor 
            # someone leave the encoder mean someone go in storage server
            # set flag
            self.machine.encoder_busy = False
                        
            # leave encoder, pass to storage server
            self.machine.enter_sotrage_server_queue(self) 
            # field leave means encoder is empty    
            self.machine.encoder_process(self) 
                 
        # time that for storage server frame leaves the system
        else:
                    
            
            self.frame_stored += 1
            
            self.machine.storage_server_busy = False
            # some one leave server, so server will be empty
            self.machine.storage_server_process(self)

#***************************************************************************************************************************************

class system:
    
    def __init__(self, simulation_time_routine, belta):
        self.encoder_queue = []
        self.storage_server_queue = []
        self.tail_is_top = False
        self.encoder_queue_count = 0
        self.dump_counter = 0
        self.encode_complexity = 0.0
        self.encoder_busy = False
        self.storage_server_busy = False
        
        self.belta = belta
               
    # this is an action, is that right?
    # check queue |not full -> append -> change beacon
    #             |full -> check tail |top -> drop tail
    #                                 |bottom -> drop it
    def enter_enc_queue(self, complexity, simulation_time_routine):
    

        # check if queue is full
        if(len(self.encoder_queue) < self.belta):
            # enter encoder queue
            self.encoder_queue.append(complexity)
            self.encoder_queue_count += 1
            
            # convert tail beacon, either way
            if(self.tail_is_top):
                self.tail_is_top = False
                
            else:
                self.tail_is_top = True
            
            # check encoder flag, automatic enter encoder
            if(not self.encoder_busy):
                # call encoder process
                self.encoder_process(simulation_time_routine)   
                 
        # sorry, queue is full        
        else:
            # if tail is top then drop tail
            if(self.tail_is_top):
                
                self.encoder_queue.pop(self.belta - 1)
                # this drop is top field
                self.dump_counter += 1
                
            # this drop is because queue is full
            self.dump_counter += 1
                                          
    # encoder start process             
    def encoder_process(self, simulation_time_routine):
        

        if(len(self.encoder_queue) > 0):
            # set encoder flag busy
            self.encoder_busy = True
            # fetch complexity for encode
            self.encode_complexity = self.encoder_queue.pop(0)
            # give encoder process time 
            encoder_process_time = self.encode_complexity / C_enc
                       

            # calcute the departure time
            master_process_time = simulation_time_routine.master_time + encoder_process_time
            # update event 1, departure encoder time
            simulation_time_routine.update_events_list(1, master_process_time)
        
        # encoder queue is empty, boring encoder has nothing to do    
        else :
            #encoder empty
            self.encoder_busy = False
            simulation_time_routine.update_events_list(1, 90000.0)
            
            
    # enter storage server
    def enter_sotrage_server_queue(self, simulation_time_routine):
    
        

        store_complexity = self.encode_complexity
        # queue empty procedure, after one field leave encoder
        if(len(self.encoder_queue) < 1):
            # if queue is empty, encoder will be idle, set departure time infinity
            simulation_time_routine.update_events_list(1, 90000.0)
        #!!!!    
        # append new field into queue
        self.storage_server_queue.append(store_complexity)
                        
        # this check for whether server is empty, because someone leave, in the case queue has been empty since last one leave
        # it's like the scene in the client when a custom arrived find doctor busy, she fall asleep
        if(not self.storage_server_busy):
            # call storage server process
            self.storage_server_process(simulation_time_routine)
        
      
    # start storage server     
    def storage_server_process(self, simulation_time_routine):
    

        # check atleast two filed waiting
        if(len(self.storage_server_queue) > 1):
        
            self.storage_server_busy = True
            # fetch the top field
            top_complexity = self.storage_server_queue.pop(0)
            # fetch the bottom field
            bottom_complexity = self.storage_server_queue.pop(0)
            
            # queue empty procedure
            if(len(self.storage_server_queue) < 2):
                # if queue have not enough field to process, set departure infinity
                simulation_time_routine.update_events_list(2, 90000.0)
                
            # calculate the complexity of frame
            frame = alpha * (top_complexity + bottom_complexity)
            # calculate  store process time
            storage_server_process_time = frame / C_storage
            
            # calculate server active time
            simulation_time_routine.storage_server_active_time += storage_server_process_time
            # calcute the mater store process time
            master_store_time = simulation_time_routine.master_time + storage_server_process_time
            # update event 2, departure server time
            simulation_time_routine.update_events_list(2, master_store_time)
        
        # storage server has no enough field (0 or 1), empty storage server has nothing to do
        else: 
         
            self.storage_server_busy = False
         
            simulation_time_routine.update_events_list(2, 90000.0)

#***************************************************************************************************************************************

  
class report_generator:

    def __init__(self, simulation_time_routine, machine):
    
        self.report_count = 0
        self.fraction = 0.0
        self.utilization = 0.0
            
    def how_is_going(self, simulation_time_routine, machine):
    
        self.report_count += 1
        
        #os.system('clear')
        
        print('\n')
        
        print ' Report Count: ', self.report_count
        
        print ' tau: ', simulation_time_routine.tau
        
        print ' h: ', simulation_time_routine.h
        
        print ' belta: ', simulation_time_routine.belta
        
        print ('____________report roof_______________\n')
        
        percent = ((simulation_time_routine.master_time / 28800.0) * 100)
        print ' procedure: ', percent, '%'
        
        print ' Current Time: ', simulation_time_routine.master_time /3600 ,'hours'
                       
        print ' New Arrival Count:', simulation_time_routine.arrived_field_count
        
        print ' Number Delayed: ', machine.encoder_queue_count
        
        print ' Dump Count:', machine.dump_counter
        
        self.fraction = ((float(machine.dump_counter) / simulation_time_routine.arrived_field_count) * 100)

        print ' Fraction of Loss: ', self.fraction, '%'
                                                                   
        print ' Storage Server Busy Time:', simulation_time_routine.storage_server_active_time/3600.0, 'hours'
                
        self.utilization = ((simulation_time_routine.storage_server_active_time / simulation_time_routine.master_time) * 100)
        print ' Storage Server Utilization: ', self.utilization, '%'
        
        print ' Frame Store: ', simulation_time_routine.frame_stored
                       
        print ('____________report ground____________\n')
               
        

#***************************************************************************************************************************************


class initial_routine:


    def __init__(self, tau, h, belta):
                    
        self.tau = tau
        self.h = h
        self.belta = belta
        self.simulation_time_routine = time_routine(self.tau, self.h, self.belta)             
        # create class report generator
        self.simulation_report_generator = report_generator(self.simulation_time_routine, self.simulation_time_routine.machine)        
                      
        # initial routine
        self.let_the_show_begin()
                        
    def let_the_show_begin(self):
        # create class time master
        # the important initial method
        # ************************************************************

        # initial all event = infinity
        # event 0
        self.simulation_time_routine.events_list.append(90000.0)
        # event 1
        self.simulation_time_routine.events_list.append(90000.0)
        # event 2
        self.simulation_time_routine.events_list.append(90000.0)
        # first arrival field
        self.simulation_time_routine.new_arrival()
        
        # set time = 0 first arrival event 0
        self.simulation_time_routine.update_events_list(0, 0.0)  
        # ***********************************************************
        
        print('________________Simulation Start_________________')
        
        # simulation_report_generator.how_is_going(simulation_time_routine, simulation_time_routine.machine)
        # start simulation
        # this is the only loop
        while(self.simulation_time_routine.master_time < duration_time ):        
                  
            self.simulation_time_routine.schedule_next_event()
                        
        # final report
        self.simulation_report_generator.how_is_going(self.simulation_time_routine, self.simulation_time_routine.machine)


    def get_simulation_data(self):
        
        # fraction and utilization are calculated in report, so it must be call once
        # get the big four data
        # 0 arrived field
        # 1 fraction
        # 2 utilaization
        # 3 frame stored
        report_array = []
        
        report_array.append(self.simulation_time_routine.arrived_field_count)
        
        report_array.append(self.simulation_report_generator.fraction)
        
        report_array.append(self.simulation_report_generator.utilization)
        
        report_array.append(self.simulation_time_routine.frame_stored)
        
        return report_array

#***************************************************************************************************************************************
# main program

# _______________parameter_______________

# encoder process flow rate 
C_enc = 15800
# storage server flow rate
C_storage = 1600
# field storage convert ratio
alpha = 0.1
# 8 hours = 28800 seconds
duration_time = 28800.0

# different simulation variable 

# Arrival time
# tau = 0.01668335
# 1/59.94 = 0.01668335 ; 1/50 = 0.02

# Field complexity
# h = 262.5
# 262.5 ; 312.5

# Encoder queue length
# belta = 20
# 20 40 60 80 100
# ___________________end_________________________
   
# create class initial_routine
# automatic start
y = []
x = [] 
u = []

for i in range(1,5):
    x.append(i)
    currReport = initial_routine(0.01668335, 262.5, i).get_simulation_data()
    y.append(currReport[1])
    u.append(currReport[2])
    
    

print 'encoder queue length:x[]=', x
print 'fraction lof loss field:y[]=', y
print 'utilization of storage server:u[]=', u


#*************************************************************
# python plot


plt.xlabel('Encoder Queue Length')

plt.ylabel('utilization of storage server')

plt.plot(x, u, 'ro')
plt.show()


#*************************************************************


