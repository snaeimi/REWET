
Future Development
##################

API Development
***************
REWET is planned to be used in in NHERI SimCenter's R2D General Recovery; thus, it must provide APIs to be seamlessly 
get connected to the R2D's planned general recovery module. There are goring to be a module providing API. The following 
APIs are to be developed in the next development cycle:

* init: this API is the conceptual init function to load the inputs and settings required pertaining to the restoration simulation tasks.
* runTillNextTime: Runs the simulation until the next specified time. Returns exception if the time is less or the same time as the current_stop_time.
* runTillNextEvent: Runs until the next events.
* getNextEventTime: Gets the next event time.
* setEventTime: sets an event time.